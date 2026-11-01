"""Shared helpers of the operations commands (G14–G16 small decision 1)."""

from __future__ import annotations

from datetime import date, datetime

from django.core.management.base import CommandError

from administration import clock

from .backup import OperationError
from .libx import LibxError

DATE_HELP = "YYYY-MM-DD; varsayılan bugün"


def run_on_option(value: str | None) -> date:
    """``--date`` read strictly; invalid values fail before any ``job_run``
    row is written (G13 tradition)."""
    if value is None:
        return clock.today()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise CommandError(f"Geçersiz tarih: {value}") from None


def command_error(exc: Exception, prefix: str) -> CommandError:
    """Expected failures keep their own message; others get ``prefix``."""
    if isinstance(exc, (OperationError, LibxError)):
        return CommandError(str(exc))
    return CommandError(f"{prefix}: {type(exc).__name__}: {exc}")
