"""The single source of "today" (phase 4 small decision 9)."""

from datetime import date

from django.utils import timezone


def today() -> date:
    """The current Europe/Istanbul calendar day."""
    return timezone.localdate()
