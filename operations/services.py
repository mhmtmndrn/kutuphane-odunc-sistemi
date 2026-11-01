"""Retention and anonymization (G15; FR-25, NFR-08, AC-25; ADR-0018,
ADR-0045, ADR-0055; KL-34).

Every record is handled in its own transaction (data-design §5): a failure
rolls back that record only, keeps the earlier ones and stops the run
(G14–G16 small decision 9). The job is idempotent: it only touches loans
that are still linked and members that are not yet anonymized, so the next
run continues where the last one stopped.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from administration.services import get_settings
from billing.models import LedgerEntry
from billing.services import member_balance
from circulation.models import Loan
from members.models import ConsentEvent, Member
from notifications.models import ReminderLog

from . import domain
from .domain import AnonymizeCounts

__all__ = ["AnonymizeCounts", "DeferredRow", "anonymize_expired", "deferred_members"]


@dataclass(frozen=True)
class DeferredRow:
    member_no: int
    full_name: str | None
    deactivated_on: date
    expires_on: date
    balance_kurus: int


def _expired_loan_ids(today: date, years: int) -> list[int]:
    # The date bound narrows the query; is_expired decides (29 February).
    rows = (
        Loan.objects.filter(
            member__isnull=False,
            closed_on__isnull=False,
            closed_on__lte=domain.add_years(today, -years),
        )
        .order_by("closed_on", "id")
        .values_list("id", "closed_on")
    )
    return [loan_id for loan_id, closed_on in rows if domain.is_expired(closed_on, years, today)]


def _expired_members(today: date, years: int) -> list[Member]:
    members = Member.objects.filter(
        is_active=False,
        anonymized_at__isnull=True,
        deactivated_on__lte=domain.add_years(today, -years),
    ).order_by("deactivated_on", "member_no")
    return [m for m in members if domain.is_expired(m.deactivated_on, years, today)]


def _clear_reminder_errors(loan_id: int) -> None:
    """ADR-0055: an SMTP error text may hold the member's e-mail address."""
    ReminderLog.objects.filter(loan_id=loan_id).update(error=None)


def _unlink_loan(loan_id: int) -> bool:
    """ADR-0018: unlink the member, count the loan in the member's archive
    counter and unlink the ledger entries, all in one transaction."""
    with transaction.atomic():
        member_id = Loan.objects.filter(pk=loan_id).values_list("member_id", flat=True).first()
        if member_id is None:
            return False
        Loan.objects.filter(pk=loan_id).update(member=None, member_unlinked_at=timezone.now())
        Member.objects.filter(pk=member_id).update(archived_loan_count=F("archived_loan_count") + 1)
        # Ledger entries are append-only (I6): queryset update, not save().
        LedgerEntry.objects.filter(loan_id=loan_id).update(loan=None)
        _clear_reminder_errors(loan_id)
    return True


def _anonymize_member(member_id: int) -> str | None:
    """ "deferred" when the member has debt (ADR-0045); otherwise clear the
    FR-01 personal fields and the consent history and return "anonymized".
    None if another run got there first."""
    with transaction.atomic():
        member = Member.objects.get(pk=member_id)
        if member.anonymized_at is not None:
            return None
        if member_balance(member) > 0:
            return "deferred"
        member.full_name = member.phone = member.email = None
        member.has_email_consent = False
        member.anonymized_at = timezone.now()
        # save() writes search_key = "" and phone_digits = NULL (ADR-0019).
        member.save()
        ConsentEvent.objects.filter(member=member).delete()
    return "anonymized"


def anonymize_expired(today: date) -> AnonymizeCounts:
    years = get_settings().retention_years
    loans = sum(_unlink_loan(loan_id) for loan_id in _expired_loan_ids(today, years))
    outcomes = [_anonymize_member(member.pk) for member in _expired_members(today, years)]
    members, deferred = outcomes.count("anonymized"), outcomes.count("deferred")
    return AnonymizeCounts(members=members, loans=loans, deferred=deferred)


@transaction.atomic
def deferred_members(today: date) -> list[DeferredRow]:
    """KL-34: expired, not anonymized members kept because of debt; oldest
    deactivation first."""
    years = get_settings().retention_years
    rows = []
    for member in _expired_members(today, years):
        balance = member_balance(member)
        if balance > 0:
            rows.append(
                DeferredRow(
                    member_no=member.member_no,
                    full_name=member.full_name,
                    deactivated_on=member.deactivated_on,
                    expires_on=domain.add_years(member.deactivated_on, years),
                    balance_kurus=balance,
                )
            )
    return rows
