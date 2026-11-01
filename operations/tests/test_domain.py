"""Operations domain tests (G14): backup and export names, retention (KL-14,
KL-24, TC-187 and TC-299 rules), the newest backup and the passphrase text."""

from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from operations import domain


def test_backup_and_export_names() -> None:
    assert domain.backup_name(date(2026, 11, 2)) == "library-20261102.sqlite3"
    assert domain.export_name(date(2026, 11, 2)) == "library-export-20261102.libx"


def test_tc187_backups_to_delete_keeps_thirty_days() -> None:
    names = [
        "library-20261201.sqlite3",  # run_on − 30
        "library-20261130.sqlite3",  # run_on − 31
        "library-20261231.sqlite3",
        "notlar.txt",
        "library-20261340.sqlite3",  # not a date
        "library-20261130.sqlite3.tmp",
    ]
    assert domain.backups_to_delete(names, date(2026, 12, 31)) == ["library-20261130.sqlite3"]


def test_tc299_exports_to_delete_keeps_eight_weeks() -> None:
    names = [
        "library-export-20261105.libx",  # run_on − 56
        "library-export-20261104.libx",  # run_on − 57
        "eski.libx",
        "library-20261001.sqlite3",
    ]
    assert domain.exports_to_delete(names, date(2026, 12, 31)) == ["library-export-20261104.libx"]


def test_keep_days_is_a_parameter() -> None:
    names = ["library-20261230.sqlite3", "library-20261229.sqlite3"]
    assert domain.backups_to_delete(names, date(2026, 12, 31), keep_days=1) == [
        "library-20261229.sqlite3"
    ]


def test_latest_backup_by_name_date() -> None:
    names = [
        "library-20261102.sqlite3",
        "library-20261101.sqlite3",
        "library-20261103.sqlite3.tmp",
        "library-export-20261109.libx",
        "notlar.txt",
    ]
    assert domain.latest_backup(names) == "library-20261102.sqlite3"
    assert domain.latest_backup(["notlar.txt"]) is None
    assert domain.latest_backup([]) is None


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("gizli\n", "gizli"),
        ("gizli\r\n", "gizli"),
        ("gizli", "gizli"),
        ("gizli\n\n", "gizli\n"),
        (" gizli parola ", " gizli parola "),
    ],
)
def test_passphrase_drops_one_trailing_line_end(text: str, expected: str) -> None:
    assert domain.passphrase_from_text(text) == expected


@pytest.mark.parametrize("text", ["", "\n", "\r\n"])
def test_empty_passphrase_is_an_error(text: str) -> None:
    with pytest.raises(ValueError):
        domain.passphrase_from_text(text)


# --- G15: retention dates (phase 3 small decision 4) -----------------------------


def test_tc307_add_years_and_is_expired() -> None:
    assert domain.add_years(date(2028, 2, 29), 2) == date(2030, 2, 28)
    assert domain.add_years(date(2024, 2, 29), 4) == date(2028, 2, 29)
    assert domain.is_expired(date(2028, 2, 29), 2, date(2030, 2, 28)) is False
    assert domain.is_expired(date(2028, 2, 29), 2, date(2030, 3, 1)) is True


def test_add_years_backwards_and_plain_days() -> None:
    assert domain.add_years(date(2032, 2, 29), -2) == date(2030, 2, 28)
    assert domain.add_years(date(2026, 11, 1), 2) == date(2028, 11, 1)
    assert domain.is_expired(date(2026, 11, 1), 2, date(2028, 11, 1)) is False
    assert domain.is_expired(date(2026, 11, 1), 2, date(2028, 11, 2)) is True


def test_anonymize_counts_text() -> None:
    counts = domain.AnonymizeCounts(members=1, loans=2, deferred=3)
    assert domain.anonymize_counts_text(counts) == (
        "anonimleştirilen üye=1, bağı koparılan ödünç=2, ertelenen üye=3"
    )


# --- G16: catch-up (ADR-0007, ADR-0053, NFR-05) -----------------------------------

ISTANBUL = ZoneInfo("Europe/Istanbul")


def at(day: int, hour: int, minute: int) -> datetime:
    return datetime(2026, 11, day, hour, minute, tzinfo=ISTANBUL)


def test_tc310_weekly_export_boundaries() -> None:
    last = {"EXPORT": date(2026, 10, 26)}  # Monday
    assert domain.jobs_due_for_catch_up(at(2, 2, 59), last) == []  # Monday 02:59
    assert domain.jobs_due_for_catch_up(at(2, 3, 1), last) == ["EXPORT"]
    assert domain.jobs_due_for_catch_up(at(4, 10, 0), {"EXPORT": date(2026, 11, 2)}) == []


def test_weekly_export_never_run_and_exact_time() -> None:
    assert domain.jobs_due_for_catch_up(at(4, 10, 0), {"EXPORT": None}) == ["EXPORT"]
    assert domain.jobs_due_for_catch_up(at(2, 3, 0), {"EXPORT": date(2026, 10, 26)}) == ["EXPORT"]
    # Sunday: the last Monday is six days back.
    assert domain.jobs_due_for_catch_up(at(8, 23, 0), {"EXPORT": date(2026, 11, 1)}) == ["EXPORT"]
    assert domain.jobs_due_for_catch_up(at(8, 23, 0), {"EXPORT": date(2026, 11, 2)}) == []


def test_tc311_order_of_catch_up() -> None:
    last = {"REMINDERS": None, "EXPORT": None, "ANONYMIZE": None, "BACKUP": None}
    assert domain.jobs_due_for_catch_up(at(2, 10, 0), last) == [
        "BACKUP",
        "ANONYMIZE",
        "EXPORT",
        "REMINDERS",
    ]


def test_tc312_successful_reminders_with_failures_are_not_repeated() -> None:
    # KL-23: the run with "başarısız=1" is still SUCCESS, so last_success is today.
    last = {"REMINDERS": date(2026, 11, 4)}
    assert domain.jobs_due_for_catch_up(at(4, 10, 0), last) == []


def test_tc210_daily_boundary() -> None:
    last = {"REMINDERS": date(2026, 11, 3)}
    assert domain.jobs_due_for_catch_up(at(4, 8, 59), last) == []
    assert domain.jobs_due_for_catch_up(at(4, 9, 1), last) == ["REMINDERS"]
    assert domain.jobs_due_for_catch_up(at(4, 9, 0), last) == ["REMINDERS"]


def test_daily_jobs_and_their_times() -> None:
    last = {"BACKUP": date(2026, 11, 3), "ANONYMIZE": date(2026, 11, 3)}
    assert domain.jobs_due_for_catch_up(at(4, 1, 59), last) == []
    assert domain.jobs_due_for_catch_up(at(4, 2, 10), last) == ["BACKUP"]
    assert domain.jobs_due_for_catch_up(at(4, 2, 30), last) == ["BACKUP", "ANONYMIZE"]
    assert domain.jobs_due_for_catch_up(at(4, 2, 30), {"BACKUP": None}) == ["BACKUP"]


def test_catch_up_keeps_the_given_keys() -> None:
    """Callers pass ``Job`` members (a ``str`` enum); the same keys come back."""

    class Key(str):
        pass

    backup = Key("BACKUP")
    assert domain.jobs_due_for_catch_up(at(4, 10, 0), {backup: None})[0] is backup
