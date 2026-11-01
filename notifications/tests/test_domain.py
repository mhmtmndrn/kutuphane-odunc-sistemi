"""Notification domain tests (G13): TC-173 and the pure helpers."""

from __future__ import annotations

from datetime import date

import pytest

from notifications import domain
from notifications.domain import ReminderCounts, ReminderKind

DUE = date(2026, 11, 16)


@pytest.mark.parametrize(
    ("today", "expected"),
    [
        (date(2026, 11, 13), None),
        (date(2026, 11, 14), ReminderKind.DUE_SOON),
        (date(2026, 11, 15), ReminderKind.DUE_SOON),
        (date(2026, 11, 16), ReminderKind.DUE_SOON),
        (date(2026, 11, 17), ReminderKind.OVERDUE_1),
        (date(2026, 11, 23), ReminderKind.OVERDUE_1),
        (date(2026, 11, 24), None),
    ],
)
def test_tc173_due_reminder_kind_windows(today: date, expected) -> None:
    assert domain.due_reminder_kind(DUE, today) == expected


def test_reminder_kind_values_match_the_schema() -> None:
    assert ReminderKind.values == ["DUE_SOON", "OVERDUE_1", "MANUAL"]


def test_due_ranges_cover_the_two_windows() -> None:
    # S6: DUE_SOON for due_on in [today, today+2], OVERDUE_1 for [today-7, today-1].
    ranges = domain.due_ranges(date(2026, 11, 16))
    assert ranges == {
        ReminderKind.DUE_SOON: (date(2026, 11, 16), date(2026, 11, 18)),
        ReminderKind.OVERDUE_1: (date(2026, 11, 9), date(2026, 11, 15)),
    }


@pytest.mark.parametrize(
    ("has_email", "has_consent", "expected"),
    [
        (False, False, "no_email"),
        (False, True, "no_email"),
        (True, False, "no_consent"),
        (True, True, None),
    ],
)
def test_contact_block(has_email: bool, has_consent: bool, expected) -> None:
    assert domain.contact_block(has_email=has_email, has_consent=has_consent) == expected


def test_outcome_labels() -> None:
    assert domain.OUTCOME_LABELS == {
        "sent": "gönderildi",
        "no_consent": "rıza yok",
        "no_email": "e-posta yok",
        "failed": "gönderilemedi",
        "not_overdue": "gecikmemiş",
    }


def test_counts_text() -> None:
    assert domain.counts_text(ReminderCounts(sent=1, failed=1, skipped=0)) == (
        "gönderilen=1, başarısız=1, atlanan=0"
    )


def test_error_text_is_type_and_message_cut_to_500() -> None:
    assert domain.error_text(OSError("timed out")) == "OSError: timed out"
    assert len(domain.error_text(ValueError("x" * 600))) == 500
