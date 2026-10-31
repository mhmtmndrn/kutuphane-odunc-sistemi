"""Pure member rules (plan G06): phone digits, query classification, field
and consent checks. No ORM, HTTP or clock calls (ADR-0015).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from administration.errors import RuleViolation
from catalog.domain import normalize_tr

__all__ = [
    "MemberQuery",
    "check_consent_change",
    "classify_member_query",
    "phone_digits",
    "validate_member_fields",
]

# KL-10 and KL-35: characters removed before a query is classified.
_QUERY_SEPARATORS = str.maketrans("", "", " -()")

FULL_NAME_MAX = 200
PHONE_MAX = 30
PHONE_DIGITS_MAX = 20


def phone_digits(phone: str) -> str:
    """The ASCII digits of ``phone``, in order; O(L)."""
    return "".join(ch for ch in phone if "0" <= ch <= "9")


@dataclass(frozen=True)
class MemberQuery:
    """A classified member search (KL-10).

    ``digits`` is set for a query of digits only (after removing space, "-",
    "(" and ")"); it matches the member number exactly or the phone digits
    partially. Otherwise ``text`` holds ``normalize_tr`` of the original query.
    Both are empty for a blank query.
    """

    digits: str = ""
    text: str = ""

    @property
    def is_empty(self) -> bool:
        return not (self.digits or self.text)


def classify_member_query(q: str) -> MemberQuery:
    cleaned = q.translate(_QUERY_SEPARATORS).strip()
    if not cleaned:
        return MemberQuery()
    if cleaned.isascii() and cleaned.isdigit():
        return MemberQuery(digits=cleaned)
    return MemberQuery(text=normalize_tr(q))


def validate_member_fields(full_name: str, phone: str) -> None:
    """FR-01 fields; ``full_name`` and ``phone`` are required."""
    full_name = full_name.strip()
    if not full_name:
        raise RuleViolation("Ad soyad boş olamaz")
    if len(full_name) > FULL_NAME_MAX:
        raise RuleViolation("Ad soyad en fazla 200 karakter olabilir")
    phone = phone.strip()
    if not phone:
        raise RuleViolation("Telefon boş olamaz")
    if len(phone) > PHONE_MAX:
        raise RuleViolation("Telefon en fazla 30 karakter olabilir")
    if not 1 <= len(phone_digits(phone)) <= PHONE_DIGITS_MAX:
        raise RuleViolation("Telefon 1 ile 20 rakam içermeli")


CONSENT_FUTURE = "Rıza tarihi gelecekte olamaz"
CONSENT_NEEDS_EMAIL = "Rıza için e-posta adresi gerekli"
CONSENT_ALREADY_GIVEN = "Üyenin rızası zaten var"
CONSENT_ALREADY_WITHDRAWN = "Üyenin rızası zaten yok"


def check_consent_change(
    *, given: bool, on: date, today: date, has_email: bool, currently_given: bool
) -> None:
    """ADR-0047 and KL-12, checked in this order: future date, missing e-mail
    (giving only), repeat of the current state."""
    if on > today:
        raise RuleViolation(CONSENT_FUTURE)
    if given and not has_email:
        raise RuleViolation(CONSENT_NEEDS_EMAIL)
    if given == currently_given:
        raise RuleViolation(CONSENT_ALREADY_GIVEN if given else CONSENT_ALREADY_WITHDRAWN)
