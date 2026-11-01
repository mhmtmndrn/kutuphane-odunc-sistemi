"""Retention and anonymization (G15): TC-201…TC-207, TC-305, TC-306 and
TC-330, TC-332, TC-333 (ADR-0018, ADR-0045, ADR-0055; G14–G16 small
decisions 1 and 9). Retention is the default 2 years."""

from __future__ import annotations

from datetime import date, timedelta
from io import StringIO

import pytest
from django.core.management import CommandError, call_command

from accounts.models import Role
from administration.models import Job, JobRun
from billing import services as billing
from billing.models import EntryKind, LedgerEntry
from catalog.models import Copy
from circulation.models import CloseReason, Loan
from members import services as members
from members.models import ConsentAction, ConsentEvent, Member
from notifications.models import ReminderLog, ReminderStatus
from operations import services
from tests.support.factories import make_charge, make_copy, make_loan, make_member, make_staff

pytestmark = pytest.mark.django_db

NOVEMBER_1 = date(2026, 11, 1)


@pytest.fixture
def clerk():
    return make_staff("ali", role=Role.CLERK)


def run(day: str) -> str:
    out = StringIO()
    call_command("anonymize_expired", "--date", day, stdout=out)
    return out.getvalue().strip()


def counts_text(members: int, loans: int, deferred: int) -> str:
    return f"anonimleştirilen üye={members}, bağı koparılan ödünç={loans}, ertelenen üye={deferred}"


def inactive_member(clerk, *, on: date = NOVEMBER_1, **fields) -> Member:
    member = make_member(
        fields.pop("full_name", "Ayşe Yılmaz"),
        fields.pop("phone", "0555 111 22 33"),
        fields.pop("email", "ayse@example.org"),
        is_active=False,
        deactivated_on=on,
        **fields,
    )
    ConsentEvent.objects.create(
        member=member, action=ConsentAction.GIVEN, effective_on=date(2026, 1, 5), recorded_by=clerk
    )
    Member.objects.filter(pk=member.pk).update(has_email_consent=True)
    return Member.objects.get(pk=member.pk)


def returned_loan(member: Member, closed_on: date = NOVEMBER_1) -> Loan:
    return make_loan(
        member,
        make_copy(),
        loaned_on=closed_on - timedelta(days=14),
        due_on=closed_on,
        closed_on=closed_on,
        close_reason=CloseReason.RETURNED,
    )


def test_tc201_member_anonymized_the_day_after_retention(clerk) -> None:
    member = inactive_member(clerk)
    make_charge(member, EntryKind.FINE, 1500)
    billing.record_payment(clerk, member, 1500)
    entries = list(LedgerEntry.objects.order_by("id").values_list("kind", "amount_kurus"))

    assert run("2028-11-01") == counts_text(0, 0, 0)
    member.refresh_from_db()
    assert member.full_name == "Ayşe Yılmaz" and member.anonymized_at is None

    assert run("2028-11-02") == counts_text(1, 0, 0)
    member.refresh_from_db()
    assert (member.full_name, member.phone, member.phone_digits, member.email) == (
        None,
        None,
        None,
        None,
    )
    assert member.search_key == ""
    assert member.has_email_consent is False
    assert member.anonymized_at is not None
    assert not ConsentEvent.objects.filter(member=member).exists()
    assert list(LedgerEntry.objects.order_by("id").values_list("kind", "amount_kurus")) == entries
    assert LedgerEntry.objects.filter(member=member).count() == len(entries)
    assert billing.member_balance(member) == 0


def test_tc202_loan_unlinked_the_day_after_retention(clerk) -> None:
    member = make_member()
    loan = returned_loan(member)
    fine = make_charge(member, EntryKind.FINE, 1000, loan=loan)

    run("2028-11-01")
    loan.refresh_from_db()
    assert loan.member_id == member.pk and loan.member_unlinked_at is None

    assert run("2028-11-02") == counts_text(0, 1, 0)
    loan.refresh_from_db()
    member.refresh_from_db()
    assert loan.member_id is None and loan.member_unlinked_at is not None
    assert member.archived_loan_count == 1
    fine = LedgerEntry.objects.get(pk=fine.pk)
    assert fine.loan_id is None and fine.member_id == member.pk


def _total(member: Member) -> int:
    member.refresh_from_db()
    return Loan.objects.filter(member=member).count() + member.archived_loan_count


def test_tc203_total_loan_count_is_kept(clerk) -> None:
    member = inactive_member(clerk, on=date(2026, 6, 1))
    returned_loan(member, date(2026, 3, 1))
    returned_loan(member, date(2026, 5, 1))
    other = make_member("Mehmet Kaya")
    returned_loan(other, date(2028, 6, 1))
    before = (_total(member), _total(other), Loan.objects.count(), Copy.objects.count())
    assert run("2028-11-02") == counts_text(1, 2, 0)
    after = (_total(member), _total(other), Loan.objects.count(), Copy.objects.count())
    assert after == before
    assert member.archived_loan_count == 2


def test_tc204_second_run_on_the_same_day_does_nothing(clerk) -> None:
    member = inactive_member(clerk)
    returned_loan(member)
    assert run("2028-11-02") == counts_text(1, 1, 0)
    assert run("2028-11-02") == counts_text(0, 0, 0)
    member.refresh_from_db()
    assert member.archived_loan_count == 1


def test_tc205_only_expired_returned_loans_and_inactive_members(clerk) -> None:
    active = make_member()
    old_returned = returned_loan(active, date(2025, 10, 1))
    still_open = make_loan(active, make_copy(), loaned_on=date(2025, 10, 1))
    recent_inactive = inactive_member(clerk, on=date(2027, 11, 1), full_name="Can Ak")
    assert run("2028-11-02") == counts_text(0, 1, 0)
    old_returned.refresh_from_db()
    still_open.refresh_from_db()
    assert old_returned.member_id is None
    assert still_open.member_id == active.pk
    active.refresh_from_db()
    recent_inactive.refresh_from_db()
    assert active.anonymized_at is None and active.full_name == "Ayşe Yılmaz"
    assert recent_inactive.anonymized_at is None and recent_inactive.full_name == "Can Ak"


def test_tc206_old_name_and_phone_are_not_found(clerk) -> None:
    member = inactive_member(clerk, full_name="Şükrü Öztürk", phone="0532 987 65 43")
    assert [m.pk for m in members.search_members("Şükrü")] == [member.pk]
    run("2028-11-02")
    member.refresh_from_db()
    assert member.search_key == ""
    assert members.search_members("Şükrü") == []
    assert members.search_members("ozturk") == []
    assert members.search_members("0532 987 65 43") == []
    assert members.search_members("98765") == []


@pytest.fixture
def second_loan_fails(monkeypatch: pytest.MonkeyPatch):
    original = services._clear_reminder_errors
    calls: list[int] = []

    def flaky(loan_id: int) -> None:
        calls.append(loan_id)
        original(loan_id)
        if len(calls) == 2:
            raise RuntimeError("disk dolu")

    monkeypatch.setattr(services, "_clear_reminder_errors", flaky)
    return monkeypatch


def test_tc207_tc333_failure_rolls_back_one_record_and_next_run_continues(
    clerk, second_loan_fails
) -> None:
    member = inactive_member(clerk)
    first = returned_loan(member, date(2026, 3, 1))
    second = returned_loan(member, date(2026, 5, 1))
    fine = make_charge(member, EntryKind.FINE, 500, loan=second)
    billing.record_payment(clerk, member, 500)  # no debt: the member is anonymized

    with pytest.raises(CommandError) as info:
        run("2028-11-02")
    assert info.value.returncode == 1
    assert str(info.value) == "Anonimleştirme yapılamadı: RuntimeError: disk dolu"
    run_row = JobRun.objects.get()
    assert (run_row.job, run_row.status, run_row.detail) == (
        Job.ANONYMIZE,
        JobRun.Status.FAILED,
        "RuntimeError: disk dolu",
    )
    first.refresh_from_db()
    second.refresh_from_db()
    member.refresh_from_db()
    assert first.member_id is None
    # The failing record: link, counter and ledger link rolled back together.
    assert second.member_id == member.pk and second.member_unlinked_at is None
    assert LedgerEntry.objects.get(pk=fine.pk).loan_id == second.pk
    assert member.archived_loan_count == 1
    assert member.anonymized_at is None  # stopped before the members

    second_loan_fails.undo()
    assert run("2028-11-02") == counts_text(1, 1, 0)  # TC-333
    second.refresh_from_db()
    member.refresh_from_db()
    assert second.member_id is None
    assert member.archived_loan_count == 2
    assert member.anonymized_at is not None
    assert JobRun.objects.order_by("id").last().status == JobRun.Status.SUCCESS


def test_tc305_member_with_debt_waits_until_paid(clerk) -> None:
    member = inactive_member(clerk)
    make_charge(member, EntryKind.FINE, 2000)
    assert run("2028-11-02") == counts_text(0, 0, 1)
    member.refresh_from_db()
    assert member.anonymized_at is None and member.full_name == "Ayşe Yılmaz"

    billing.record_payment(clerk, member, 2000)
    assert run("2028-11-03") == counts_text(1, 0, 0)
    member.refresh_from_db()
    assert member.anonymized_at is not None


def test_tc306_loans_of_a_deferred_member_are_still_unlinked(clerk) -> None:
    member = inactive_member(clerk)
    make_charge(member, EntryKind.FINE, 2000)
    loan = returned_loan(member)
    assert run("2028-11-02") == counts_text(0, 1, 1)
    loan.refresh_from_db()
    member.refresh_from_db()
    assert loan.member_id is None
    assert member.archived_loan_count == 1
    assert member.anonymized_at is None


def test_tc330_reminder_errors_cleared_with_the_unlink(clerk) -> None:
    member = make_member(email="ayse@example.org")
    old = returned_loan(member)
    kept = returned_loan(member, date(2028, 10, 1))
    refused = "SMTPRecipientsRefused: {'ayse@example.org': (550, b'User unknown')}"
    failed = ReminderLog.objects.create(
        loan=old, kind="OVERDUE_1", status=ReminderStatus.FAILED, error=refused, due_on=NOVEMBER_1
    )
    sent = ReminderLog.objects.create(
        loan=old, kind="OVERDUE_1", status=ReminderStatus.SENT, due_on=NOVEMBER_1
    )
    other = ReminderLog.objects.create(
        loan=kept,
        kind="DUE_SOON",
        status=ReminderStatus.FAILED,
        error=refused,
        due_on=date(2028, 10, 1),
    )
    before = {
        row.pk: (row.loan_id, row.kind, row.status, row.due_on, row.sent_at)
        for row in (failed, sent, other)
    }
    assert run("2028-11-02") == counts_text(0, 1, 0)
    for row in (failed, sent, other):
        row.refresh_from_db()
        assert (row.loan_id, row.kind, row.status, row.due_on, row.sent_at) == before[row.pk]
    assert failed.error is None and sent.error is None
    assert other.error == refused


def test_tc332_invalid_date(clerk) -> None:
    member = inactive_member(clerk)
    with pytest.raises(CommandError) as info:
        run("2028-02-30")
    assert str(info.value) == "Geçersiz tarih: 2028-02-30"
    assert JobRun.objects.count() == 0
    member.refresh_from_db()
    assert member.full_name == "Ayşe Yılmaz"


def test_job_run_and_default_date(clerk, monkeypatch) -> None:
    inactive_member(clerk)
    monkeypatch.setattr("administration.clock.today", lambda: date(2028, 11, 2))
    out = StringIO()
    call_command("anonymize_expired", stdout=out)
    assert out.getvalue().strip() == counts_text(1, 0, 0)
    run_row = JobRun.objects.get()
    assert (run_row.job, run_row.run_on, run_row.status, run_row.detail) == (
        Job.ANONYMIZE,
        date(2028, 11, 2),
        JobRun.Status.SUCCESS,
        counts_text(1, 0, 0),
    )


def test_retention_setting_is_used(clerk) -> None:
    from administration.models import LibrarySettings

    LibrarySettings.objects.filter(pk=1).update(retention_years=1)
    member = inactive_member(clerk)
    assert run("2027-11-02") == counts_text(1, 0, 0)
    member.refresh_from_db()
    assert member.anonymized_at is not None


def test_deferred_members_rows(clerk) -> None:
    later = inactive_member(clerk, on=NOVEMBER_1, full_name="Can Ak")
    earlier = inactive_member(clerk, on=date(2026, 10, 1), full_name="Ece Su")
    make_charge(later, EntryKind.FINE, 2000)
    make_charge(earlier, EntryKind.FEE, 4550)
    inactive_member(clerk, on=date(2026, 9, 1), full_name="Borçsuz")  # no debt: not listed
    not_expired = inactive_member(clerk, on=date(2027, 11, 1), full_name="Süresi Dolmadı")
    make_charge(not_expired, EntryKind.FINE, 100)
    rows = services.deferred_members(date(2028, 11, 2))
    assert rows == [
        services.DeferredRow(
            earlier.member_no, "Ece Su", date(2026, 10, 1), date(2028, 10, 1), 4550
        ),
        services.DeferredRow(later.member_no, "Can Ak", NOVEMBER_1, date(2028, 11, 1), 2000),
    ]
