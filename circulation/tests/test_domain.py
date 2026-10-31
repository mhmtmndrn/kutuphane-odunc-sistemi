"""Unit tests for the circulation domain (G10).

TC-104…TC-123, TC-276, TC-277, TC-279, TC-280; plus the copy state machine
of architecture §5.1 (``COPY_TRANSITIONS``, ``check_transition``), which G12
exercises through the services (TC-163…TC-167).
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from administration.errors import RuleViolation
from catalog.models import CopyStatus
from circulation.domain import (
    COPY_TRANSITIONS,
    NO_OPEN_DAY_MESSAGE,
    STATUS_LABELS,
    Blocker,
    CheckoutState,
    InvalidTransition,
    MemberInput,
    NoOpenDayError,
    RenewState,
    check_transition,
    checkout_blockers,
    classify_member_input,
    due_date,
    fine,
    late_days,
    renew_blockers,
    renewed_due_date,
)

SUNDAY = 6


def never_closed(day: date) -> bool:
    return False


def closed_on(weekdays: set[int] = frozenset(), dates: set[date] = frozenset()):
    def is_closed(day: date) -> bool:
        return day.weekday() in weekdays or day in dates

    return is_closed


# --- due_date (FR-07, FR-24, ADR-0028) -----------------------------------------


def test_tc104_due_date_without_closed_days() -> None:
    assert due_date(date(2026, 11, 2), 14, never_closed) == date(2026, 11, 16)


def test_tc105_due_date_shifts_off_a_closed_sunday() -> None:
    # 2026-11-02 + 13 = 2026-11-15, a Sunday.
    assert due_date(date(2026, 11, 2), 13, closed_on({SUNDAY})) == date(2026, 11, 16)


def test_tc106_due_date_shifts_off_a_closed_date() -> None:
    is_closed = closed_on({SUNDAY}, {date(2027, 10, 29)})
    assert due_date(date(2027, 10, 15), 14, is_closed) == date(2027, 10, 30)


def test_tc107_due_date_skips_weekend_and_closed_monday() -> None:
    # 2026-10-31 + 14 = Saturday 11-14; Sunday 11-15; Monday 11-16 is closed.
    is_closed = closed_on({5, SUNDAY}, {date(2026, 11, 16)})
    assert due_date(date(2026, 10, 31), 14, is_closed) == date(2026, 11, 17)


def test_tc108_due_date_across_leap_february_and_new_year() -> None:
    assert due_date(date(2028, 2, 20), 14, never_closed) == date(2028, 3, 5)
    assert due_date(date(2026, 12, 25), 14, never_closed) == date(2027, 1, 8)


def test_tc109_due_date_looks_366_days_ahead() -> None:
    start = date(2026, 11, 2)
    candidate = start + timedelta(days=14)
    last_open = candidate + timedelta(days=366)

    def closed_until_366(day: date) -> bool:
        return day < last_open

    assert due_date(start, 14, closed_until_366) == last_open


def test_tc109_due_date_raises_when_367_days_are_closed() -> None:
    start = date(2026, 11, 2)
    candidate = start + timedelta(days=14)
    checked: list[date] = []

    def closed_through_366(day: date) -> bool:
        checked.append(day)
        return day <= candidate + timedelta(days=366)

    with pytest.raises(NoOpenDayError) as exc:
        due_date(start, 14, closed_through_366)
    assert exc.value.message == NO_OPEN_DAY_MESSAGE
    assert NO_OPEN_DAY_MESSAGE == (
        "Önümüzdeki 366 günde açık gün yok; kapalı gün ayarlarını kontrol edin"
    )
    assert isinstance(exc.value, RuleViolation)
    # aday + 0…366: 367 checks and never further.
    assert len(checked) == 367
    assert max(checked) == candidate + timedelta(days=366)


def test_renewed_due_date_extends_from_the_current_due_date() -> None:
    """Phase 1 small decision 3: current due date + period, shifted (TC-140 at service level)."""
    assert renewed_due_date(date(2026, 11, 16), 14, never_closed) == date(2026, 11, 30)
    assert renewed_due_date(date(2026, 11, 16), 13, closed_on({SUNDAY})) == date(2026, 11, 30)


# --- late_days and fine (FR-12, ADR-0023, ADR-0040) ------------------------------


@pytest.mark.parametrize(
    ("on", "expected"),
    [(date(2026, 11, 15), 0), (date(2026, 11, 16), 0), (date(2026, 11, 17), 1)],
)
def test_tc110_late_days_around_the_due_date(on: date, expected: int) -> None:
    assert late_days(date(2026, 11, 16), on, frozenset()) == expected


def test_tc111_late_days_three_days_late() -> None:
    assert late_days(date(2026, 11, 16), date(2026, 11, 19), frozenset()) == 3


@pytest.mark.parametrize(
    ("days", "expected"), [(0, 0), (29, 14500), (30, 15000), (31, 15000), (40, 15000)]
)
def test_tc112_fine_is_capped(days: int, expected: int) -> None:
    assert fine(days, 500, 15000) == expected


def test_tc113_fine_edge_cases() -> None:
    assert fine(10, 0, 15000) == 0
    assert fine(10, 500, 0) == 0
    assert fine(100000, 500, 15000) == 15000


def test_tc276_closed_date_inside_the_range_is_not_counted() -> None:
    assert late_days(date(2026, 11, 16), date(2026, 11, 20), {date(2026, 11, 18)}) == 3
    assert fine(3, 500, 15000) == 1500


@pytest.mark.parametrize(
    ("closed", "expected"),
    [
        ({date(2026, 11, 16)}, 4),  # the due date itself is not subtracted
        ({date(2026, 11, 20)}, 3),  # the return day is subtracted
        ({date(2026, 11, 15), date(2026, 11, 21)}, 4),  # outside the range
    ],
)
def test_tc277_closed_date_range_bounds(closed: set[date], expected: int) -> None:
    assert late_days(date(2026, 11, 16), date(2026, 11, 20), closed) == expected


def test_tc277_late_days_never_negative() -> None:
    assert late_days(date(2026, 11, 16), date(2026, 11, 17), {date(2026, 11, 17)}) == 0


# --- checkout_blockers (FR-02, FR-08, KL-6) ---------------------------------------


def checkout_state(**changes: object) -> CheckoutState:
    values: dict[str, object] = {
        "member_active": True,
        "open_loans": 2,
        "max_open_loans": 3,
        "has_overdue": False,
        "balance_kurus": 4999,
        "debt_threshold_kurus": 5000,
        "copy_status": "ON_SHELF",
    }
    values.update(changes)
    return CheckoutState(**values)  # type: ignore[arg-type]


def test_tc114_no_blockers() -> None:
    assert checkout_blockers(checkout_state()) == []


def test_tc115_inactive_member() -> None:
    assert checkout_blockers(checkout_state(member_active=False)) == [Blocker.MEMBER_INACTIVE]
    assert Blocker.MEMBER_INACTIVE.value == "Üye pasif"


@pytest.mark.parametrize("open_loans", [3, 4])
def test_tc116_limit_reached(open_loans: int) -> None:
    assert checkout_blockers(checkout_state(open_loans=open_loans)) == [Blocker.LIMIT_REACHED]
    assert Blocker.LIMIT_REACHED.value == "Ödünç limiti dolu"


def test_tc117_has_overdue() -> None:
    assert checkout_blockers(checkout_state(has_overdue=True)) == [Blocker.HAS_OVERDUE]
    assert Blocker.HAS_OVERDUE.value == "Gecikmiş ödünç var"


@pytest.mark.parametrize("balance", [5000, 5001])
def test_tc118_debt_threshold_is_inclusive(balance: int) -> None:
    assert checkout_blockers(checkout_state(balance_kurus=balance)) == [Blocker.DEBT_THRESHOLD]
    assert Blocker.DEBT_THRESHOLD.value == "Borç eşiği aşıldı"


@pytest.mark.parametrize("status", ["ON_LOAN", "LOST", "DAMAGED", "WITHDRAWN"])
def test_tc119_copy_not_on_shelf(status: str) -> None:
    assert checkout_blockers(checkout_state(copy_status=status)) == [Blocker.COPY_NOT_ON_SHELF]
    assert Blocker.COPY_NOT_ON_SHELF.value == "Nüsha rafta değil"


# --- renew_blockers (FR-10, KL-6) -------------------------------------------------

TODAY = date(2026, 11, 16)


def renew_state(**changes: object) -> RenewState:
    values: dict[str, object] = {
        "renewed": False,
        "due_on": TODAY,
        "today": TODAY,
        "balance_kurus": 0,
    }
    values.update(changes)
    return RenewState(**values)  # type: ignore[arg-type]


def test_tc120_renew_on_the_due_date() -> None:
    assert renew_blockers(renew_state()) == []


def test_tc121_already_renewed() -> None:
    assert renew_blockers(renew_state(renewed=True)) == [Blocker.ALREADY_RENEWED]
    assert Blocker.ALREADY_RENEWED.value == "Uzatma hakkı kullanıldı"


def test_tc122_loan_overdue() -> None:
    assert renew_blockers(renew_state(due_on=TODAY - timedelta(days=1))) == [
        Blocker.LOAN_OVERDUE
    ]
    assert Blocker.LOAN_OVERDUE.value == "Ödünç gecikmiş"


@pytest.mark.parametrize("balance", [200, 1])
def test_tc123_unpaid_debt(balance: int) -> None:
    assert renew_blockers(renew_state(balance_kurus=balance)) == [Blocker.HAS_DEBT]
    assert Blocker.HAS_DEBT.value == "Ödenmemiş borç var"


def test_tc280_all_blockers_in_enum_order() -> None:
    state = checkout_state(
        member_active=False,
        open_loans=3,
        has_overdue=True,
        balance_kurus=5000,
        copy_status="ON_LOAN",
    )
    assert checkout_blockers(state) == [
        Blocker.MEMBER_INACTIVE,
        Blocker.LIMIT_REACHED,
        Blocker.HAS_OVERDUE,
        Blocker.DEBT_THRESHOLD,
        Blocker.COPY_NOT_ON_SHELF,
    ]
    renew = renew_state(renewed=True, due_on=TODAY - timedelta(days=1), balance_kurus=1)
    assert renew_blockers(renew) == [
        Blocker.ALREADY_RENEWED,
        Blocker.LOAN_OVERDUE,
        Blocker.HAS_DEBT,
    ]


def test_blocker_enum_order_and_messages() -> None:
    assert [b.value for b in Blocker] == [
        "Üye pasif",
        "Ödünç limiti dolu",
        "Gecikmiş ödünç var",
        "Borç eşiği aşıldı",
        "Nüsha rafta değil",
        "Uzatma hakkı kullanıldı",
        "Ödünç gecikmiş",
        "Ödenmemiş borç var",
    ]


# --- classify_member_input (FR-11, ADR-0046, KL-35) -----------------------------


@pytest.mark.parametrize(
    ("raw", "kind", "value"),
    [
        ("00000042", "COPY_BARCODE", "00000042"),
        ("05551112233", "PHONE", "05551112233"),
        ("5551112233", "PHONE", "5551112233"),
        ("0555 111 22 33", "PHONE", "05551112233"),
        ("(0555) 111-22-33", "PHONE", "05551112233"),
        ("1042", "MEMBER_NO", "1042"),
        ("12345678", "MEMBER_NO", "12345678"),
        ("0000042", "MEMBER_NO", "0000042"),
        ("012345678", "MEMBER_NO", "012345678"),
        ("ayşe", "TEXT", "ayşe"),
    ],
)
def test_tc279_classify_member_input(raw: str, kind: str, value: str) -> None:
    assert classify_member_input(raw) == MemberInput(kind, value)  # type: ignore[arg-type]


def test_classify_member_input_edges() -> None:
    """Surrounding whitespace is ignored; text keeps its own spelling; blank is empty TEXT."""
    assert classify_member_input(" 00000042\t") == MemberInput("COPY_BARCODE", "00000042")
    assert classify_member_input("  Ayşe Yılmaz ") == MemberInput("TEXT", "Ayşe Yılmaz")
    assert classify_member_input("0555-ABC") == MemberInput("TEXT", "0555-ABC")
    # Non-ASCII digits are not digits here (same rule as members.domain).
    assert classify_member_input("٤٢").kind == "TEXT"
    assert classify_member_input("  ") == MemberInput("TEXT", "")
    assert classify_member_input("()-") == MemberInput("TEXT", "")


# --- Copy state machine (architecture §5.1, FR-05, FR-15, FR-16, FR-39) -----------

EXPECTED_TRANSITIONS = {
    ("ON_SHELF", "ON_LOAN"): "CLERK",
    ("ON_LOAN", "ON_SHELF"): "CLERK",
    ("ON_LOAN", "LOST"): "ADMIN",
    ("ON_LOAN", "DAMAGED"): "ADMIN",
    ("ON_SHELF", "LOST"): "ADMIN",
    ("ON_SHELF", "DAMAGED"): "ADMIN",
    ("ON_SHELF", "WITHDRAWN"): "ADMIN",
    ("LOST", "WITHDRAWN"): "ADMIN",
    ("LOST", "ON_SHELF"): "CLERK",
    ("DAMAGED", "ON_SHELF"): "ADMIN",
    ("DAMAGED", "WITHDRAWN"): "ADMIN",
}


def test_copy_transitions_match_architecture() -> None:
    assert COPY_TRANSITIONS == EXPECTED_TRANSITIONS


@pytest.mark.parametrize(("pair", "role"), sorted(EXPECTED_TRANSITIONS.items()))
def test_check_transition_returns_the_required_role(pair: tuple[str, str], role: str) -> None:
    assert check_transition(*pair) == role


def test_check_transition_refuses_every_other_pair() -> None:
    statuses = list(CopyStatus.values)
    refused = [
        (old, new)
        for old in statuses
        for new in statuses
        if (old, new) not in EXPECTED_TRANSITIONS
    ]
    assert len(refused) == 25 - 11
    for old, new in refused:
        with pytest.raises(InvalidTransition) as exc:
            check_transition(old, new)
        assert isinstance(exc.value, RuleViolation)
        assert exc.value.message == (
            f"Bu durum değişikliği yapılamaz: {STATUS_LABELS[old]} → {STATUS_LABELS[new]}"
        )


def test_check_transition_message_uses_turkish_labels() -> None:
    with pytest.raises(InvalidTransition, match="Bu durum değişikliği yapılamaz: Kayıp → Hasarlı"):
        check_transition("LOST", "DAMAGED")


def test_status_labels_match_copy_status() -> None:
    assert STATUS_LABELS == dict(CopyStatus.choices)


def test_transition_error_builds_the_same_message() -> None:
    """G12: a service refusing a source status it does not handle (e.g.
    ``mark_shelf_copy`` on an ON_LOAN copy, TC-164) uses the same message."""
    from circulation.domain import transition_error

    error = transition_error("ON_LOAN", "LOST")
    assert isinstance(error, InvalidTransition)
    assert error.message == "Bu durum değişikliği yapılamaz: Ödünçte → Kayıp"
    assert transition_error("X", "Y").message == "Bu durum değişikliği yapılamaz: X → Y"
