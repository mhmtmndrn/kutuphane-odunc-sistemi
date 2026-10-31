"""Unit tests for the catalog domain: Turkish normalization and ISBN (G05).

TC-34…TC-43, TC-253; plus ``isbn10_to_13`` and the two ``IsbnInvalid``
reasons of plan G05.
"""

from __future__ import annotations

import pytest

from catalog.domain import (
    IsbnInvalid,
    IsbnOk,
    IsbnSuggest,
    isbn10_to_13,
    normalize_tr,
    parse_isbn,
)

LENGTH_REASON = "ISBN 10 ya da 13 haneli olmalı"
CHECK_REASON = "ISBN kontrol hanesi hatalı"

# --- normalize_tr (ADR-0019) --------------------------------------------------


@pytest.mark.parametrize("text", ["istanbul", "İstanbul", "İSTANBUL", "ISTANBUL"])
def test_tc34_istanbul_spellings_normalize_alike(text: str) -> None:
    assert normalize_tr(text) == "istanbul"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Şefiller", "sefiller"),
        ("IŞIK ÇĞÖÜ", "isik cgou"),
        ("Hâlâ", "hala"),
        ("Ayşe   Yılmaz", "ayse yilmaz"),
        ("", ""),
    ],
)
def test_tc35_turkish_letters_and_diacritics_fold(text: str, expected: str) -> None:
    assert normalize_tr(text) == expected


TURKISH_SAMPLES = [
    "Çalıkuşu",
    "Kürk Mantolu Madonna",
    "İnce Memed",
    "IŞIK ığdır",
    "Âşık Veysel",
    "Hâlâ Şöyle Böyle",
    "  boşluklu \t  metin  ",
    "Gülşen ÖZTÜRK",
    "Tutunamayanlar — Oğuz Atay",
    "Saatleri Ayarlama Enstitüsü",
    "Iğdır'ın İncileri",
    "şekil",  # "şekil" with a combining cedilla
]


@pytest.mark.parametrize("text", TURKISH_SAMPLES)
def test_tc36_normalize_is_idempotent_and_case_blind(text: str) -> None:
    once = normalize_tr(text)
    assert normalize_tr(once) == once
    assert normalize_tr(text.upper()) == normalize_tr(text.lower()) == once


def test_normalize_collapses_and_trims_whitespace() -> None:
    assert normalize_tr("  Oğuz \n Atay ") == "oguz atay"


# --- parse_isbn (ADR-0008, KL-40) ---------------------------------------------


@pytest.mark.parametrize("raw", ["9786053609322", "978-605-360-932-2", "978 605 360 932 2"])
def test_tc37_isbn13_with_hyphens_or_spaces_is_ok(raw: str) -> None:
    assert parse_isbn(raw) == IsbnOk("9786053609322")


@pytest.mark.parametrize(
    ("raw", "isbn13"),
    [("0306406152", "9780306406157"), ("080442957X", "9780804429573")],
)
def test_tc38_valid_isbn10_converts_to_isbn13(raw: str, isbn13: str) -> None:
    assert parse_isbn(raw) == IsbnOk(isbn13)


def test_tc39_isbn10_with_dropped_978_prefix_gets_a_suggestion() -> None:
    assert parse_isbn("6053609322") == IsbnSuggest("9786053609322")


def test_tc40_invalid_isbn10_without_valid_978_form_has_no_suggestion() -> None:
    assert parse_isbn("6053609321") == IsbnInvalid(CHECK_REASON)


def test_tc41_isbn13_with_wrong_check_digit_is_invalid() -> None:
    assert parse_isbn("9786053609321") == IsbnInvalid(CHECK_REASON)


@pytest.mark.parametrize("raw", ["605360932", "97860536093", "978605360932", "97860536093221"])
def test_tc42_wrong_digit_counts_are_invalid(raw: str) -> None:
    assert len(raw) in {9, 11, 12, 14}
    assert parse_isbn(raw) == IsbnInvalid(LENGTH_REASON)


@pytest.mark.parametrize("raw", ["978605360932X", "97860536O9322", "X053609322"])
def test_tc43_letters_in_the_wrong_place_are_invalid(raw: str) -> None:
    result = parse_isbn(raw)
    assert isinstance(result, IsbnInvalid)
    assert result.reason == LENGTH_REASON


def test_tc253_lowercase_x_in_isbn10_is_accepted() -> None:
    assert parse_isbn("080442957x") == IsbnOk("9780804429573")


def test_empty_isbn_is_invalid() -> None:
    assert parse_isbn("  ") == IsbnInvalid(LENGTH_REASON)


def test_isbn10_with_x_and_wrong_check_digit_has_no_suggestion() -> None:
    # "0306406153" fails; an X ending cannot take the "978" prefix.
    assert parse_isbn("030640615X") == IsbnInvalid(CHECK_REASON)


def test_results_are_frozen() -> None:
    with pytest.raises(AttributeError):
        IsbnOk("9786053609322").isbn13 = "x"  # type: ignore[misc]


# --- isbn10_to_13 -------------------------------------------------------------


@pytest.mark.parametrize(
    ("isbn10", "isbn13"),
    [
        ("0306406152", "9780306406157"),
        ("080442957X", "9780804429573"),
        ("080442957x", "9780804429573"),
        ("6053609322", "9786053609322"),
    ],
)
def test_isbn10_to_13_keeps_nine_digits_and_recomputes_the_check(isbn10: str, isbn13: str) -> None:
    assert isbn10_to_13(isbn10) == isbn13


@pytest.mark.parametrize("bad", ["030640615", "03064061521", "03064O6152"])
def test_isbn10_to_13_rejects_malformed_input(bad: str) -> None:
    with pytest.raises(ValueError):
        isbn10_to_13(bad)
