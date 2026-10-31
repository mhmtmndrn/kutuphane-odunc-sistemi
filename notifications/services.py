"""Reminders and the overdue list (plan G13: FR-18, FR-19, FR-20).

Sending follows data-design §5 and architecture §10: the e-mail goes out
first, then ``reminder_log`` is written in its own transaction. No
transaction is open during SMTP, so no database lock is held while the mail
server answers (G13 small decision 3; a deliberate exception to the single
``transaction.atomic()`` rule of plan §4.0). A crash between the two steps
can repeat one reminder; that risk was accepted (architecture §10).
"""

from __future__ import annotations

import smtplib
from dataclasses import dataclass
from datetime import date

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import IntegrityError, transaction
from django.db.models import Exists, OuterRef
from django.template.loader import render_to_string

from accounts.models import Role
from accounts.permissions import require_role
from administration import clock
from administration.errors import RuleViolation
from administration.services import get_settings
from circulation.models import Loan
from circulation.services import OverdueRow, overdue_loans
from members.models import Member

from . import domain
from .domain import ContactBlock, Outcome, ReminderCounts, ReminderKind
from .models import ReminderLog, ReminderStatus

# MANUAL reminders are sent for overdue loans and use the OVERDUE_1 text (KL-13).
_TEMPLATE = {
    ReminderKind.DUE_SOON: "due_soon",
    ReminderKind.OVERDUE_1: "overdue",
    ReminderKind.MANUAL: "overdue",
}
# G13 small decision 5: anything else is a bug and propagates. A timeout
# (EMAIL_TIMEOUT, ADR-0052) is an OSError.
_SEND_ERRORS = (smtplib.SMTPException, OSError)


def _block(member: Member | None) -> ContactBlock | None:
    if member is None:  # unlinked loans are closed; kept for safety (ADR-0018)
        return "no_email"
    return domain.contact_block(has_email=bool(member.email), has_consent=member.has_email_consent)


# --- Overdue list (FR-20) -------------------------------------------------------


@dataclass(frozen=True)
class OverdueEntry:
    row: OverdueRow
    block: ContactBlock | None  # why no reminder can be sent, or None


def overdue_list(today: date) -> list[OverdueEntry]:
    """``overdue_loans(today)`` with the "rıza yok" / "e-posta yok" mark of each row."""
    return [OverdueEntry(row, _block(row.loan.member)) for row in overdue_loans(today)]


# --- Sending ----------------------------------------------------------------------


def _message(loan: Loan, kind: ReminderKind, library_name: str) -> EmailMessage:
    """The KL-13 e-mail. The fine rates are the loan's copies (ADR-0023)."""
    context = {
        "library_name": library_name,
        "title": loan.copy.book.title,
        "due_on": loan.due_on,
        "daily_fine": loan.daily_fine_kurus,
        "fine_cap": loan.fine_cap_kurus,
    }
    name = _TEMPLATE[kind]
    subject = render_to_string(f"notifications/email/{name}_subject.txt", context)
    body = render_to_string(f"notifications/email/{name}_body.txt", context)
    # A header must be one line.
    subject = " ".join(subject.splitlines()).strip()
    return EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [loan.member.email])


def _send(message: EmailMessage) -> None:
    message.send()


def _attempt(loan: Loan, kind: ReminderKind, library_name: str) -> tuple[str, str | None]:
    """Send one reminder; returns the log status and error text."""
    try:
        _send(_message(loan, kind, library_name))
    except _SEND_ERRORS as exc:
        return ReminderStatus.FAILED, domain.error_text(exc)
    return ReminderStatus.SENT, None


def _log(loan: Loan, kind: ReminderKind, status: str, error: str | None, actor=None) -> None:
    """Write the attempt in its own transaction, with the due date it was for."""
    with transaction.atomic():
        ReminderLog.objects.create(
            loan=loan,
            kind=kind,
            status=status,
            error=error,
            triggered_by=actor,
            due_on=loan.due_on,
        )


# --- Automatic reminders (FR-18, S6) ---------------------------------------------


def _candidates(today: date) -> list[tuple[Loan, ReminderKind]]:
    """S6: open loans in a window whose member is active, has an e-mail
    address and consent, and that have no SENT log of that kind for the
    loan's current due date (ADR-0039)."""
    candidates: list[tuple[Loan, ReminderKind]] = []
    for kind, (first, last) in domain.due_ranges(today).items():
        sent = ReminderLog.objects.filter(
            loan=OuterRef("pk"), kind=kind, due_on=OuterRef("due_on"), status=ReminderStatus.SENT
        )
        loans = (
            Loan.objects.filter(
                closed_on__isnull=True,
                due_on__range=(first, last),
                member__is_active=True,
                member__has_email_consent=True,
                member__email__isnull=False,
            )
            .exclude(member__email="")
            .exclude(Exists(sent))
            .select_related("member", "copy__book")
            .order_by("due_on", "id")
        )
        candidates.extend((loan, kind) for loan in loans)
    return candidates


def send_due_reminders(today: date) -> ReminderCounts:
    """Send the DUE_SOON and OVERDUE_1 reminders due on ``today``.

    A unique-index violation on the log means another run already sent this
    reminder; it counts as sent and is reported as skipped (data-design §5).
    SMTP errors are logged as FAILED and retried while the window lasts
    (phase 3 small decision 7).
    """
    library_name = get_settings().library_name
    sent = failed = skipped = 0
    for loan, kind in _candidates(today):
        status, error = _attempt(loan, kind, library_name)
        try:
            _log(loan, kind, status, error)
        except IntegrityError:
            skipped += 1
            continue
        if status == ReminderStatus.SENT:
            sent += 1
        else:
            failed += 1
    return ReminderCounts(sent=sent, failed=failed, skipped=skipped)


# --- Manual reminders (FR-19, KL-28) ----------------------------------------------


@dataclass(frozen=True)
class ManualResult:
    loan_id: int
    outcome: Outcome
    # For the message of the overdue screen (G13 small decision 1).
    member_no: int | None
    full_name: str | None
    title: str


def _manual_outcome(actor, loan: Loan, today: date, library_name: str) -> Outcome:
    if not loan.is_open or loan.due_on >= today:
        return "not_overdue"
    block = _block(loan.member)
    if block is not None:
        return block
    status, error = _attempt(loan, ReminderKind.MANUAL, library_name)
    _log(loan, ReminderKind.MANUAL, status, error, actor)
    return "sent" if status == ReminderStatus.SENT else "failed"


@require_role(Role.CLERK)
def send_manual_reminders(actor, loan_ids: list[int]) -> list[ManualResult]:
    """Send a MANUAL reminder for each selected loan, in the given order.

    No repeat guard (KL-28); ``triggered_by`` records the staff member and no
    audit event is written. An unknown id sends nothing: "Ödünç bulunamadı".
    """
    today = clock.today()
    ids = list(dict.fromkeys(loan_ids))
    loans = Loan.objects.select_related("member", "copy__book").in_bulk(ids)
    if len(loans) != len(ids):
        raise RuleViolation("Ödünç bulunamadı")
    library_name = get_settings().library_name
    results = []
    for loan_id in ids:
        loan = loans[loan_id]
        member = loan.member
        results.append(
            ManualResult(
                loan_id=loan_id,
                outcome=_manual_outcome(actor, loan, today, library_name),
                member_no=member.member_no if member else None,
                full_name=member.full_name if member else None,
                title=loan.copy.book.title,
            )
        )
    return results
