"""Administration services (plan G03). Each public function is one transaction."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from accounts.models import Role
from accounts.permissions import require_role

from . import clock, domain, jobs
from .audit import AuditAction, record_audit
from .errors import RuleViolation
from .models import AuditEvent, ClosedDate, LibrarySettings, WeeklyClosedDay

WEEKLY_TARGET_ID = 0  # weekly_closed_day events have no single row (KL-15)


@transaction.atomic
def get_settings() -> LibrarySettings:
    """The single settings row; migration 0001 creates it with the defaults."""
    settings, _ = LibrarySettings.objects.get_or_create(pk=1)
    return settings


@require_role(Role.ADMIN)
@transaction.atomic
def update_settings(actor, **changes: object) -> LibrarySettings:
    """Change settings; one SETTINGS_CHANGED event lists every changed field.

    Nothing is written when no value changes. Existing loans keep their due
    dates and fine rate (AC-23, ADR-0023).
    """
    domain.validate_settings(changes)
    settings = get_settings()
    diff = {
        name: {"old": getattr(settings, name), "new": value}
        for name, value in changes.items()
        if getattr(settings, name) != value
    }
    if not diff:
        return settings
    for name, values in diff.items():
        setattr(settings, name, values["new"])
    settings.updated_at = timezone.now()
    settings.updated_by = actor
    settings.save()
    record_audit(actor, AuditAction.SETTINGS_CHANGED, "library_settings", settings.pk, diff)
    return settings


@transaction.atomic
def weekly_closed() -> set[int]:
    return set(WeeklyClosedDay.objects.values_list("weekday", flat=True))


@require_role(Role.ADMIN)
@transaction.atomic
def set_weekly_closed(actor, days: set[int]) -> None:
    """Replace the weekly closed days; all seven are refused (ADR-0028)."""
    domain.validate_weekly_closed(days)
    old = weekly_closed()
    if old == days:
        return
    WeeklyClosedDay.objects.exclude(weekday__in=days).delete()
    WeeklyClosedDay.objects.bulk_create(
        [WeeklyClosedDay(weekday=day) for day in sorted(days - old)]
    )
    record_audit(
        actor,
        AuditAction.CLOSED_DAY_CHANGED,
        "weekly_closed_day",
        WEEKLY_TARGET_ID,
        {"op": "set", "old": sorted(old), "new": sorted(days)},
    )


@require_role(Role.ADMIN)
@transaction.atomic
def add_closed_date(actor, on: date, note: str = "") -> ClosedDate:
    if ClosedDate.objects.filter(date=on).exists():
        raise RuleViolation("Bu tarih zaten kapalı")
    closed = ClosedDate.objects.create(date=on, note=note or None)
    record_audit(
        actor,
        AuditAction.CLOSED_DAY_CHANGED,
        "closed_date",
        closed.pk,
        {"op": "add", "date": on.isoformat(), "note": note},
    )
    return closed


@require_role(Role.ADMIN)
@transaction.atomic
def remove_closed_date(actor, pk: int) -> None:
    closed = ClosedDate.objects.filter(pk=pk).first()
    if closed is None:
        raise RuleViolation("Kapalı tarih bulunamadı")
    closed.delete()
    record_audit(
        actor,
        AuditAction.CLOSED_DAY_CHANGED,
        "closed_date",
        pk,
        {"op": "remove", "date": closed.date.isoformat()},
    )


@transaction.atomic
def closed_date_list() -> list[ClosedDate]:
    return list(ClosedDate.objects.order_by("date"))


@transaction.atomic
def closed_dates() -> frozenset[date]:
    """Single closed dates only, without weekly days (ADR-0040, KL-29)."""
    return frozenset(ClosedDate.objects.values_list("date", flat=True))


def closed_day_predicate() -> Callable[[date], bool]:
    """Read weekly days and dates once; the returned check is O(1)."""
    with transaction.atomic():
        weekly = frozenset(weekly_closed())
        dates = closed_dates()

    def is_closed(day: date) -> bool:
        return day.weekday() in weekly or day in dates

    return is_closed


@require_role(Role.ADMIN)
def audit_events(actor) -> QuerySet[AuditEvent]:
    """Audit log, newest first (KL-11). A lazy queryset for the paginator."""
    return AuditEvent.objects.select_related("actor").order_by("-occurred_at", "-id")


@dataclass(frozen=True)
class AdminHome:
    last_export_on: date | None
    warnings: list[str] = field(default_factory=list)


@require_role(Role.ADMIN)
@transaction.atomic
def admin_home(actor) -> AdminHome:
    """Admin home panel: backup warning first, then export warning (KL-33)."""
    last_backup = jobs.last_finished(jobs.Job.BACKUP)
    backup = domain.backup_warning(
        jobs.last_success_at(jobs.Job.BACKUP),
        last_backup is not None and last_backup.status == last_backup.Status.FAILED,
        timezone.now(),
    )
    last_export_on = jobs.last_success(jobs.Job.EXPORT)
    export = domain.export_age_warning(last_export_on, clock.today())
    return AdminHome(last_export_on, [w for w in (backup, export) if w])
