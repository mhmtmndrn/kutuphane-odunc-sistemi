"""Circulation service tests (G11, G12) and the ``Loan`` model's database
constraints (G10, KL-39; data-design §2.4, §4).
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, connection, transaction

from accounts.models import Role, StaffUser
from administration import clock
from administration.errors import RuleViolation
from administration.models import ClosedDate, LibrarySettings, WeeklyClosedDay
from administration.services import update_settings
from billing import services as billing
from billing.models import EntryKind, LedgerEntry
from catalog.models import Copy, CopyStatus
from circulation import services
from circulation.domain import Blocker
from circulation.models import CloseReason, Loan
from members.services import reactivate_member
from tests.support.concurrency import file_db, run_parallel  # noqa: F401
from tests.support.factories import make_charge, make_copy, make_loan, make_member, make_staff

pytestmark = pytest.mark.django_db


# --- Loan model constraints (G10, KL-39) ------------------------------------------


def _loan(**changes: object) -> Loan:
    values: dict[str, object] = {
        "copy": changes.pop("copy", None) or make_copy(),
        "member": make_member(),
        "loaned_on": date(2026, 11, 2),
        "due_on": date(2026, 11, 16),
        "daily_fine_kurus": 500,
        "fine_cap_kurus": 15000,
        "created_by": StaffUser.objects.first() or make_staff(),
    }
    values.update(changes)
    return Loan(**values)  # type: ignore[arg-type]


def _refused(loan: Loan) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        loan.save()


def test_loan_table_and_indexes() -> None:
    """data-design §4: partial unique copy index, (member, closed_on),
    partial due_on and closed_on indexes."""
    with connection.cursor() as cursor:
        indexes = connection.introspection.get_constraints(cursor, "loan")
    columns = {tuple(info["columns"]) for info in indexes.values() if info["index"]}
    assert ("member_id", "closed_on") in columns
    assert ("due_on",) in columns
    assert ("closed_on",) in columns
    with connection.cursor() as cursor:
        cursor.execute("SELECT sql FROM sqlite_master WHERE type = 'index' AND tbl_name = 'loan'")
        sql = " ".join(row[0] or "" for row in cursor.fetchall())
    assert 'CREATE UNIQUE INDEX "loan_one_open_per_copy" ON "loan" ("copy_id") WHERE "closed_on" IS NULL' in sql
    assert 'ON "loan" ("due_on") WHERE "closed_on" IS NULL' in sql


def test_open_loan_is_valid() -> None:
    loan = _loan()
    loan.save()
    assert loan.is_open
    assert loan.member_unlinked_at is None and loan.copy_found_on is None


def test_due_on_must_be_after_loaned_on() -> None:
    _refused(_loan(due_on=date(2026, 11, 2)))


def test_close_reason_and_closed_on_go_together() -> None:
    _refused(_loan(closed_on=date(2026, 11, 10)))
    _refused(_loan(close_reason=CloseReason.RETURNED))
    _refused(_loan(closed_on=date(2026, 11, 10), close_reason="STOLEN"))
    closed = _loan(closed_on=date(2026, 11, 10), close_reason=CloseReason.RETURNED)
    closed.save()
    assert not closed.is_open


def test_copy_found_on_only_for_lost_loans_on_or_after_closing() -> None:
    _refused(
        _loan(
            closed_on=date(2026, 11, 10),
            close_reason=CloseReason.DAMAGED,
            copy_found_on=date(2026, 11, 12),
        )
    )
    _refused(
        _loan(
            closed_on=date(2026, 11, 10),
            close_reason=CloseReason.LOST,
            copy_found_on=date(2026, 11, 9),
        )
    )
    _refused(_loan(copy_found_on=date(2026, 11, 12)))
    found = _loan(
        closed_on=date(2026, 11, 10),
        close_reason=CloseReason.LOST,
        copy_found_on=date(2026, 11, 10),
    )
    found.save()


def test_member_may_be_unlinked() -> None:
    """ADR-0018: the member link becomes NULL after retention."""
    loan = _loan(member=None, closed_on=date(2026, 11, 10), close_reason=CloseReason.RETURNED)
    loan.save()
    assert loan.member is None


# ================================================================================
# G11: check-out, check-in, renewal, deactivation, overdue list
# ================================================================================


NO_OPEN_DAY = "Önümüzdeki 366 günde açık gün yok; kapalı gün ayarlarını kontrol edin"


@pytest.fixture
def today(monkeypatch: pytest.MonkeyPatch):
    def set_today(day: date) -> None:
        monkeypatch.setattr(clock, "today", lambda: day)

    set_today(date(2026, 11, 2))
    return set_today


@pytest.fixture
def clerk():
    return make_staff("ali", role=Role.CLERK)


@pytest.fixture
def admin():
    return make_staff("ayse.y", role=Role.ADMIN)


@pytest.fixture
def member():
    return make_member("Mehmet Demir", member_no=1042)


def _shelf_copy(pk: int | None = None) -> Copy:
    return make_copy(pk=pk)


def _refresh(*objects) -> None:
    for obj in objects:
        obj.refresh_from_db()


# --- check_out (FR-07, FR-08, ADR-0023) ------------------------------------------


def test_tc124_check_out_writes_the_loan(today, clerk, member) -> None:
    copy = _shelf_copy()
    loan = services.check_out(clerk, 1042, copy.barcode)
    _refresh(copy)
    assert (loan.member, loan.copy, loan.loaned_on, loan.due_on) == (
        member,
        copy,
        date(2026, 11, 2),
        date(2026, 11, 16),
    )
    assert (loan.daily_fine_kurus, loan.fine_cap_kurus, loan.created_by) == (500, 15000, clerk)
    assert loan.closed_on is None and loan.renewed_on is None
    assert copy.status == CopyStatus.ON_LOAN


@pytest.mark.parametrize(("due_offset", "refused"), [(0, False), (-1, True)])
def test_tc125_overdue_open_loan_blocks(today, clerk, member, due_offset, refused) -> None:
    make_loan(member, loaned_on=date(2026, 10, 1), due_on=date(2026, 11, 2) + timedelta(days=due_offset))
    copy = _shelf_copy()
    if refused:
        with pytest.raises(RuleViolation, match="^Gecikmiş ödünç var$"):
            services.check_out(clerk, 1042, copy.barcode)
    else:
        services.check_out(clerk, 1042, copy.barcode)


def _assert_refused(clerk, member_no: int, copy: Copy, message: str) -> None:
    loans = Loan.objects.count()
    status = copy.status
    with pytest.raises(RuleViolation) as exc:
        services.check_out(clerk, member_no, copy.barcode)
    assert exc.value.message == message
    assert Loan.objects.count() == loans
    copy.refresh_from_db()
    assert copy.status == status


def test_tc126_refusals_come_from_the_database(today, clerk) -> None:
    inactive = make_member("Pasif Üye", member_no=1, is_active=False)
    _assert_refused(clerk, inactive.member_no, _shelf_copy(), "Üye pasif")

    full = make_member("Dolu Üye", member_no=2)
    for _ in range(3):
        make_loan(full, loaned_on=date(2026, 11, 1))
    _assert_refused(clerk, 2, _shelf_copy(), "Ödünç limiti dolu")

    late = make_member("Geciken Üye", member_no=3)
    make_loan(late, loaned_on=date(2026, 10, 1), due_on=date(2026, 10, 15))
    _assert_refused(clerk, 3, _shelf_copy(), "Gecikmiş ödünç var")

    debtor = make_member("Borçlu Üye", member_no=4)
    make_charge(debtor, EntryKind.FINE, 5000)
    _assert_refused(clerk, 4, _shelf_copy(), "Borç eşiği aşıldı")

    free = make_member("Serbest Üye", member_no=5)
    on_loan = make_loan(make_member("Başka", member_no=6)).copy
    _assert_refused(clerk, free.member_no, on_loan, "Nüsha rafta değil")


def test_check_out_unknown_member_or_copy(today, clerk, member) -> None:
    with pytest.raises(RuleViolation, match="^Üye bulunamadı$"):
        services.check_out(clerk, 999999, _shelf_copy().barcode)
    with pytest.raises(RuleViolation, match="^Nüsha bulunamadı$"):
        services.check_out(clerk, 1042, "99999999")
    assert Loan.objects.count() == 0


def test_check_out_strips_the_barcode(today, clerk, member) -> None:
    copy = _shelf_copy()
    assert services.check_out(clerk, 1042, f" {copy.barcode} ").copy == copy


def test_check_out_needs_active_staff(today, member) -> None:
    with pytest.raises(PermissionDenied):
        services.check_out(make_staff("eski", is_active=False), 1042, _shelf_copy().barcode)


def test_tc131_settings_change_affects_new_loans_only(today, clerk, admin, member) -> None:
    old = services.check_out(clerk, 1042, _shelf_copy().barcode)
    update_settings(admin, loan_period_days=21)
    new = services.check_out(clerk, 1042, _shelf_copy().barcode)
    old.refresh_from_db()
    assert old.due_on == date(2026, 11, 16)
    assert new.due_on == date(2026, 11, 23)


def test_tc132_fine_uses_the_rate_of_checkout(today, clerk, admin, member) -> None:
    copy = _shelf_copy()
    services.check_out(clerk, 1042, copy.barcode)
    update_settings(admin, daily_fine_kurus=1000)
    today(date(2026, 11, 19))
    result = services.check_in(clerk, copy.barcode)
    assert result.fine_kurus == 1500


def test_tc133_no_open_day_refuses_check_out(today, clerk, member) -> None:
    WeeklyClosedDay.objects.bulk_create([WeeklyClosedDay(weekday=d) for d in range(7)])
    copy = _shelf_copy()
    _assert_refused(clerk, 1042, copy, NO_OPEN_DAY)
    assert copy.status == CopyStatus.ON_SHELF


def test_tc149_second_open_loan_violates_the_partial_index(member) -> None:
    loan = make_loan(member)
    with pytest.raises(IntegrityError), transaction.atomic():
        make_loan(make_member("Başka Üye"), loan.copy)


def test_tc285_reactivated_member_can_borrow(today, clerk) -> None:
    member = make_member("Dönen Üye", member_no=77, is_active=False)
    reactivate_member(clerk, member)
    assert services.check_out(clerk, 77, _shelf_copy().barcode).member == member


# --- check_in (FR-09, FR-12, ADR-0040) -------------------------------------------


def _loan_due(member, due_on: date = date(2026, 11, 16), **kwargs) -> Loan:
    return make_loan(member, loaned_on=due_on - timedelta(days=14), due_on=due_on, **kwargs)


def test_tc134_return_on_the_due_date(today, clerk, member) -> None:
    loan = _loan_due(member)
    today(date(2026, 11, 16))
    result = services.check_in(clerk, loan.copy.barcode)
    _refresh(loan, loan.copy)
    assert (loan.close_reason, loan.closed_on, loan.closed_by) == ("RETURNED", date(2026, 11, 16), clerk)
    assert loan.copy.status == CopyStatus.ON_SHELF
    assert (result.loan, result.fine_kurus) == (loan, 0)
    assert not LedgerEntry.objects.exists()


def test_tc136_fine_is_capped(today, clerk, member) -> None:
    loan = _loan_due(member)
    today(date(2026, 11, 16) + timedelta(days=40))
    assert services.check_in(clerk, loan.copy.barcode).fine_kurus == 15000
    assert LedgerEntry.objects.get().amount_kurus == 15000


def test_tc137_zero_rate_writes_no_fine(today, clerk, member) -> None:
    loan = _loan_due(member, daily_fine_kurus=0)
    today(date(2026, 11, 21))
    result = services.check_in(clerk, loan.copy.barcode)
    loan.refresh_from_db()
    assert result.fine_kurus == 0 and not loan.is_open
    assert not LedgerEntry.objects.exists()


def test_late_return_fine_is_linked_to_loan_and_member(today, clerk, member) -> None:
    loan = _loan_due(member)
    today(date(2026, 11, 19))
    services.check_in(clerk, loan.copy.barcode)
    fine = LedgerEntry.objects.get()
    assert (fine.kind, fine.amount_kurus, fine.loan, fine.member) == ("FINE", 1500, loan, member)


def test_tc138_check_in_without_open_loan(today, clerk) -> None:
    copy = _shelf_copy()
    with pytest.raises(RuleViolation, match="^Bu nüshanın açık ödüncü yok$"):
        services.check_in(clerk, copy.barcode)
    with pytest.raises(RuleViolation, match="^Nüsha bulunamadı$"):
        services.check_in(clerk, "99999999")
    copy.refresh_from_db()
    assert copy.status == CopyStatus.ON_SHELF
    assert not Loan.objects.exists() and not LedgerEntry.objects.exists()


@pytest.mark.parametrize(("extra_closed", "days", "fine"), [(False, 3, 1500), (True, 2, 1000)])
def test_tc278_weekly_days_count_single_dates_do_not(
    today, clerk, member, extra_closed, days, fine
) -> None:
    WeeklyClosedDay.objects.create(weekday=6)
    if extra_closed:
        ClosedDate.objects.create(date=date(2026, 11, 15))
    loan = _loan_due(member, date(2026, 11, 14))
    today(date(2026, 11, 17))
    assert services.check_in(clerk, loan.copy.barcode).fine_kurus == fine
    assert fine == days * 500


# --- renew (FR-10) ---------------------------------------------------------------


def test_tc139_renewal_extends_from_the_due_date(today, clerk, member) -> None:
    loan = _loan_due(member)
    today(date(2026, 11, 10))
    renewed = services.renew(clerk, loan.pk)
    assert (renewed.due_on, renewed.renewed_on) == (date(2026, 11, 30), date(2026, 11, 10))
    assert (renewed.daily_fine_kurus, renewed.fine_cap_kurus) == (500, 15000)


def test_tc140_renewal_shifts_off_a_closed_sunday(today, clerk, admin, member) -> None:
    WeeklyClosedDay.objects.create(weekday=6)
    LibrarySettings.objects.filter(pk=1).update(loan_period_days=13)
    loan = _loan_due(member)
    today(date(2026, 11, 10))
    assert services.renew(clerk, loan.pk).due_on == date(2026, 11, 30)


def test_tc141_second_renewal_is_refused(today, clerk, member) -> None:
    loan = _loan_due(member, renewed_on=date(2026, 11, 5))
    with pytest.raises(RuleViolation, match="^Uzatma hakkı kullanıldı$"):
        services.renew(clerk, loan.pk)
    loan.refresh_from_db()
    assert loan.due_on == date(2026, 11, 16)


def test_tc142_debt_blocks_renewal(today, clerk, member) -> None:
    loan = _loan_due(member)
    make_charge(member, EntryKind.FINE, 200)
    with pytest.raises(RuleViolation, match="^Ödenmemiş borç var$"):
        services.renew(clerk, loan.pk)


@pytest.mark.parametrize(("day", "refused"), [(date(2026, 11, 16), False), (date(2026, 11, 17), True)])
def test_tc143_renewal_on_and_after_the_due_date(today, clerk, member, day, refused) -> None:
    loan = _loan_due(member)
    today(day)
    if refused:
        with pytest.raises(RuleViolation, match="^Ödünç gecikmiş$"):
            services.renew(clerk, loan.pk)
    else:
        assert services.renew(clerk, loan.pk).due_on == date(2026, 11, 30)


def test_tc144_closed_loan_and_no_open_day(today, clerk, member) -> None:
    closed = _loan_due(member, closed_on=date(2026, 11, 3), close_reason=CloseReason.RETURNED)
    with pytest.raises(RuleViolation, match="^Ödünç kapanmış$"):
        services.renew(clerk, closed.pk)
    loan = _loan_due(member)
    WeeklyClosedDay.objects.bulk_create([WeeklyClosedDay(weekday=d) for d in range(7)])
    with pytest.raises(RuleViolation, match=f"^{NO_OPEN_DAY}$"):
        services.renew(clerk, loan.pk)
    loan.refresh_from_db()
    assert (loan.due_on, loan.renewed_on) == (date(2026, 11, 16), None)
    with pytest.raises(RuleViolation, match="^Ödünç bulunamadı$"):
        services.renew(clerk, 999)


def test_tc288_renewal_overdue_check_uses_calendar_days(today, clerk, member) -> None:
    ClosedDate.objects.create(date=date(2026, 11, 17))
    loan = _loan_due(member)
    today(date(2026, 11, 17))
    with pytest.raises(RuleViolation, match="^Ödünç gecikmiş$"):
        services.renew(clerk, loan.pk)


# --- member_status, preview_checkout, open_loans, overdue_loans -------------------


def test_member_status_lists_open_loans_balance_and_blockers(today, member) -> None:
    late = make_loan(member, loaned_on=date(2026, 10, 1), due_on=date(2026, 10, 20))
    soon = make_loan(member, loaned_on=date(2026, 11, 1))
    make_loan(member, closed_on=date(2026, 11, 1), close_reason=CloseReason.RETURNED, loaned_on=date(2026, 10, 1))
    make_charge(member, EntryKind.FINE, 700)
    status = services.member_status(1042, date(2026, 11, 2))
    assert status.member == member
    assert [loan.pk for loan in status.open_loans] == [late.pk, soon.pk]
    assert status.balance_kurus == 700
    assert status.blockers == [Blocker.HAS_OVERDUE]
    assert services.open_loans(member) == status.open_loans
    with pytest.raises(RuleViolation, match="^Üye bulunamadı$"):
        services.member_status(5, date(2026, 11, 2))


def test_preview_checkout(today, member) -> None:
    copy = _shelf_copy()
    preview = services.preview_checkout(1042, copy.barcode, date(2026, 11, 2))
    assert (preview.copy, preview.due_on, preview.blockers) == (copy, date(2026, 11, 16), [])
    on_loan = make_loan(make_member("Başka")).copy
    assert services.preview_checkout(1042, on_loan.barcode, date(2026, 11, 2)).blockers == [
        Blocker.COPY_NOT_ON_SHELF
    ]
    with pytest.raises(RuleViolation, match="^Nüsha bulunamadı$"):
        services.preview_checkout(1042, "99999999", date(2026, 11, 2))


def test_preview_without_open_day_has_no_due_date(today, member) -> None:
    WeeklyClosedDay.objects.bulk_create([WeeklyClosedDay(weekday=d) for d in range(7)])
    with pytest.raises(RuleViolation, match=f"^{NO_OPEN_DAY}$"):
        services.preview_checkout(1042, _shelf_copy().barcode, date(2026, 11, 2))


def test_tc287_overdue_loans_skip_single_closed_dates(member) -> None:
    ClosedDate.objects.create(date=date(2026, 11, 18))
    late = _loan_due(member)
    _loan_due(make_member("Zamanında"), date(2026, 11, 20))
    _loan_due(member, date(2026, 11, 10), closed_on=date(2026, 11, 12), close_reason=CloseReason.RETURNED)
    rows = services.overdue_loans(date(2026, 11, 20))
    assert len(rows) == 1
    row = rows[0]
    assert (row.loan, row.member_no, row.full_name, row.phone) == (late, 1042, "Mehmet Demir", "0555 111 22 33")
    assert (row.title, row.due_on, row.late_days, row.accrued_fine) == (
        late.copy.book.title,
        date(2026, 11, 16),
        3,
        1500,
    )


def test_overdue_loans_oldest_first(member) -> None:
    newer = _loan_due(member, date(2026, 11, 16))
    older = _loan_due(member, date(2026, 11, 10))
    assert [r.loan for r in services.overdue_loans(date(2026, 11, 20))] == [older, newer]


# --- deactivate_member (FR-02, KL-22; user decision 2026-11-01) -------------------


def test_tc53_deactivation_without_loans_or_debt(today, clerk, member) -> None:
    services.deactivate_member(clerk, member, confirm_debt=False)
    member.refresh_from_db()
    assert (member.is_active, member.deactivated_on) == (False, date(2026, 11, 2))


@pytest.mark.parametrize("confirm", [False, True])
def test_tc54_open_loan_blocks_deactivation(today, clerk, member, confirm) -> None:
    make_loan(member)
    make_charge(member, EntryKind.FINE, 100)
    with pytest.raises(RuleViolation, match="^Açık ödüncü olan üye pasifleştirilemez$"):
        services.deactivate_member(clerk, member, confirm_debt=confirm)
    member.refresh_from_db()
    assert member.is_active


def test_tc55_debt_needs_confirmation(today, clerk, member) -> None:
    make_charge(member, EntryKind.FINE, 1)
    with pytest.raises(RuleViolation, match="^Üyenin 0,01 TL borcu var; onaylayarak pasifleştirin$"):
        services.deactivate_member(clerk, member, confirm_debt=False)
    member.refresh_from_db()
    assert member.is_active


def test_tc56_confirmed_debt_deactivates(today, clerk, member) -> None:
    make_charge(member, EntryKind.FINE, 2000)
    services.deactivate_member(clerk, member, confirm_debt=True)
    member.refresh_from_db()
    assert not member.is_active
    assert billing.member_balance(member) == 2000


def test_tc53_guard_anonymized_member_is_refused(today, clerk) -> None:
    """User decision 2026-11-01: checked before loans and debt."""
    member = make_member(member_no=9, anonymized=True, deactivated_on=date(2024, 1, 1))
    make_charge(member, EntryKind.FINE, 100)
    with pytest.raises(RuleViolation, match="^Anonimleştirilmiş üye pasifleştirilemez$"):
        services.deactivate_member(clerk, member, confirm_debt=True)
    member.refresh_from_db()
    assert member.deactivated_on == date(2024, 1, 1)


def test_tc53_guard_inactive_member_keeps_its_deactivation_date(today, clerk) -> None:
    """User decision 2026-11-01: ``deactivated_on`` (ADR-0045) is not overwritten."""
    member = make_member(member_no=9, is_active=False, deactivated_on=date(2025, 5, 1))
    make_loan(member)
    with pytest.raises(RuleViolation, match="^Üye zaten pasif$"):
        services.deactivate_member(clerk, member, confirm_debt=True)
    member.refresh_from_db()
    assert member.deactivated_on == date(2025, 5, 1)


def test_deactivation_needs_active_staff(today, member) -> None:
    with pytest.raises(PermissionDenied):
        services.deactivate_member(make_staff("eski", is_active=False), member, confirm_debt=False)


# --- Concurrency (data-design §5; file-based SQLite) ------------------------------


@pytest.mark.django_db(transaction=True)
def test_tc145_same_copy_to_two_members(file_db, today) -> None:
    clerk = make_staff("ali")
    make_member("Bir", member_no=1)
    make_member("İki", member_no=2)
    copy = _shelf_copy()
    results = run_parallel(
        lambda: services.check_out(clerk, 1, copy.barcode),
        lambda: services.check_out(clerk, 2, copy.barcode),
    )
    loans = [r for r in results if isinstance(r, Loan)]
    errors = [r for r in results if not isinstance(r, Loan)]
    assert len(loans) == 1 and len(errors) == 1, results
    assert isinstance(errors[0], RuleViolation) and errors[0].message == "Nüsha rafta değil"
    assert Loan.objects.filter(closed_on__isnull=True).count() == 1


@pytest.mark.django_db(transaction=True)
def test_tc146_limit_holds_under_concurrency(file_db, today) -> None:
    clerk = make_staff("ali")
    member = make_member("Bir", member_no=1)
    for _ in range(2):
        make_loan(member, loaned_on=date(2026, 11, 1))
    first, second = _shelf_copy(), _shelf_copy()
    results = run_parallel(
        lambda: services.check_out(clerk, 1, first.barcode),
        lambda: services.check_out(clerk, 1, second.barcode),
    )
    errors = [r for r in results if not isinstance(r, Loan)]
    assert len(errors) == 1, results
    assert isinstance(errors[0], RuleViolation) and errors[0].message == "Ödünç limiti dolu"
    assert Loan.objects.filter(member=member, closed_on__isnull=True).count() == 3


@pytest.mark.django_db(transaction=True)
def test_tc147_double_check_in(file_db, today) -> None:
    clerk = make_staff("ali")
    loan = _loan_due(make_member("Bir", member_no=1))
    today(date(2026, 11, 19))
    results = run_parallel(
        lambda: services.check_in(clerk, loan.copy.barcode),
        lambda: services.check_in(clerk, loan.copy.barcode),
    )
    errors = [r for r in results if isinstance(r, Exception)]
    assert len(errors) == 1, results
    assert isinstance(errors[0], RuleViolation)
    assert errors[0].message == "Bu nüshanın açık ödüncü yok"
    assert list(LedgerEntry.objects.values_list("kind", "amount_kurus")) == [("FINE", 1500)]


@pytest.mark.django_db(transaction=True)
def test_tc148_double_renewal(file_db, today) -> None:
    clerk = make_staff("ali")
    loan = _loan_due(make_member("Bir", member_no=1))
    today(date(2026, 11, 10))
    results = run_parallel(lambda: services.renew(clerk, loan.pk), lambda: services.renew(clerk, loan.pk))
    errors = [r for r in results if isinstance(r, Exception)]
    assert len(errors) == 1, results
    assert isinstance(errors[0], RuleViolation)
    assert errors[0].message == "Uzatma hakkı kullanıldı"
    loan.refresh_from_db()
    assert loan.due_on == date(2026, 11, 30)
