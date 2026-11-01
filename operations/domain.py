"""Pure rules for backups and exports (G14), retention (G15) and catch-up
(G16). No ORM, file system or clock: dates and names come in as arguments."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta

_BACKUP = re.compile(r"^library-(\d{8})\.sqlite3$")
_EXPORT = re.compile(r"^library-export-(\d{8})\.libx$")


def _name_date(pattern: re.Pattern[str], name: str) -> date | None:
    match = pattern.match(name)
    if match is None:
        return None
    try:
        return datetime.strptime(match.group(1), "%Y%m%d").date()
    except ValueError:  # e.g. library-20261340.sqlite3
        return None


def backup_name(on: date) -> str:
    """``library-YYYYMMDD.sqlite3`` (architecture §6.2)."""
    return f"library-{on:%Y%m%d}.sqlite3"


def export_name(on: date) -> str:
    """``library-export-YYYYMMDD.libx`` (architecture §6.2)."""
    return f"library-export-{on:%Y%m%d}.libx"


def _to_delete(
    pattern: re.Pattern[str], names: list[str], run_on: date, keep_days: int
) -> list[str]:
    oldest_kept = run_on - timedelta(days=keep_days)
    return sorted(
        name for name in names if (on := _name_date(pattern, name)) is not None and on < oldest_kept
    )


def backups_to_delete(names: list[str], run_on: date, keep_days: int = 30) -> list[str]:
    """Daily backups older than ``run_on − keep_days`` (KL-14). Names that do
    not follow the pattern are never returned."""
    return _to_delete(_BACKUP, names, run_on, keep_days)


def exports_to_delete(names: list[str], run_on: date, keep_days: int = 56) -> list[str]:
    """Exports older than ``run_on − keep_days``, the last 8 weeks (KL-24)."""
    return _to_delete(_EXPORT, names, run_on, keep_days)


def latest_backup(names: list[str]) -> str | None:
    """The daily backup with the newest date in its name (KL-14)."""
    dated = [(on, name) for name in names if (on := _name_date(_BACKUP, name)) is not None]
    return max(dated)[1] if dated else None


def passphrase_from_text(text: str) -> str:
    """Drop one trailing line end (``\\n`` or ``\\r\\n``); an empty passphrase
    raises ``ValueError`` (plan G14)."""
    passphrase = text.removesuffix("\n").removesuffix("\r")
    if not passphrase:
        raise ValueError("empty passphrase")
    return passphrase
