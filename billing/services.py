"""Ledger services (plan G09). Each public function is one transaction.

Writes start with ``require_role`` and end with the audit record (plan §4.0).
``post_charge`` and ``cancel_unpaid`` are internal: they run inside the
caller's transaction (check-in, lost or damaged, found), and the caller
writes the audit event of its own operation; ``post_charge`` also writes
``FEE`` (plan G09).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from django.db import transaction
from django.db.models import Case, F, IntegerField, Q, Sum, Value, When
from django.db.models.functions import Coalesce

from accounts.models import Role
from accounts.permissions import require_role
from administration.audit import AuditAction, record_audit
from administration.errors import RuleViolation

from .domain import OpenCharge, allocate_fifo
from .models import Allocation, EntryKind, LedgerEntry

_CHARGES = (EntryKind.FINE, EntryKind.FEE)
_CREDITS = (EntryKind.PAYMENT, EntryKind.WAIVER, EntryKind.CANCELLATION)
_FIFO_ORDER = ("created_at", "id")  # ADR-0017

REFUND_PRECONDITION = "Para iadesi yalnız bulunan kayıp nüshanın bedeli için yapılabilir"
REFUND_TOO_MUCH = "Para iadesi, ödenmiş ve henüz iade edilmemiş tutarı aşamaz"


def _entry(actor, member, kind: EntryKind, amount: int, **fields) -> LedgerEntry:
    return LedgerEntry.objects.create(
        member=member, kind=kind, amount_kurus=amount, created_by=actor, **fields
    )


def _audit(actor, action: AuditAction, entry: LedgerEntry, **extra) -> None:
    """KL-15: target ``ledger_entry``; details never name the loan."""
    details = {"amount_kurus": entry.amount_kurus, "member_no": entry.member.member_no, **extra}
    record_audit(actor, action, "ledger_entry", entry.pk, details)


def _paid_or_settled(charge: LedgerEntry) -> int:
    total = charge.charge_allocations.aggregate(total=Sum("amount_kurus"))["total"]
    return total or 0


def _unpaid(charge: LedgerEntry) -> int:
    """I4: amount − Σ allocations."""
    return charge.amount_kurus - _paid_or_settled(charge)


def _require_positive(amount: int, message: str) -> None:
    if amount <= 0:
        raise RuleViolation(message)


def _clean_reason(reason: str | None, message: str) -> str:
    reason = (reason or "").strip()
    if not reason:
        raise RuleViolation(message)
    return reason


# --- Charges -----------------------------------------------------------------


@require_role(Role.CLERK)
@transaction.atomic
def post_charge(actor, member, loan, kind: Literal["FINE", "FEE"], amount: int) -> LedgerEntry:
    """Internal: a FINE (check-in, lost, damaged) or FEE (lost, damaged)."""
    if kind not in _CHARGES:
        raise ValueError(f"post_charge writes FINE or FEE, not {kind!r}")
    if amount <= 0:
        raise ValueError("a charge must be positive")
    entry = _entry(actor, member, EntryKind(kind), amount, loan=loan)
    if kind == EntryKind.FEE:
        _audit(actor, AuditAction.FEE, entry)
    return entry


# --- Payment (FR-13, ADR-0017) ------------------------------------------------


@require_role(Role.CLERK)
@transaction.atomic
def record_payment(actor, member, amount: int) -> LedgerEntry:
    """Spread the payment FIFO over the open charges; never above the debt (I1)."""
    _require_positive(amount, "Ödeme tutarı 0,00 TL'den büyük olmalı")
    charges = open_charges(member)
    if amount > sum(charge.unpaid for charge in charges):
        raise RuleViolation("Ödeme tutarı borcu aşamaz")
    payment = _entry(actor, member, EntryKind.PAYMENT, amount)
    Allocation.objects.bulk_create(
        [
            Allocation(credit_entry=payment, charge_entry_id=charge_id, amount_kurus=part)
            for charge_id, part in allocate_fifo(charges, amount)
        ]
    )
    _audit(actor, AuditAction.PAYMENT, payment)
    return payment


# --- Waiver (FR-14, ADR-0021) -------------------------------------------------


@require_role(Role.ADMIN)
@transaction.atomic
def waive(actor, charge: LedgerEntry, amount: int, reason: str) -> LedgerEntry:
    """A targeted waiver: one allocation to the chosen charge."""
    reason = _clean_reason(reason, "Af için gerekçe zorunlu")
    if charge.kind not in _CHARGES:
        raise RuleViolation("Yalnız ceza ve bedel kalemleri affedilebilir")
    _require_positive(amount, "Af tutarı 0,00 TL'den büyük olmalı")
    if amount > _unpaid(charge):
        raise RuleViolation("Af tutarı kalemin ödenmemiş kısmını aşamaz")
    waiver = _entry(
        actor, charge.member, EntryKind.WAIVER, amount, target_entry=charge, reason=reason
    )
    Allocation.objects.create(credit_entry=waiver, charge_entry=charge, amount_kurus=amount)
    _audit(actor, AuditAction.WAIVER, waiver, target_entry_id=charge.pk, reason=reason)
    return waiver


# --- Cancellation (FR-16, ADR-0020, ADR-0041) ---------------------------------


def _cancel(actor, fee: LedgerEntry, amount: int, reason: str | None) -> LedgerEntry:
    cancellation = _entry(
        actor, fee.member, EntryKind.CANCELLATION, amount, target_entry=fee, reason=reason
    )
    Allocation.objects.create(credit_entry=cancellation, charge_entry=fee, amount_kurus=amount)
    return cancellation


@require_role(Role.CLERK)
@transaction.atomic
def cancel_unpaid(actor, fee: LedgerEntry) -> LedgerEntry | None:
    """Internal (``mark_found``): cancel the fee's unpaid part; ``None`` if 0.

    The caller's COPY_FOUND event is the audit record (plan §11, G09).
    """
    if fee.kind != EntryKind.FEE:
        raise ValueError("only a FEE is cancelled when its copy is found")
    unpaid = _unpaid(fee)
    if unpaid == 0:
        return None
    return _cancel(actor, fee, unpaid, None)


@require_role(Role.ADMIN)
@transaction.atomic
def cancel_fee_manual(actor, fee: LedgerEntry, reason: str) -> LedgerEntry:
    """ADR-0041: an unlinked fee's whole unpaid part, with a reason."""
    if fee.kind != EntryKind.FEE:
        raise RuleViolation("Yalnız bedel kalemleri iptal edilebilir")
    reason = _clean_reason(reason, "İptal için gerekçe zorunlu")
    if fee.loan_id is not None:
        raise RuleViolation("Bu bedel ödüncüne bağlı; nüshayı Bulundu olarak işaretleyin")
    unpaid = _unpaid(fee)
    if unpaid == 0:
        raise RuleViolation("Bedelin ödenmemiş kısmı yok")
    cancellation = _cancel(actor, fee, unpaid, reason)
    _audit(actor, AuditAction.CANCELLATION, cancellation, target_entry_id=fee.pk, reason=reason)
    return cancellation


# --- Refund (FR-16, ADR-0020, ADR-0027, ADR-0037, KL-26) -----------------------


def _refund_allowed(fee: LedgerEntry) -> bool:
    """I5: a FEE whose loan closed as LOST and whose copy was found."""
    loan = fee.loan
    return (
        fee.kind == EntryKind.FEE
        and loan is not None
        and loan.close_reason == "LOST"
        and loan.copy_found_on is not None
    )


@transaction.atomic
def refundable(fee: LedgerEntry) -> int:
    """KL-26: PAYMENT allocations to the fee − its REFUNDs; 0 without I5."""
    if not _refund_allowed(fee):
        return 0
    paid = fee.charge_allocations.filter(credit_entry__kind=EntryKind.PAYMENT).aggregate(
        total=Sum("amount_kurus")
    )["total"] or 0
    refunded = fee.targeted_by.filter(kind=EntryKind.REFUND).aggregate(
        total=Sum("amount_kurus")
    )["total"] or 0
    return paid - refunded


@require_role(Role.ADMIN)
@transaction.atomic
def refund(actor, fee: LedgerEntry, amount: int) -> LedgerEntry:
    """A balance-neutral REFUND entry; no allocation (ADR-0020)."""
    if not _refund_allowed(fee):
        raise RuleViolation(REFUND_PRECONDITION)
    _require_positive(amount, "Para iadesi tutarı 0,00 TL'den büyük olmalı")
    if amount > refundable(fee):
        raise RuleViolation(REFUND_TOO_MUCH)
    entry = _entry(actor, fee.member, EntryKind.REFUND, amount, target_entry=fee)
    _audit(actor, AuditAction.REFUND, entry, target_entry_id=fee.pk)
    return entry


# --- Reads (S3, S4, FR-17) ---------------------------------------------------


@transaction.atomic
def member_balance(member) -> int:
    """S3: one aggregate over the member's entries."""
    signed = Case(
        When(kind__in=_CHARGES, then=F("amount_kurus")),
        When(kind__in=_CREDITS, then=-F("amount_kurus")),
        default=Value(0),
        output_field=IntegerField(),
    )
    total = LedgerEntry.objects.filter(member=member).aggregate(
        total=Coalesce(Sum(signed), Value(0))
    )["total"]
    return int(total)


@transaction.atomic
def open_charges(member) -> list[OpenCharge]:
    """S4: charges with an unpaid part, oldest first (created_at, id)."""
    rows = (
        LedgerEntry.objects.filter(member=member, kind__in=_CHARGES)
        .annotate(
            settled=Coalesce(Sum("charge_allocations__amount_kurus"), Value(0)),
            unpaid=F("amount_kurus") - F("settled"),
        )
        .filter(unpaid__gt=0)
        .order_by(*_FIFO_ORDER)
        .values_list("id", "unpaid")
    )
    return [OpenCharge(entry_id, unpaid) for entry_id, unpaid in rows]


@dataclass(frozen=True)
class StatementRow:
    """One ledger entry on the statement screen (FR-17).

    ``unpaid_kurus`` is set for FINE and FEE only. ``refundable_kurus`` and
    ``manually_cancellable`` decide which admin forms the row gets (KL-26,
    ADR-0041).
    """

    entry_id: int
    created_at: datetime
    kind: str
    kind_label: str
    amount_kurus: int
    staff_name: str
    reason: str | None
    target_entry_id: int | None
    unpaid_kurus: int | None
    refundable_kurus: int
    manually_cancellable: bool


@transaction.atomic
def statement(member) -> list[StatementRow]:
    """Every entry, oldest first (created_at, id)."""
    entries = (
        LedgerEntry.objects.filter(member=member)
        .select_related("created_by", "loan")
        .annotate(settled=Coalesce(Sum("charge_allocations__amount_kurus"), Value(0)))
        .order_by(*_FIFO_ORDER)
    )
    rows = []
    for entry in entries:
        is_charge = entry.kind in _CHARGES
        unpaid = entry.amount_kurus - entry.settled if is_charge else None
        rows.append(
            StatementRow(
                entry_id=entry.pk,
                created_at=entry.created_at,
                kind=entry.kind,
                kind_label=entry.get_kind_display(),
                amount_kurus=entry.amount_kurus,
                staff_name=entry.created_by.first_name or entry.created_by.get_username(),
                reason=entry.reason,
                target_entry_id=entry.target_entry_id,
                unpaid_kurus=unpaid,
                refundable_kurus=refundable(entry) if entry.kind == EntryKind.FEE else 0,
                manually_cancellable=(
                    entry.kind == EntryKind.FEE and entry.loan_id is None and bool(unpaid)
                ),
            )
        )
    return rows


@transaction.atomic
def loan_fee(loan) -> LedgerEntry | None:
    """The FEE written when the loan closed as lost or damaged, if any."""
    return (
        LedgerEntry.objects.select_related("member", "loan")
        .filter(loan=loan, kind=EntryKind.FEE)
        .order_by("id")
        .first()
    )


@transaction.atomic
def get_entry(member, entry_id: int | None) -> LedgerEntry:
    """The member's entry by id; a form's hidden id cannot reach another member."""
    entry = (
        LedgerEntry.objects.select_related("member", "loan").filter(member=member, pk=entry_id).first()
        if entry_id is not None
        else None
    )
    if entry is None:
        raise RuleViolation("Kalem bulunamadı")
    return entry
