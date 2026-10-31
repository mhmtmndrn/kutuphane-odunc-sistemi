"""Pure catalog rules: Turkish search normalization and ISBN parsing (plan G05).

No ORM, HTTP or clock calls (ADR-0015). ``members`` imports ``normalize_tr``
from here (KL-2).
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

__all__ = [
    "IsbnInvalid",
    "IsbnOk",
    "IsbnSuggest",
    "isbn10_to_13",
    "normalize_tr",
    "parse_isbn",
]

# --- Turkish normalization (ADR-0019) -----------------------------------------

_DOTTED_CAPITAL = str.maketrans({"İ": "i", "I": "ı"})
_FOLD = str.maketrans("ışğçöü", "isgcou")


def normalize_tr(text: str) -> str:
    """The search key of ``text``: O(L) time and space for length L.

    1. "İ" -> "i" and "I" -> "ı", then lower case.
    2. ı, ş, ğ, ç, ö, ü -> i, s, g, c, o, u.
    3. Combining marks left after NFKD are dropped (â, î, û).
    4. Runs of whitespace become one space; leading and trailing space go.
    """
    text = text.translate(_DOTTED_CAPITAL).lower()
    text = text.translate(_FOLD)
    text = "".join(ch for ch in unicodedata.normalize("NFKD", text) if not unicodedata.combining(ch))
    return " ".join(text.split())


# --- ISBN (ADR-0008, KL-40) ---------------------------------------------------

LENGTH_REASON = "ISBN 10 ya da 13 haneli olmalı"
CHECK_REASON = "ISBN kontrol hanesi hatalı"


@dataclass(frozen=True)
class IsbnOk:
    """A valid ISBN, always stored as a 13-digit string without hyphens."""

    isbn13: str


@dataclass(frozen=True)
class IsbnSuggest:
    """A 10-digit entry whose check digit fails but whose "978" form is valid."""

    suggestion: str


@dataclass(frozen=True)
class IsbnInvalid:
    reason: str


def _isbn10_valid(isbn10: str) -> bool:
    total = sum((10 - i) * int(ch) for i, ch in enumerate(isbn10[:9]))
    last = 10 if isbn10[9] == "X" else int(isbn10[9])
    return (total + last) % 11 == 0


def _isbn13_check_digit(first12: str) -> str:
    total = sum(int(ch) * (3 if i % 2 else 1) for i, ch in enumerate(first12))
    return str((10 - total % 10) % 10)


def _isbn13_valid(isbn13: str) -> bool:
    return _isbn13_check_digit(isbn13[:12]) == isbn13[12]


def _is_isbn10_form(value: str) -> bool:
    return len(value) == 10 and value[:9].isascii() and value[:9].isdigit() and (
        value[9] == "X" or (value[9].isascii() and value[9].isdigit())
    )


def _is_isbn13_form(value: str) -> bool:
    return len(value) == 13 and value.isascii() and value.isdigit()


def isbn10_to_13(isbn10: str) -> str:
    """"978" + the first nine digits + a new ISBN-13 check digit.

    The ISBN-10 check digit is not verified; a malformed value raises
    ``ValueError``.
    """
    value = isbn10.upper()
    if not _is_isbn10_form(value):
        raise ValueError(f"not an ISBN-10: {isbn10!r}")
    first12 = "978" + value[:9]
    return first12 + _isbn13_check_digit(first12)


def parse_isbn(raw: str) -> IsbnOk | IsbnSuggest | IsbnInvalid:
    """Validate an ISBN entry (ADR-0008). O(1): at most 13 digits.

    Hyphens and whitespace are removed. A valid ISBN-10 (last digit may be
    "X" or "x") becomes ISBN-13. A 10-digit entry with a failing check digit
    gets a suggestion when "978" + entry is a valid ISBN-13.
    """
    value = "".join(ch for ch in raw if ch != "-" and not ch.isspace()).upper()
    if _is_isbn13_form(value):
        return IsbnOk(value) if _isbn13_valid(value) else IsbnInvalid(CHECK_REASON)
    if not _is_isbn10_form(value):
        return IsbnInvalid(LENGTH_REASON)
    if _isbn10_valid(value):
        return IsbnOk(isbn10_to_13(value))
    prefixed = "978" + value
    if _is_isbn13_form(prefixed) and _isbn13_valid(prefixed):
        return IsbnSuggest(prefixed)
    return IsbnInvalid(CHECK_REASON)
