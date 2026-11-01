"""Operations domain tests (G14): backup and export names, retention (KL-14,
KL-24, TC-187 and TC-299 rules), the newest backup and the passphrase text."""

from __future__ import annotations

from datetime import date

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
