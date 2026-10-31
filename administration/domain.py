"""Pure administration rules: no ORM, HTTP or clock calls (ADR-0015)."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timedelta

from .errors import RuleViolation

BACKUP_MAX_AGE = timedelta(hours=26)  # 02:00 daily run plus two hours (ADR-0044)
EXPORT_MAX_AGE_DAYS = 7  # KL-14

# Inclusive bounds for numeric settings (plan G03) and their messages.
SETTING_BOUNDS: Mapping[str, tuple[int, int | None, str]] = {
    "loan_period_days": (1, 365, "Ödünç süresi 1 ile 365 gün arasında olmalı"),
    "max_open_loans": (1, 20, "Ödünç limiti 1 ile 20 arasında olmalı"),
    "daily_fine_kurus": (0, None, "Günlük ceza negatif olamaz"),
    "fine_cap_kurus": (0, None, "Ceza üst sınırı negatif olamaz"),
    "debt_threshold_kurus": (1, None, "Borç eşiği 0,00 TL'den büyük olmalı"),
    "retention_years": (1, 10, "Saklama süresi 1 ile 10 yıl arasında olmalı"),
}
LIBRARY_NAME_MAX = 80
LIBRARY_NAME_MESSAGE = "Kütüphane adı 1 ile 80 karakter arasında olmalı"
SETTING_FIELDS = frozenset({*SETTING_BOUNDS, "library_name"})


def validate_settings(values: Mapping[str, object]) -> None:
    """Check proposed setting values; raise ``RuleViolation`` on the first bad one.

    Unknown names raise ``TypeError``: they are programming errors, not input.
    """
    unknown = set(values) - SETTING_FIELDS
    if unknown:
        raise TypeError(f"Unknown settings: {sorted(unknown)}")
    for name, value in values.items():
        if name == "library_name":
            # A whitespace-only name counts as empty.
            if (
                not isinstance(value, str)
                or not value.strip()
                or len(value) > LIBRARY_NAME_MAX
            ):
                raise RuleViolation(LIBRARY_NAME_MESSAGE)
            continue
        low, high, message = SETTING_BOUNDS[name]
        if not isinstance(value, int) or value < low or (high is not None and value > high):
            raise RuleViolation(message)


def validate_weekly_closed(days: set[int]) -> None:
    """At least one weekday stays open (FR-24, ADR-0028). 0 is Monday."""
    if any(not 0 <= day <= 6 for day in days):
        raise ValueError(f"Weekdays must be 0-6: {sorted(days)}")
    if len(days) == 7:
        raise RuleViolation("En az bir gün açık kalmalı")


def export_age_warning(last_export_on: date | None, today: date) -> str | None:
    """Off-site export warning for the admin home page (FR-37, KL-14)."""
    if last_export_on is None:
        return "Bina dışı yedek henüz alınmadı"
    if (today - last_export_on).days > EXPORT_MAX_AGE_DAYS:
        return "Bina dışı yedek 7 günden eski"
    return None


def backup_warning(
    last_success_at: datetime | None, last_finished_failed: bool, now: datetime
) -> str | None:
    """Daily backup warning, rules in ADR-0044 order (FR-42)."""
    if last_finished_failed:
        return "Son günlük yedek başarısız oldu"
    if last_success_at is None:
        return "Günlük yedek henüz alınmadı"
    if now - last_success_at > BACKUP_MAX_AGE:
        return "Günlük yedek 26 saatten eski"
    return None
