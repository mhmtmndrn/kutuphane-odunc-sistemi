"""Money as integer kuruş (ADR-0016) and its Turkish text form (KL-3)."""

from __future__ import annotations

import re

# Integer part: plain digits, or 1-3 digits followed by "."-separated groups
# of exactly three. Optional "," with one or two decimals. ASCII digits only.
_AMOUNT = re.compile(r"(?P<int>[0-9]{1,3}(?:\.[0-9]{3})+|[0-9]+)(?:,(?P<dec>[0-9]{1,2}))?")


def parse_tl(text: str) -> int:
    """Parse "1.250,50" style Turkish lira text into kuruş.

    Raises ``ValueError`` for empty, negative or malformed input and for more
    than two decimals.
    """
    match = _AMOUNT.fullmatch(text.strip())
    if match is None:
        raise ValueError(f"Geçersiz tutar: {text!r}")
    lira = int(match["int"].replace(".", ""))
    kurus = int((match["dec"] or "0").ljust(2, "0"))
    return lira * 100 + kurus


def format_tl(kurus: int) -> str:
    """Format kuruş as "1.250,00 TL"."""
    if not isinstance(kurus, int) or isinstance(kurus, bool):
        raise TypeError("format_tl expects an int amount in kuruş")
    sign = "-" if kurus < 0 else ""
    lira, rest = divmod(abs(kurus), 100)
    grouped = f"{lira:,}".replace(",", ".")
    return f"{sign}{grouped},{rest:02d} TL"
