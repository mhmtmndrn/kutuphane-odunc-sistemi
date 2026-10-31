"""Circulation services (plan G11, G12). Each public function is one transaction.

Every write runs in one IMMEDIATE transaction (ADR-0002, data-design §5): the
reads that decide a blocker and the writes they allow cannot interleave with
another desk's request. "Today" comes from ``administration.clock`` only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from django.db import IntegrityError, transaction
from django.db.models import Q

from accounts.models import Role
from accounts.permissions import require_role
from administration import clock
from administration.errors import RuleViolation
from administration.money import format_tl
from administration.services import closed_dates, closed_day_predicate, get_settings
from billing import services as billing
from catalog.models import Copy, CopyStatus
from catalog.services import find_copy, search_books
from members import services as members
from members.models import Member

from . import domain
from .domain import Blocker, CheckoutState, RenewState
from .models import CloseReason, Loan

# --- Reads ----------------------------------------------------------------------


def _open_loans(member: Member):
    return (
        Loan.objects.filter(member=member, closed_on__isnull=True)
        .select_related("copy__book")
        .order_by("due_on", "id")
    )


@transaction.atomic
def open_loans(member: Member) -> list[Loan]:
    """The member's open loans, earliest due date first."""
    return list(_open_loans(member))


def _checkout_state(member: Member, copy_status: str, today: date) -> CheckoutState:
    """S2 and S3 from the database, with the current settings."""
    settings = get_settings()
    loans = Loan.objects.filter(member=member, closed_on__isnull=True)
    return CheckoutState(
        member_active=member.is_active,
        open_loans=loans.count(),
        max_open_loans=settings.max_open_loans,
        has_overdue=loans.filter(due_on__lt=today).exists(),
        balance_kurus=billing.member_balance(member),
        debt_threshold_kurus=settings.debt_threshold_kurus,
        copy_status=copy_status,
    )


@dataclass(frozen=True)
class MemberStatus:
    """The checkout screen's member panel (FR-08, FR-11).

    ``blockers`` are the member's own ones: every blocker but the copy's.
    """

    member: Member
    open_loans: list[Loan]
    balance_kurus: int
    blockers: list[Blocker]


@transaction.atomic
def member_status(member_no: int, today: date) -> MemberStatus:
    member = members.member_by_no(member_no)
    state = _checkout_state(member, CopyStatus.ON_SHELF, today)
    return MemberStatus(
        member=member,
        open_loans=open_loans(member),
        balance_kurus=state.balance_kurus,
        blockers=domain.checkout_blockers(state),
    )


@dataclass(frozen=True)
class CheckoutPreview:
    copy: Copy
    due_on: date
    blockers: list[Blocker]


@transaction.atomic
def preview_checkout(member_no: int, barcode: str, today: date) -> CheckoutPreview:
    """The copy, the due date and every blocker, without writing anything.

    Raises ``NoOpenDayError`` when no due date exists (ADR-0028).
    """
    member = members.member_by_no(member_no)
    copy = find_copy(barcode.strip())
    blockers = domain.checkout_blockers(_checkout_state(member, copy.status, today))
    due_on = domain.due_date(today, get_settings().loan_period_days, closed_day_predicate())
    return CheckoutPreview(copy=copy, due_on=due_on, blockers=blockers)


@transaction.atomic
def copies_matching(q: str, status: str) -> list[Copy]:
    """FR-11 manual choice: the copies in ``status`` of the books that
    ``search_books(q)`` finds (at most 50 books), by barcode."""
    books = search_books(q)
    return list(
        Copy.objects.filter(book__in=books, status=status)
        .select_related("book")
        .order_by("barcode")
    )


@transaction.atomic
def get_loan(loan_id: int) -> Loan | None:
    return Loan.objects.select_related("member", "copy__book").filter(pk=loan_id).first()


# --- Check-out, check-in, renewal (FR-07…FR-12) ---------------------------------


def _set_status(copy: Copy, status: str) -> None:
    copy.status = status
    copy.save(update_fields=["status"])


@require_role(Role.CLERK)
@transaction.atomic
def check_out(actor, member_no: int, barcode: str) -> Loan:
    """Re-evaluate every blocker inside the transaction; on any, refuse with
    the messages joined by "; " (KL-6). The fine rate is copied (ADR-0023)."""
    today = clock.today()
    member = members.member_by_no(member_no)
    copy = find_copy(barcode.strip())
    blockers = domain.checkout_blockers(_checkout_state(member, copy.status, today))
    if blockers:
        raise RuleViolation("; ".join(blocker.value for blocker in blockers))
    settings = get_settings()
    due_on = domain.due_date(today, settings.loan_period_days, closed_day_predicate())
    domain.check_transition(copy.status, CopyStatus.ON_LOAN)
    try:
        with transaction.atomic():
            loan = Loan.objects.create(
                copy=copy,
                member=member,
                loaned_on=today,
                due_on=due_on,
                daily_fine_kurus=settings.daily_fine_kurus,
                fine_cap_kurus=settings.fine_cap_kurus,
                created_by=actor,
            )
    except IntegrityError:
        # The partial unique index is the second guard (data-design §5).
        raise RuleViolation(Blocker.COPY_NOT_ON_SHELF.value) from None
    _set_status(copy, CopyStatus.ON_LOAN)
    return loan


def _open_loan_of(copy: Copy) -> Loan | None:
    return (
        Loan.objects.select_related("member", "copy__book")
        .filter(copy=copy, closed_on__isnull=True)
        .first()
    )


def _accrued_fine(loan: Loan, on: date, closed: frozenset[date]) -> int:
    days = domain.late_days(loan.due_on, on, closed)
    return domain.fine(days, loan.daily_fine_kurus, loan.fine_cap_kurus)


def _close(actor, loan: Loan, reason: str, today: date) -> int:
    """Close the loan and write its accrued FINE, if any (ADR-0040, KL-29)."""
    fine_kurus = _accrued_fine(loan, today, closed_dates())
    loan.closed_on = today
    loan.close_reason = reason
    loan.closed_by = actor
    loan.save(update_fields=["closed_on", "close_reason", "closed_by"])
    if fine_kurus > 0:
        billing.post_charge(actor, loan.member, loan, "FINE", fine_kurus)
    return fine_kurus


@dataclass(frozen=True)
class CheckInResult:
    loan: Loan
    fine_kurus: int


@require_role(Role.CLERK)
@transaction.atomic
def check_in(actor, barcode: str) -> CheckInResult:
    today = clock.today()
    copy = find_copy(barcode.strip())
    loan = _open_loan_of(copy)
    if loan is None:
        raise RuleViolation("Bu nüshanın açık ödüncü yok")
    domain.check_transition(copy.status, CopyStatus.ON_SHELF)
    fine_kurus = _close(actor, loan, CloseReason.RETURNED, today)
    _set_status(copy, CopyStatus.ON_SHELF)
    return CheckInResult(loan=loan, fine_kurus=fine_kurus)


@require_role(Role.CLERK)
@transaction.atomic
def renew(actor, loan_id: int) -> Loan:
    """``renewed_on = today``; the new due date runs from the current one
    (phase 1 small decision 3); the fine rate is kept (phase 3 small decision 5)."""
    today = clock.today()
    loan = Loan.objects.select_related("member", "copy__book").filter(pk=loan_id).first()
    if loan is None:
        raise RuleViolation("Ödünç bulunamadı")
    if not loan.is_open:
        raise RuleViolation("Ödünç kapanmış")
    state = RenewState(
        renewed=loan.renewed_on is not None,
        due_on=loan.due_on,
        today=today,
        balance_kurus=billing.member_balance(loan.member),
    )
    blockers = domain.renew_blockers(state)
    if blockers:
        raise RuleViolation("; ".join(blocker.value for blocker in blockers))
    loan.due_on = domain.renewed_due_date(
        loan.due_on, get_settings().loan_period_days, closed_day_predicate()
    )
    loan.renewed_on = today
    loan.save(update_fields=["due_on", "renewed_on"])
    return loan


# --- Deactivation (FR-02, KL-22) ------------------------------------------------


@require_role(Role.CLERK)
@transaction.atomic
def deactivate_member(actor, member: Member, confirm_debt: bool) -> None:
    """Refuse an anonymized or already inactive member first, so the retention
    start ``deactivated_on`` is never overwritten (plan §11, user decision
    2026-11-01); then open loans; a debt needs ``confirm_debt``."""
    if member.is_anonymized:
        raise RuleViolation("Anonimleştirilmiş üye pasifleştirilemez")
    if not member.is_active:
        raise RuleViolation("Üye zaten pasif")
    if Loan.objects.filter(member=member, closed_on__isnull=True).exists():
        raise RuleViolation("Açık ödüncü olan üye pasifleştirilemez")
    balance = billing.member_balance(member)
    if balance > 0 and not confirm_debt:
        raise RuleViolation(f"Üyenin {format_tl(balance)} borcu var; onaylayarak pasifleştirin")
    members.set_inactive(actor, member)


# --- Overdue list (FR-20, S5) ---------------------------------------------------


@dataclass(frozen=True)
class OverdueRow:
    loan: Loan
    member_no: int | None
    full_name: str | None
    phone: str | None
    title: str
    due_on: date
    late_days: int
    accrued_fine: int


@transaction.atomic
def overdue_loans(today: date) -> list[OverdueRow]:
    """Open loans past their due date, oldest due date first (KL-11)."""
    closed = closed_dates()
    loans = (
        Loan.objects.filter(Q(closed_on__isnull=True), due_on__lt=today)
        .select_related("member", "copy__book")
        .order_by("due_on", "id")
    )
    rows = []
    for loan in loans:
        member = loan.member
        rows.append(
            OverdueRow(
                loan=loan,
                member_no=member.member_no if member else None,
                full_name=member.full_name if member else None,
                phone=member.phone if member else None,
                title=loan.copy.book.title,
                due_on=loan.due_on,
                late_days=domain.late_days(loan.due_on, today, closed),
                accrued_fine=_accrued_fine(loan, today, closed),
            )
        )
    return rows
