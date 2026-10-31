"""Pure circulation rules (plan G10): due dates, late days, fines, blockers,
member input classification and the copy state machine.

No ORM, HTTP or clock calls (ADR-0015); "today" and the closed days arrive
as parameters.
"""

from __future__ import annotations

from collections.abc import Callable, Set as AbstractSet
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
from typing import Literal

from administration.errors import RuleViolation

__all__ = [
    "COPY_TRANSITIONS",
    "NO_OPEN_DAY_MESSAGE",
    "STATUS_LABELS",
    "Blocker",
    "CheckoutState",
    "InvalidTransition",
    "MemberInput",
    "NoOpenDayError",
    "RenewState",
    "check_transition",
    "checkout_blockers",
    "classify_member_input",
    "due_date",
    "fine",
    "late_days",
    "renew_blockers",
    "renewed_due_date",
]

# --- Due dates (FR-07, FR-10, FR-24, ADR-0028) -----------------------------------

SHIFT_LIMIT_DAYS = 366  # ADR-0028: candidate + 0…366 are checked
NO_OPEN_DAY_MESSAGE = "Önümüzdeki 366 günde açık gün yok; kapalı gün ayarlarını kontrol edin"


class NoOpenDayError(RuleViolation):
    """No open day within 366 days of the candidate due date (ADR-0028)."""

    def __init__(self, message: str = NO_OPEN_DAY_MESSAGE) -> None:
        super().__init__(message)


def due_date(start: date, period_days: int, is_closed: Callable[[date], bool]) -> date:
    """The first open day from ``start + period_days``; worst case O(366)."""
    candidate = start + timedelta(days=period_days)
    for offset in range(SHIFT_LIMIT_DAYS + 1):
        day = candidate + timedelta(days=offset)
        if not is_closed(day):
            return day
    raise NoOpenDayError()


def renewed_due_date(current_due: date, period_days: int, is_closed: Callable[[date], bool]) -> date:
    """Renewal extends from the current due date (phase 1 small decision 3)."""
    return due_date(current_due, period_days, is_closed)


# --- Late days and fines (FR-12, ADR-0023, ADR-0040) -----------------------------


def late_days(due_on: date, on: date, closed_dates: AbstractSet[date]) -> int:
    """Calendar days after ``due_on`` up to ``on``, minus the single closed
    dates in ``(due_on, on]``; never negative. O(c), c = len(closed_dates)."""
    calendar_days = (on - due_on).days
    if calendar_days <= 0:
        return 0
    closed = sum(1 for day in closed_dates if due_on < day <= on)
    return max(0, calendar_days - closed)


def fine(late_days: int, daily_kurus: int, cap_kurus: int) -> int:
    """``min(late_days × daily_kurus, cap_kurus)``; O(1)."""
    return min(late_days * daily_kurus, cap_kurus)


# --- Blockers (FR-02, FR-08, FR-10, KL-6) ----------------------------------------


class Blocker(Enum):
    """A reason that refuses a checkout or renewal; the value is the SRS text.

    All applicable blockers are listed together, in this order (KL-6).
    """

    MEMBER_INACTIVE = "Üye pasif"
    LIMIT_REACHED = "Ödünç limiti dolu"
    HAS_OVERDUE = "Gecikmiş ödünç var"
    DEBT_THRESHOLD = "Borç eşiği aşıldı"
    COPY_NOT_ON_SHELF = "Nüsha rafta değil"
    ALREADY_RENEWED = "Uzatma hakkı kullanıldı"
    LOAN_OVERDUE = "Ödünç gecikmiş"
    HAS_DEBT = "Ödenmemiş borç var"


@dataclass(frozen=True)
class CheckoutState:
    member_active: bool
    open_loans: int
    max_open_loans: int
    has_overdue: bool
    balance_kurus: int
    debt_threshold_kurus: int
    copy_status: str


def checkout_blockers(s: CheckoutState) -> list[Blocker]:
    """Every applicable blocker in enum order; the threshold is inclusive."""
    checks = [
        (not s.member_active, Blocker.MEMBER_INACTIVE),
        (s.open_loans >= s.max_open_loans, Blocker.LIMIT_REACHED),
        (s.has_overdue, Blocker.HAS_OVERDUE),
        (s.balance_kurus >= s.debt_threshold_kurus, Blocker.DEBT_THRESHOLD),
        (s.copy_status != "ON_SHELF", Blocker.COPY_NOT_ON_SHELF),
    ]
    return [blocker for applies, blocker in checks if applies]


@dataclass(frozen=True)
class RenewState:
    renewed: bool
    due_on: date
    today: date
    balance_kurus: int


def renew_blockers(s: RenewState) -> list[Blocker]:
    """A loan is overdue when ``due_on < today`` (calendar days, ADR-0040)."""
    checks = [
        (s.renewed, Blocker.ALREADY_RENEWED),
        (s.due_on < s.today, Blocker.LOAN_OVERDUE),
        (s.balance_kurus > 0, Blocker.HAS_DEBT),
    ]
    return [blocker for applies, blocker in checks if applies]


# --- Member field on the checkout screen (FR-11, ADR-0046, KL-35) ----------------

MemberInputKind = Literal["COPY_BARCODE", "PHONE", "MEMBER_NO", "TEXT"]

# KL-35: characters removed before the input is classified (as in KL-10).
_INPUT_SEPARATORS = str.maketrans("", "", " -()")
_PHONE_LENGTHS = (10, 11)
_BARCODE_LENGTH = 8


@dataclass(frozen=True)
class MemberInput:
    """``value`` is the cleaned digits, or the stripped text for TEXT."""

    kind: MemberInputKind
    value: str


def classify_member_input(raw: str) -> MemberInput:
    """ADR-0046: an 8-digit value starting with "0" is a copy barcode, 10–11
    digits a phone number, other digits a member number, anything else a name.
    Blank input is ``TEXT`` with an empty value."""
    cleaned = raw.translate(_INPUT_SEPARATORS).strip()
    if not (cleaned and cleaned.isascii() and cleaned.isdigit()):
        return MemberInput("TEXT", raw.strip() if cleaned else "")
    if len(cleaned) == _BARCODE_LENGTH and cleaned.startswith("0"):
        return MemberInput("COPY_BARCODE", cleaned)
    if len(cleaned) in _PHONE_LENGTHS:
        return MemberInput("PHONE", cleaned)
    return MemberInput("MEMBER_NO", cleaned)


# --- Copy state machine (architecture §5.1) -------------------------------------

Role = Literal["ADMIN", "CLERK"]

# The Turkish labels of catalog.models.CopyStatus; kept here so the domain
# does not import a models module (ADR-0015). A test keeps them equal.
STATUS_LABELS = {
    "ON_SHELF": "Rafta",
    "ON_LOAN": "Ödünçte",
    "LOST": "Kayıp",
    "DAMAGED": "Hasarlı",
    "WITHDRAWN": "Kayıttan düşmüş",
}

COPY_TRANSITIONS: dict[tuple[str, str], Role] = {
    ("ON_SHELF", "ON_LOAN"): "CLERK",  # checkout
    ("ON_LOAN", "ON_SHELF"): "CLERK",  # check-in
    ("ON_LOAN", "LOST"): "ADMIN",  # lost, with fee
    ("ON_LOAN", "DAMAGED"): "ADMIN",  # damaged, with fee
    ("ON_SHELF", "LOST"): "ADMIN",  # FR-39, no fee
    ("ON_SHELF", "DAMAGED"): "ADMIN",  # FR-39, no fee
    ("ON_SHELF", "WITHDRAWN"): "ADMIN",  # FR-39
    ("LOST", "WITHDRAWN"): "ADMIN",  # FR-39
    ("LOST", "ON_SHELF"): "CLERK",  # found
    ("DAMAGED", "ON_SHELF"): "ADMIN",  # repaired
    ("DAMAGED", "WITHDRAWN"): "ADMIN",  # withdrawn
}


class InvalidTransition(RuleViolation):
    """A copy status change outside architecture §5.1."""


def check_transition(from_status: str, to_status: str) -> Role:
    """The role a transition needs; any other pair raises ``InvalidTransition``."""
    role = COPY_TRANSITIONS.get((from_status, to_status))
    if role is None:
        old = STATUS_LABELS.get(from_status, from_status)
        new = STATUS_LABELS.get(to_status, to_status)
        raise InvalidTransition(f"Bu durum değişikliği yapılamaz: {old} → {new}")
    return role
