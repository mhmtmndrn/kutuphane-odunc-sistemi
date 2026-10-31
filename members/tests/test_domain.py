"""Unit tests for the members domain (G06).

TC-52 (member fields, NFR-08); plus ``phone_digits``,
``classify_member_query`` (KL-10), the member field rules and the consent
rule order of ADR-0047.
"""

from __future__ import annotations

from datetime import date

import pytest

from administration.errors import RuleViolation
from members.domain import (
    MemberQuery,
    check_consent_change,
    classify_member_query,
    phone_digits,
    validate_member_fields,
)
from members.models import Member

TODAY = date(2026, 11, 1)

# --- TC-52: only FR-01 personal fields (NFR-08) -------------------------------

PERSONAL_FIELDS = {"full_name", "phone", "phone_digits", "email", "search_key"}
# data-design §2.2: technical fields of ``member``.
TECHNICAL_FIELDS = {
    "id",
    "member_no",
    "is_active",
    "deactivated_on",
    "has_email_consent",
    "archived_loan_count",
    "anonymized_at",
}


def test_tc52_member_holds_only_fr01_personal_fields() -> None:
    fields = {field.name for field in Member._meta.concrete_fields}
    assert fields == PERSONAL_FIELDS | TECHNICAL_FIELDS


# --- phone_digits -------------------------------------------------------------


@pytest.mark.parametrize(
    ("phone", "digits"),
    [
        ("0555 111 22 33", "05551112233"),
        ("(0555) 111-22-33", "05551112233"),
        ("+90 555 111 22 33", "905551112233"),
        ("", ""),
        ("yok", ""),
    ],
)
def test_phone_digits_keeps_ascii_digits_only(phone: str, digits: str) -> None:
    assert phone_digits(phone) == digits


def test_phone_digits_drops_non_ascii_digits() -> None:
    assert phone_digits("٠٥٥٥ 12") == "12"


# --- classify_member_query (KL-10) ------------------------------------------------


@pytest.mark.parametrize(
    ("q", "expected"),
    [
        ("1042", MemberQuery(digits="1042")),
        ("0555-111-2233", MemberQuery(digits="05551112233")),
        ("(0555) 111 22 33", MemberQuery(digits="05551112233")),
        (" 42 ", MemberQuery(digits="42")),
        ("Ayşe Yılmaz", MemberQuery(text="ayse yilmaz")),
        ("AYŞE", MemberQuery(text="ayse")),
        ("Ali 2", MemberQuery(text="ali 2")),
        ("%", MemberQuery(text="%")),
        ("", MemberQuery()),
        ("  -() ", MemberQuery()),
    ],
)
def test_classify_member_query(q: str, expected: MemberQuery) -> None:
    assert classify_member_query(q) == expected


def test_empty_member_query_is_empty() -> None:
    assert MemberQuery().is_empty
    assert not MemberQuery(digits="1").is_empty
    assert not MemberQuery(text="a").is_empty


# --- validate_member_fields -----------------------------------------------------


def test_valid_member_fields_pass() -> None:
    validate_member_fields("Ayşe Yılmaz", "0555 111 22 33")


@pytest.mark.parametrize(
    ("full_name", "phone", "message"),
    [
        ("", "0555 111 22 33", "Ad soyad boş olamaz"),
        ("   ", "0555 111 22 33", "Ad soyad boş olamaz"),
        ("A" * 201, "0555 111 22 33", "Ad soyad en fazla 200 karakter olabilir"),
        ("Ayşe Yılmaz", "", "Telefon boş olamaz"),
        ("Ayşe Yılmaz", "  ", "Telefon boş olamaz"),
        ("Ayşe Yılmaz", "1" * 31, "Telefon en fazla 30 karakter olabilir"),
        ("Ayşe Yılmaz", "yok", "Telefon 1 ile 20 rakam içermeli"),
        ("Ayşe Yılmaz", "1" * 21, "Telefon 1 ile 20 rakam içermeli"),
    ],
)
def test_invalid_member_fields_are_refused(full_name: str, phone: str, message: str) -> None:
    with pytest.raises(RuleViolation) as exc:
        validate_member_fields(full_name, phone)
    assert exc.value.message == message


def test_member_field_bounds_are_inclusive() -> None:
    validate_member_fields("A" * 200, "1" * 20)


# --- check_consent_change (ADR-0047, KL-12) -------------------------------------


def test_consent_change_accepts_today_and_the_past() -> None:
    check_consent_change(given=True, on=TODAY, today=TODAY, has_email=True, currently_given=False)
    check_consent_change(
        given=False, on=date(2026, 1, 1), today=TODAY, has_email=True, currently_given=True
    )


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        (
            {"given": True, "on": date(2026, 11, 2), "has_email": True, "currently_given": False},
            "Rıza tarihi gelecekte olamaz",
        ),
        (
            {"given": True, "on": TODAY, "has_email": False, "currently_given": False},
            "Rıza için e-posta adresi gerekli",
        ),
        (
            {"given": True, "on": TODAY, "has_email": True, "currently_given": True},
            "Üyenin rızası zaten var",
        ),
        (
            {"given": False, "on": TODAY, "has_email": True, "currently_given": False},
            "Üyenin rızası zaten yok",
        ),
        (
            # Withdrawing needs no e-mail address.
            {"given": False, "on": TODAY, "has_email": False, "currently_given": False},
            "Üyenin rızası zaten yok",
        ),
    ],
)
def test_consent_change_refusals(kwargs: dict, message: str) -> None:
    with pytest.raises(RuleViolation) as exc:
        check_consent_change(today=TODAY, **kwargs)
    assert exc.value.message == message
