"""Reminder rules (FR-18, FR-19; phase 3 small decisions 6 and 7). Pure: no ORM,
no HTTP and no clock; "today" is passed in (phase 4 small decision 9)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

from django.db.models import TextChoices

# Reminder windows (phase 3 small decision 6, architecture §4.3).
DUE_SOON_DAYS_BEFORE = 2
OVERDUE_1_FIRST_DAY = 1
OVERDUE_1_LAST_DAY = 7

ERROR_MAX_LENGTH = 500  # reminder_log.error varchar(500)


class ReminderKind(TextChoices):
    DUE_SOON = "DUE_SOON", "Son tarih yaklaşıyor"
    OVERDUE_1 = "OVERDUE_1", "Gecikme"
    MANUAL = "MANUAL", "Elle"


Outcome = Literal["sent", "no_consent", "no_email", "failed", "not_overdue"]
ContactBlock = Literal["no_email", "no_consent"]

# Labels of the manual outcomes (plan G13; G13 small decision 1).
OUTCOME_LABELS: dict[str, str] = {
    "sent": "gönderildi",
    "no_consent": "rıza yok",
    "no_email": "e-posta yok",
    "failed": "gönderilemedi",
    "not_overdue": "gecikmemiş",
}


@dataclass(frozen=True)
class ReminderCounts:
    sent: int
    failed: int
    skipped: int


def due_reminder_kind(due_on: date, today: date) -> ReminderKind | None:
    """DUE_SOON for today ∈ [due−2, due], OVERDUE_1 for today ∈ [due+1, due+7]."""
    days_after = (today - due_on).days
    if -DUE_SOON_DAYS_BEFORE <= days_after <= 0:
        return ReminderKind.DUE_SOON
    if OVERDUE_1_FIRST_DAY <= days_after <= OVERDUE_1_LAST_DAY:
        return ReminderKind.OVERDUE_1
    return None


def due_ranges(today: date) -> dict[ReminderKind, tuple[date, date]]:
    """The ``due_on`` range (inclusive) of each automatic kind on ``today`` (S6)."""
    return {
        ReminderKind.DUE_SOON: (today, today + timedelta(days=DUE_SOON_DAYS_BEFORE)),
        ReminderKind.OVERDUE_1: (
            today - timedelta(days=OVERDUE_1_LAST_DAY),
            today - timedelta(days=OVERDUE_1_FIRST_DAY),
        ),
    }


def contact_block(*, has_email: bool, has_consent: bool) -> ContactBlock | None:
    """Why a member cannot get a reminder e-mail, or None (FR-03, FR-19)."""
    if not has_email:
        return "no_email"
    if not has_consent:
        return "no_consent"
    return None


def counts_text(counts: ReminderCounts) -> str:
    """The command output and ``job_run.detail`` (KL-23)."""
    return f"gönderilen={counts.sent}, başarısız={counts.failed}, atlanan={counts.skipped}"


def error_text(exc: BaseException) -> str:
    """``reminder_log.error`` (G13 small decision 5)."""
    return f"{type(exc).__name__}: {exc}"[:ERROR_MAX_LENGTH]
