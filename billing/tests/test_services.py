"""Billing service tests (G09).

TC-80…TC-85, TC-87…TC-90, TC-92…TC-96, TC-100…TC-103, TC-270…TC-274; plus
``post_charge``, the input checks of each service and the I6 model guard.
"""

from __future__ import annotations

from datetime import date, datetime, timezone as dt_timezone

import pytest
from django.core.exceptions import PermissionDenied
from django.db import connection

from accounts.models import Role
from administration.audit import AuditAction
from administration.errors import RuleViolation
from administration.models import AuditEvent
from billing import services
from billing.domain import OpenCharge, balance
from billing.models import Allocation, EntryKind, LedgerEntry
from circulation.models import CloseReason
from tests.support.concurrency import file_db, run_parallel  # noqa: F401
from tests.support.factories import make_charge, make_loan, make_member, make_staff

pytestmark = pytest.mark.django_db

PAID_MESSAGE = "Para iadesi, ödenmiş ve henüz iade edilmemiş tutarı aşamaz"
PRECONDITION_MESSAGE = "Para iadesi yalnız bulunan kayıp nüshanın bedeli için yapılabilir"


@pytest.fixture
def clerk():
    return make_staff("ali", role=Role.CLERK, full_name="Ali Yılmaz")


@pytest.fixture
def admin():
    return make_staff("ayse.y", role=Role.ADMIN, full_name="Ayşe Yıldız")


@pytest.fixture
def member():
    return make_member("Mehmet Demir", member_no=1042)


def _counts() -> tuple[int, int, int]:
    return LedgerEntry.objects.count(), Allocation.objects.count(), AuditEvent.objects.count()


def _found_lost_fee(member, amount: int = 12000, *, found: bool = True) -> LedgerEntry:
    """A FEE whose loan closed as LOST; ``found`` sets ``copy_found_on``."""
    loan = make_loan(
        member,
        closed_on=date(2026, 11, 20),
        close_reason=CloseReason.LOST,
        copy_found_on=date(2026, 11, 25) if found else None,
    )
    return make_charge(member, EntryKind.FEE, amount, loan=loan)


def _unpaid(entry: LedgerEntry) -> int:
    return {c.id: c.unpaid for c in services.open_charges(entry.member)}.get(entry.id, 0)


def _audit(action: AuditAction) -> AuditEvent:
    return AuditEvent.objects.get(action=action)


# --- post_charge -----------------------------------------------------------------


def test_post_charge_fine_writes_no_audit(clerk, member) -> None:
    loan = make_loan(member)
    entry = services.post_charge(clerk, member, loan, "FINE", 1500)
    assert (entry.kind, entry.amount_kurus, entry.loan, entry.created_by) == (
        "FINE",
        1500,
        loan,
        clerk,
    )
    assert AuditEvent.objects.count() == 0


def test_post_charge_fee_writes_fee_audit(admin, member) -> None:
    loan = make_loan(member)
    entry = services.post_charge(admin, member, loan, "FEE", 12000)
    event = _audit(AuditAction.FEE)
    assert (event.actor, event.target_type, event.target_id) == (admin, "ledger_entry", entry.id)
    assert event.details == {"amount_kurus": 12000, "member_no": 1042}


@pytest.mark.parametrize(("kind", "amount"), [("PAYMENT", 100), ("FINE", 0), ("FEE", -5)])
def test_post_charge_refuses_other_kinds_and_non_positive(clerk, member, kind, amount) -> None:
    with pytest.raises(ValueError):
        services.post_charge(clerk, member, None, kind, amount)
    assert LedgerEntry.objects.count() == 0


# --- record_payment (FR-13, ADR-0017) --------------------------------------------


def test_tc80_payment_reduces_the_debt_and_is_audited(clerk, member) -> None:
    make_charge(member, EntryKind.FINE, 4000)
    payment = services.record_payment(clerk, member, 1500)
    assert services.member_balance(member) == 2500
    assert (payment.kind, payment.amount_kurus, payment.created_by) == ("PAYMENT", 1500, clerk)
    assert payment.created_at is not None
    row = [r for r in services.statement(member) if r.entry_id == payment.id][0]
    assert (row.kind_label, row.amount_kurus, row.staff_name) == ("Ödeme", 1500, "Ali Yılmaz")
    event = _audit(AuditAction.PAYMENT)
    assert (event.actor, event.target_type, event.target_id) == (clerk, "ledger_entry", payment.id)
    assert event.details == {"amount_kurus": 1500, "member_no": 1042}


def test_tc81_payment_above_the_debt_is_refused(clerk, member) -> None:
    make_charge(member, EntryKind.FINE, 4000)
    before = _counts()
    with pytest.raises(RuleViolation, match="^Ödeme tutarı borcu aşamaz$"):
        services.record_payment(clerk, member, 4001)
    assert _counts() == before
    services.record_payment(clerk, member, 4000)
    assert services.member_balance(member) == 0


def test_tc82_zero_payment_is_refused_one_kurus_accepted(clerk, member) -> None:
    make_charge(member, EntryKind.FINE, 4000)
    with pytest.raises(RuleViolation, match="^Ödeme tutarı 0,00 TL'den büyük olmalı$"):
        services.record_payment(clerk, member, 0)
    assert LedgerEntry.objects.filter(kind="PAYMENT").count() == 0
    services.record_payment(clerk, member, 1)
    assert services.member_balance(member) == 3999


def test_tc83_payment_is_spread_fifo_and_fully(clerk, member) -> None:
    fine = make_charge(member, EntryKind.FINE, 1500)
    fee = make_charge(member, EntryKind.FEE, 1000)
    payment = services.record_payment(clerk, member, 2000)
    allocations = {
        a.charge_entry_id: a.amount_kurus for a in Allocation.objects.filter(credit_entry=payment)
    }
    assert allocations == {fine.id: 1500, fee.id: 500}
    assert sum(allocations.values()) == payment.amount_kurus  # I2
    for charge in (fine, fee):  # I3
        assert allocations[charge.id] <= charge.amount_kurus
    assert _unpaid(fine) == 0 and _unpaid(fee) == 500  # I4
    assert services.open_charges(member) == [OpenCharge(fee.id, 500)]


def test_tc84_equal_created_at_goes_to_the_smaller_id(clerk, member) -> None:
    moment = datetime(2026, 11, 16, 9, 0, tzinfo=dt_timezone.utc)
    first = make_charge(member, EntryKind.FINE, 1500, created_at=moment)
    second = make_charge(member, EntryKind.FINE, 1500, created_at=moment)
    payment = services.record_payment(clerk, member, 1000)
    allocation = Allocation.objects.get(credit_entry=payment)
    assert allocation.charge_entry_id == min(first.id, second.id)


def test_open_charges_order_by_created_at_then_id(member) -> None:
    late = make_charge(member, created_at=datetime(2026, 11, 17, tzinfo=dt_timezone.utc))
    early = make_charge(member, created_at=datetime(2026, 11, 16, tzinfo=dt_timezone.utc))
    assert [c.id for c in services.open_charges(member)] == [early.id, late.id]


def test_tc85_waived_charge_gets_no_payment(clerk, admin, member) -> None:
    fine = make_charge(member, EntryKind.FINE, 1500)
    fee = make_charge(member, EntryKind.FEE, 1000)
    services.waive(admin, fine, 1500, "Hastalık")
    payment = services.record_payment(clerk, member, 500)
    assert list(
        Allocation.objects.filter(credit_entry=payment).values_list("charge_entry_id", "amount_kurus")
    ) == [(fee.id, 500)]


def test_payment_needs_staff(member) -> None:
    make_charge(member, EntryKind.FINE, 1000)
    inactive = make_staff("eski", is_active=False)
    with pytest.raises(PermissionDenied):
        services.record_payment(inactive, member, 500)


# --- waive (FR-14, ADR-0021) -----------------------------------------------------


def test_waive_is_admin_only(clerk, member) -> None:
    fine = make_charge(member, EntryKind.FINE, 1500)
    with pytest.raises(PermissionDenied):
        services.waive(clerk, fine, 500, "Hastalık")
    assert LedgerEntry.objects.filter(kind="WAIVER").count() == 0


@pytest.mark.parametrize("reason", ["", "   "])
def test_tc87_waiver_needs_a_reason(admin, member, reason) -> None:
    fine = make_charge(member, EntryKind.FINE, 1500)
    before = _counts()
    with pytest.raises(RuleViolation, match="^Af için gerekçe zorunlu$"):
        services.waive(admin, fine, 500, reason)
    assert _counts() == before


def test_tc88_waiver_up_to_the_unpaid_part(clerk, admin, member) -> None:
    fine = make_charge(member, EntryKind.FINE, 1500)
    services.record_payment(clerk, member, 500)
    with pytest.raises(RuleViolation, match="^Af tutarı kalemin ödenmemiş kısmını aşamaz$"):
        services.waive(admin, fine, 1001, "Hastalık")
    waiver = services.waive(admin, fine, 1000, "Hastalık")
    assert _unpaid(fine) == 0
    assert list(
        Allocation.objects.filter(credit_entry=waiver).values_list("charge_entry_id", "amount_kurus")
    ) == [(fine.id, 1000)]
    assert (waiver.target_entry_id, waiver.reason) == (fine.id, "Hastalık")


def test_tc89_partial_waiver(admin, member) -> None:
    fine = make_charge(member, EntryKind.FINE, 1000)
    services.waive(admin, fine, 300, "Hastalık")
    assert _unpaid(fine) == 700
    assert services.member_balance(member) == 700


def test_tc90_waiver_target_must_be_an_open_charge(clerk, admin, member) -> None:
    fine = make_charge(member, EntryKind.FINE, 1500)
    payment = services.record_payment(clerk, member, 1500)
    before = _counts()
    with pytest.raises(RuleViolation, match="^Af tutarı kalemin ödenmemiş kısmını aşamaz$"):
        services.waive(admin, fine, 100, "Hastalık")
    with pytest.raises(RuleViolation, match="^Yalnız ceza ve bedel kalemleri affedilebilir$"):
        services.waive(admin, payment, 100, "Hastalık")
    assert _counts() == before


def test_waiver_amount_must_be_positive_and_is_audited(admin, member) -> None:
    fine = make_charge(member, EntryKind.FINE, 1500)
    with pytest.raises(RuleViolation, match="^Af tutarı 0,00 TL'den büyük olmalı$"):
        services.waive(admin, fine, 0, "Hastalık")
    waiver = services.waive(admin, fine, 500, "  Hastalık ")
    event = _audit(AuditAction.WAIVER)
    assert (event.actor, event.target_type, event.target_id) == (admin, "ledger_entry", waiver.id)
    assert event.details == {
        "amount_kurus": 500,
        "member_no": 1042,
        "target_entry_id": fine.id,
        "reason": "Hastalık",
    }


# --- cancel_unpaid and refund (FR-16, ADR-0020, ADR-0037, KL-26) -----------------


def test_tc92_cancel_unpaid_cancels_the_rest(clerk, member) -> None:
    fee = _found_lost_fee(member)
    services.record_payment(clerk, member, 2000)
    cancellation = services.cancel_unpaid(clerk, fee)
    assert cancellation is not None
    assert (cancellation.kind, cancellation.amount_kurus, cancellation.target_entry_id) == (
        "CANCELLATION",
        10000,
        fee.id,
    )
    assert cancellation.reason is None
    assert list(
        Allocation.objects.filter(credit_entry=cancellation).values_list(
            "charge_entry_id", "amount_kurus"
        )
    ) == [(fee.id, 10000)]
    assert services.refundable(fee) == 2000
    assert services.member_balance(member) == 0


def test_cancel_unpaid_returns_none_when_nothing_is_open(clerk, member) -> None:
    fee = _found_lost_fee(member, 1000)
    services.record_payment(clerk, member, 1000)
    before = _counts()
    assert services.cancel_unpaid(clerk, fee) is None
    assert _counts() == before


def test_cancel_unpaid_refuses_a_fine(clerk, member) -> None:
    fine = make_charge(member, EntryKind.FINE, 1000)
    with pytest.raises(ValueError):
        services.cancel_unpaid(clerk, fine)


def test_tc93_refund_is_balance_neutral_and_audited(clerk, admin, member) -> None:
    fee = _found_lost_fee(member)
    services.record_payment(clerk, member, 2000)
    services.cancel_unpaid(clerk, fee)
    refund = services.refund(admin, fee, 2000)
    assert (refund.kind, refund.amount_kurus, refund.target_entry_id) == ("REFUND", 2000, fee.id)
    assert not Allocation.objects.filter(credit_entry=refund).exists()
    assert services.member_balance(member) == 0
    assert services.refundable(fee) == 0
    event = _audit(AuditAction.REFUND)
    assert (event.actor, event.target_type, event.target_id) == (admin, "ledger_entry", refund.id)
    assert event.details == {"amount_kurus": 2000, "member_no": 1042, "target_entry_id": fee.id}


def test_tc94_refund_bounds(clerk, admin, member) -> None:
    fee = _found_lost_fee(member)
    services.record_payment(clerk, member, 2000)
    services.cancel_unpaid(clerk, fee)
    with pytest.raises(RuleViolation, match=f"^{PAID_MESSAGE}$"):
        services.refund(admin, fee, 2001)
    services.refund(admin, fee, 1500)
    with pytest.raises(RuleViolation, match=f"^{PAID_MESSAGE}$"):
        services.refund(admin, fee, 501)
    services.refund(admin, fee, 500)
    total = sum(LedgerEntry.objects.filter(kind="REFUND").values_list("amount_kurus", flat=True))
    assert total == 2000


def test_tc95_refund_needs_a_found_copy(clerk, admin, member) -> None:
    fee = _found_lost_fee(member, found=False)
    services.record_payment(clerk, member, 2000)
    fine = make_charge(member, EntryKind.FINE, 1000)
    before = _counts()
    with pytest.raises(RuleViolation, match=f"^{PRECONDITION_MESSAGE}$"):
        services.refund(admin, fee, 1000)
    with pytest.raises(RuleViolation, match=f"^{PRECONDITION_MESSAGE}$"):
        services.refund(admin, fine, 100)
    assert _counts() == before


def test_tc96_waived_part_is_not_refundable(clerk, admin, member) -> None:
    fee = _found_lost_fee(member)
    services.record_payment(clerk, member, 2000)
    services.waive(admin, fee, 1000, "İndirim")
    cancellation = services.cancel_unpaid(clerk, fee)
    assert cancellation is not None and cancellation.amount_kurus == 9000
    assert services.refundable(fee) == 2000


def test_refund_amount_must_be_positive_and_admin_only(clerk, admin, member) -> None:
    fee = _found_lost_fee(member)
    services.record_payment(clerk, member, 2000)
    with pytest.raises(RuleViolation, match="^Para iadesi tutarı 0,00 TL'den büyük olmalı$"):
        services.refund(admin, fee, 0)
    with pytest.raises(PermissionDenied):
        services.refund(clerk, fee, 100)


def test_tc270_refundable_is_payments_minus_refunds(clerk, admin, member) -> None:
    fee = _found_lost_fee(member)
    services.record_payment(clerk, member, 5000)
    services.record_payment(clerk, member, 3000)
    assert services.refundable(fee) == 8000
    services.refund(admin, fee, 3000)
    assert services.refundable(fee) == 5000


def test_tc270_refundable_is_zero_without_the_precondition(clerk, member) -> None:
    fee = _found_lost_fee(member, found=False)
    services.record_payment(clerk, member, 5000)
    assert services.refundable(fee) == 0


def test_tc271_damaged_or_unlinked_fee_is_not_refundable(clerk, admin, member) -> None:
    damaged_loan = make_loan(member, closed_on=date(2026, 11, 20), close_reason=CloseReason.DAMAGED)
    damaged = make_charge(member, EntryKind.FEE, 5000, loan=damaged_loan)
    unlinked = make_charge(member, EntryKind.FEE, 5000)
    services.record_payment(clerk, member, 10000)
    before = _counts()
    for fee in (damaged, unlinked):
        assert services.refundable(fee) == 0
        with pytest.raises(RuleViolation, match=f"^{PRECONDITION_MESSAGE}$"):
            services.refund(admin, fee, 100)
    assert _counts() == before


def test_tc272_fully_paid_fee_refund_bounds(clerk, admin, member) -> None:
    fee = _found_lost_fee(member)
    services.record_payment(clerk, member, 12000)
    with pytest.raises(RuleViolation, match=f"^{PAID_MESSAGE}$"):
        services.refund(admin, fee, 12001)
    services.refund(admin, fee, 12000)
    assert services.refundable(fee) == 0
    assert services.member_balance(member) == 0


# --- cancel_fee_manual (FR-16, ADR-0041, KL-30) -----------------------------------


def test_tc273_manual_cancellation_of_an_unlinked_fee(clerk, admin, member) -> None:
    fee = make_charge(member, EntryKind.FEE, 12000)
    services.record_payment(clerk, member, 4000)
    cancellation = services.cancel_fee_manual(admin, fee, "Nüsha bulundu")
    assert services.member_balance(member) == 0
    assert (cancellation.kind, cancellation.amount_kurus, cancellation.reason) == (
        "CANCELLATION",
        8000,
        "Nüsha bulundu",
    )
    event = _audit(AuditAction.CANCELLATION)
    assert (event.actor, event.target_type, event.target_id) == (
        admin,
        "ledger_entry",
        cancellation.id,
    )
    assert event.occurred_at is not None
    assert event.details == {
        "amount_kurus": 8000,
        "member_no": 1042,
        "target_entry_id": fee.id,
        "reason": "Nüsha bulundu",
    }
    with pytest.raises(RuleViolation, match=f"^{PRECONDITION_MESSAGE}$"):
        services.refund(admin, fee, 1000)


def test_tc274_manual_cancellation_refusals(clerk, admin, member) -> None:
    unlinked = make_charge(member, EntryKind.FEE, 5000)
    linked = _found_lost_fee(member, 5000, found=False)
    settled = make_charge(member, EntryKind.FEE, 1000)
    fine = make_charge(member, EntryKind.FINE, 1000)
    services.waive(admin, settled, 1000, "İndirim")
    before = _counts()
    for reason in ("", "   "):
        with pytest.raises(RuleViolation, match="^İptal için gerekçe zorunlu$"):
            services.cancel_fee_manual(admin, unlinked, reason)
    with pytest.raises(
        RuleViolation, match="^Bu bedel ödüncüne bağlı; nüshayı Bulundu olarak işaretleyin$"
    ):
        services.cancel_fee_manual(admin, linked, "Nüsha bulundu")
    with pytest.raises(RuleViolation, match="^Bedelin ödenmemiş kısmı yok$"):
        services.cancel_fee_manual(admin, settled, "Nüsha bulundu")
    with pytest.raises(RuleViolation, match="^Yalnız bedel kalemleri iptal edilebilir$"):
        services.cancel_fee_manual(admin, fine, "Nüsha bulundu")
    assert _counts() == before
    with pytest.raises(PermissionDenied):
        services.cancel_fee_manual(clerk, unlinked, "Nüsha bulundu")


# --- Balance, statement and invariants (FR-17, I1–I6, NFR-12) --------------------

_S3 = """
SELECT COALESCE(SUM(CASE WHEN kind IN ('FINE','FEE') THEN amount_kurus
                         WHEN kind IN ('PAYMENT','WAIVER','CANCELLATION') THEN -amount_kurus
                         ELSE 0 END), 0)
FROM ledger_entry WHERE member_id = %s
"""


def _s3(member) -> int:
    with connection.cursor() as cursor:
        cursor.execute(_S3, [member.pk])
        return cursor.fetchone()[0]


def _scenario(clerk, admin, member) -> None:
    """Fine, partial payment, waiver, fee, cancellation, refund; I1 after each step."""

    def check() -> None:
        entries = LedgerEntry.objects.filter(member=member).values_list("kind", "amount_kurus")
        assert balance(list(entries)) == _s3(member) == services.member_balance(member) >= 0

    loan = make_loan(member)
    fine = services.post_charge(clerk, member, loan, "FINE", 1500)
    check()
    services.record_payment(clerk, member, 500)
    check()
    services.waive(admin, fine, 500, "Hastalık")
    check()
    lost = make_loan(member, closed_on=date(2026, 11, 20), close_reason=CloseReason.LOST)
    fee = services.post_charge(admin, member, lost, "FEE", 12000)
    check()
    services.record_payment(clerk, member, 3000)
    check()
    type(lost).objects.filter(pk=lost.pk).update(copy_found_on=date(2026, 11, 25))
    fee = LedgerEntry.objects.get(pk=fee.pk)  # drop the cached loan
    services.cancel_unpaid(clerk, fee)
    check()
    services.refund(admin, fee, services.refundable(fee))
    check()


def test_tc100_balance_matches_s3_after_every_step(clerk, admin, member) -> None:
    _scenario(clerk, admin, member)
    assert services.member_balance(member) == 0


def test_tc101_existing_rows_never_change(clerk, admin, member) -> None:
    fine = make_charge(member, EntryKind.FINE, 2000)
    services.record_payment(clerk, member, 700)

    def snapshot(model) -> dict[int, dict]:
        return {row["id"]: row for row in model.objects.values()}

    entries, allocations = snapshot(LedgerEntry), snapshot(Allocation)
    _scenario(clerk, admin, member)
    assert {k: v for k, v in snapshot(LedgerEntry).items() if k in entries} == entries
    assert {k: v for k, v in snapshot(Allocation).items() if k in allocations} == allocations
    assert len(snapshot(LedgerEntry)) > len(entries)
    assert fine.pk in entries


def test_i6_model_refuses_update_and_delete(member) -> None:
    fine = make_charge(member, EntryKind.FINE, 2000)
    fine.amount_kurus = 1
    with pytest.raises(ValueError):
        fine.save()
    with pytest.raises(ValueError):
        fine.delete()


def test_tc102_integer_kurus_balance(clerk, member) -> None:
    for _ in range(3):
        make_charge(member, EntryKind.FINE, 500)
    services.record_payment(clerk, member, 1500)
    result = services.member_balance(member)
    assert result == 0 and type(result) is int
    from administration.money import format_tl

    assert format_tl(result) == "0,00 TL"


def test_statement_rows_in_order_with_labels(clerk, admin, member) -> None:
    fee = _found_lost_fee(member, 3000)
    services.record_payment(clerk, member, 1000)
    services.cancel_unpaid(clerk, fee)
    services.refund(admin, fee, 1000)
    rows = services.statement(member)
    assert [r.kind_label for r in rows] == ["Bedel", "Ödeme", "İptal", "Para iadesi"]
    fee_row = rows[0]
    assert (fee_row.unpaid_kurus, fee_row.refundable_kurus, fee_row.manually_cancellable) == (
        0,
        0,
        False,
    )
    assert rows[1].unpaid_kurus is None
    assert services.statement(make_member("Boş Üye")) == []


def test_get_entry_belongs_to_the_member(member) -> None:
    fine = make_charge(member, EntryKind.FINE, 1000)
    other = make_member("Başka Üye")
    assert services.get_entry(member, fine.id) == fine
    with pytest.raises(RuleViolation, match="^Kalem bulunamadı$"):
        services.get_entry(other, fine.id)
    with pytest.raises(RuleViolation, match="^Kalem bulunamadı$"):
        services.get_entry(member, None)


@pytest.mark.django_db(transaction=True)
def test_tc103_concurrent_payments_cannot_exceed_the_debt(file_db) -> None:
    clerk = make_staff("ali")
    member = make_member(member_no=7)
    make_charge(member, EntryKind.FINE, 1000)

    def pay():
        return services.record_payment(clerk, member, 600)

    results = run_parallel(pay, pay)
    accepted = [r for r in results if isinstance(r, LedgerEntry)]
    refused = [r for r in results if isinstance(r, RuleViolation)]
    assert len(accepted) == 1 and len(refused) == 1, results
    assert refused[0].message == "Ödeme tutarı borcu aşamaz"
    assert services.member_balance(member) == 400
