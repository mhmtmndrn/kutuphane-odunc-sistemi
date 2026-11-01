"""Pure rules for backups and exports (G14), retention (G15) and catch-up
(G16). No ORM, file system or clock: dates and names come in as arguments."""

from __future__ import annotations

import re
from dataclasses import dataclass
from collections.abc import Hashable, Mapping
from typing import TypeVar
from datetime import date, datetime, time, timedelta

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


# --- G15: retention (FR-25, phase 3 small decision 4, ADR-0018, ADR-0045) ---------


def add_years(d: date, years: int) -> date:
    """The same day ``years`` later (or earlier); 29 February falls back to
    28 February."""
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d.replace(year=d.year + years, day=28)


def is_expired(start: date, years: int, today: date) -> bool:
    """Retention is over the day after the anniversary (small decision 4)."""
    return add_years(start, years) < today


@dataclass(frozen=True)
class AnonymizeCounts:
    members: int
    loans: int
    deferred: int


def anonymize_counts_text(counts: AnonymizeCounts) -> str:
    """Output and ``job_run`` detail of ``anonymize_expired`` (architecture §6.2)."""
    return (
        f"anonimleştirilen üye={counts.members}, bağı koparılan ödünç={counts.loans}, "
        f"ertelenen üye={counts.deferred}"
    )


# --- G16: catch-up (ADR-0007, ADR-0053, NFR-05) -------------------------------------

# Planned local times (Europe/Istanbul, phase 3 small decision 13): job name ->
# (weekday or None for daily, time). The scheduler's cron triggers match these.
PLANNED: dict[str, tuple[int | None, time]] = {
    "BACKUP": (None, time(2, 0)),
    "ANONYMIZE": (None, time(2, 30)),
    "REMINDERS": (None, time(9, 0)),
    "EXPORT": (0, time(3, 0)),  # Monday
}
CATCH_UP_ORDER = ("BACKUP", "ANONYMIZE", "EXPORT", "REMINDERS")


def _last_planned_on(name: str, now: datetime) -> date | None:
    """The date of the latest planned run at or before ``now``; for a daily
    job only today counts (plan G16)."""
    weekday, planned = PLANNED[name]
    today = now.date()
    if weekday is None:
        return today if now.time() >= planned else None
    day = today - timedelta(days=(today.weekday() - weekday) % 7)
    if day == today and now.time() < planned:
        day -= timedelta(days=7)
    return day


K = TypeVar("K", bound=Hashable)


def jobs_due_for_catch_up(now: datetime, last_success: Mapping[K, date | None]) -> list[K]:
    """Jobs whose latest planned run has no successful run on or after its
    date, in the order BACKUP, ANONYMIZE, EXPORT, REMINDERS.

    ``now`` is local time (Europe/Istanbul). ``last_success`` maps each job
    (``Job`` members, which are strings) to the ``run_on`` of its latest
    SUCCESS; the same keys are returned.
    """
    due = []
    for name in CATCH_UP_ORDER:
        for job, last in last_success.items():
            if job != name:
                continue
            planned_on = _last_planned_on(name, now)
            if planned_on is not None and (last is None or last < planned_on):
                due.append(job)
    return due
