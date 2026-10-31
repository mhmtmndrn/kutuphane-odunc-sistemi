"""Unit tests for administration: clock, money and pure rules (G03).

TC-13, TC-14…TC-17, TC-238…TC-241, TC-247; plus validate_weekly_closed and
export_age_warning (KL-14).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone as dt_timezone

import pytest
from django.template import Context, Template
from django.utils import timezone

from administration import clock
from administration.audit import AuditAction
from administration.domain import backup_warning, export_age_warning, validate_weekly_closed
from administration.errors import RuleViolation
from administration.money import format_tl, parse_tl

# --- TC-13: "today" follows the Istanbul calendar day ------------------------


@pytest.mark.parametrize(
    ("instant", "expected"),
    [
        (datetime(2026, 11, 16, 20, 59, 59, tzinfo=dt_timezone.utc), date(2026, 11, 16)),
        (datetime(2026, 11, 16, 21, 0, 0, tzinfo=dt_timezone.utc), date(2026, 11, 17)),
    ],
)
def test_tc13_today_uses_local_midnight(
    monkeypatch: pytest.MonkeyPatch, instant: datetime, expected: date
) -> None:
    monkeypatch.setattr(timezone, "now", lambda: instant)
    assert clock.today() == expected


# --- TC-14…TC-17, TC-238…TC-240: money (ADR-0016, KL-3) ----------------------


@pytest.mark.parametrize(("text", "kurus"), [("15,00", 1500), ("0,01", 1), ("150,00", 15000)])
def test_tc14_parse_tl(text: str, kurus: int) -> None:
    assert parse_tl(text) == kurus


@pytest.mark.parametrize(("kurus", "text"), [(1500, "15,00 TL"), (1, "0,01 TL"), (0, "0,00 TL")])
def test_tc14_format_tl(kurus: int, text: str) -> None:
    assert format_tl(kurus) == text


def test_tc15_more_than_two_decimals_is_rejected() -> None:
    with pytest.raises(ValueError):
        parse_tl("15,005")


def test_tc16_negative_amount_is_rejected() -> None:
    with pytest.raises(ValueError):
        parse_tl("-5,00")


def test_tc16_letters_are_rejected() -> None:
    with pytest.raises(ValueError):
        parse_tl("abc")


def test_tc16_empty_input_is_rejected() -> None:
    with pytest.raises(ValueError):
        parse_tl("")


def test_tc17_sum_is_exact_integer() -> None:
    total = parse_tl("0,10") + parse_tl("0,20")
    assert total == 30
    assert type(total) is int


@pytest.mark.parametrize(
    ("text", "kurus"),
    [("15", 1500), ("15,5", 1550), ("15,50", 1550), ("1.250,00", 125000), ("1250", 125000)],
)
def test_tc238_accepted_forms(text: str, kurus: int) -> None:
    assert parse_tl(text) == kurus


@pytest.mark.parametrize(
    ("kurus", "text"),
    [(125000, "1.250,00 TL"), (100000000, "1.000.000,00 TL"), (5, "0,05 TL")],
)
def test_tc239_format_with_thousands_separator(kurus: int, text: str) -> None:
    assert format_tl(kurus) == text


def test_tc239_template_filter() -> None:
    rendered = Template("{% load money %}{{ amount|tl }}").render(Context({"amount": 125000}))
    assert rendered == "1.250,00 TL"


@pytest.mark.parametrize("text", ["15.00", "1.25", "1,250.00", "12.50,00"])
def test_tc240_thousands_dot_only_in_groups_of_three(text: str) -> None:
    with pytest.raises(ValueError):
        parse_tl(text)


def test_parse_tl_ignores_surrounding_spaces_and_rejects_non_ascii_digits() -> None:
    assert parse_tl(" 7,50 ") == 750
    with pytest.raises(ValueError):
        parse_tl("١٥")  # Arabic-Indic digits


def test_format_tl_rejects_non_integer() -> None:
    with pytest.raises(TypeError):
        format_tl(15.0)  # type: ignore[arg-type]


def test_format_tl_negative_amount() -> None:
    assert format_tl(-1250) == "-12,50 TL"


# --- TC-241: backup warning decision table (ADR-0044) -----------------------

NOW = datetime(2026, 11, 16, 4, 6, tzinfo=dt_timezone.utc)


@pytest.mark.parametrize(
    ("last_success_at", "last_failed", "expected"),
    [
        (None, False, "Günlük yedek henüz alınmadı"),
        (None, True, "Son günlük yedek başarısız oldu"),
        (NOW - timedelta(hours=1), True, "Son günlük yedek başarısız oldu"),
        (NOW - timedelta(hours=26), False, None),
        (NOW - timedelta(hours=26, seconds=1), False, "Günlük yedek 26 saatten eski"),
        (NOW - timedelta(hours=1), False, None),
    ],
)
def test_tc241_backup_warning(last_success_at, last_failed, expected) -> None:
    assert backup_warning(last_success_at, last_failed, NOW) == expected


# --- KL-14: export age warning ---------------------------------------------

TODAY = date(2026, 11, 16)


@pytest.mark.parametrize(
    ("last_export_on", "expected"),
    [
        (None, "Bina dışı yedek henüz alınmadı"),
        (TODAY - timedelta(days=7), None),
        (TODAY - timedelta(days=8), "Bina dışı yedek 7 günden eski"),
        (TODAY, None),
    ],
)
def test_export_age_warning(last_export_on, expected) -> None:
    assert export_age_warning(last_export_on, TODAY) == expected


# --- FR-24, ADR-0028: weekly closed days -----------------------------------


@pytest.mark.parametrize("days", [set(), {6}, {0, 1, 2, 3, 4, 5}])
def test_validate_weekly_closed_accepts_up_to_six_days(days: set[int]) -> None:
    validate_weekly_closed(days)


def test_validate_weekly_closed_rejects_all_seven_days() -> None:
    with pytest.raises(RuleViolation) as excinfo:
        validate_weekly_closed({0, 1, 2, 3, 4, 5, 6})
    assert excinfo.value.message == "En az bir gün açık kalmalı"


@pytest.mark.parametrize("days", [{7}, {-1}, {0, 9}])
def test_validate_weekly_closed_rejects_out_of_range(days: set[int]) -> None:
    with pytest.raises(ValueError):
        validate_weekly_closed(days)


def test_rule_violation_carries_message() -> None:
    error = RuleViolation("Örnek")
    assert error.message == "Örnek"
    assert str(error) == "Örnek"


# --- TC-247: audit actions (KL-30, KL-31) ------------------------------------


def test_tc247_audit_actions_are_exactly_fourteen() -> None:
    assert set(AuditAction.values) == {
        "PAYMENT",
        "WAIVER",
        "FEE",
        "REFUND",
        "COPY_LOST",
        "COPY_DAMAGED",
        "COPY_FOUND",
        "COPY_REPAIRED",
        "COPY_WITHDRAWN",
        "SETTINGS_CHANGED",
        "CLOSED_DAY_CHANGED",
        "STAFF_CHANGED",
        "CANCELLATION",
        "MEMBER_REACTIVATED",
    }
    assert len(AuditAction.values) == 14
