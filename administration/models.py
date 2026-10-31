"""Settings, closed days, audit log and job runs (data-design §2.1, §2.6)."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class LibrarySettings(models.Model):
    """The single settings row, id = 1 (FR-23). Created by migration 0001."""

    loan_period_days = models.PositiveSmallIntegerField("ödünç süresi (gün)", default=14)
    max_open_loans = models.PositiveSmallIntegerField("aynı anda ödünç limiti", default=3)
    daily_fine_kurus = models.PositiveIntegerField("günlük ceza (kuruş)", default=500)
    fine_cap_kurus = models.PositiveIntegerField("ceza üst sınırı (kuruş)", default=15000)
    debt_threshold_kurus = models.PositiveIntegerField("borç eşiği (kuruş)", default=5000)
    retention_years = models.PositiveSmallIntegerField("saklama süresi (yıl)", default=2)
    library_name = models.CharField("kütüphane adı", max_length=80, default="Kütüphane")
    updated_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="+"
    )

    class Meta:
        db_table = "library_settings"
        constraints = [
            models.CheckConstraint(condition=Q(id=1), name="library_settings_single_row"),
            models.CheckConstraint(condition=Q(loan_period_days__gt=0), name="settings_period_gt0"),
            models.CheckConstraint(condition=Q(max_open_loans__gt=0), name="settings_limit_gt0"),
            models.CheckConstraint(
                condition=Q(debt_threshold_kurus__gt=0), name="settings_threshold_gt0"
            ),
            models.CheckConstraint(condition=Q(retention_years__gt=0), name="settings_retention_gt0"),
            models.CheckConstraint(condition=~Q(library_name=""), name="settings_name_not_empty"),
        ]


class WeeklyClosedDay(models.Model):
    """A weekday the library is closed every week; 0 = Monday (FR-24)."""

    weekday = models.PositiveSmallIntegerField(unique=True)

    class Meta:
        db_table = "weekly_closed_day"
        constraints = [
            models.CheckConstraint(
                condition=Q(weekday__gte=0, weekday__lte=6), name="weekly_closed_day_range"
            ),
        ]


class ClosedDate(models.Model):
    """A single closed date (FR-24); excluded from late days (ADR-0040)."""

    date = models.DateField(unique=True)
    note = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = "closed_date"
        ordering = ["date"]


class AuditAction(models.TextChoices):
    """Audited operations: phase 4 small decision 8 plus KL-30 and KL-31."""

    PAYMENT = "PAYMENT", "Ödeme"
    WAIVER = "WAIVER", "Af"
    FEE = "FEE", "Bedel"
    REFUND = "REFUND", "Para iadesi"
    COPY_LOST = "COPY_LOST", "Nüsha kayıp"
    COPY_DAMAGED = "COPY_DAMAGED", "Nüsha hasarlı"
    COPY_FOUND = "COPY_FOUND", "Nüsha bulundu"
    COPY_REPAIRED = "COPY_REPAIRED", "Nüsha onarıldı"
    COPY_WITHDRAWN = "COPY_WITHDRAWN", "Nüsha kayıttan düşüldü"
    SETTINGS_CHANGED = "SETTINGS_CHANGED", "Ayar değişikliği"
    CLOSED_DAY_CHANGED = "CLOSED_DAY_CHANGED", "Kapalı gün değişikliği"
    STAFF_CHANGED = "STAFF_CHANGED", "Personel değişikliği"
    CANCELLATION = "CANCELLATION", "Bedel iptali"
    MEMBER_REACTIVATED = "MEMBER_REACTIVATED", "Üye yeniden aktifleştirildi"


class AuditEvent(models.Model):
    """Append-only audit record (FR-26, phase 3 small decision 10)."""

    occurred_at = models.DateTimeField(default=timezone.now, db_index=True)
    # NULL means a scheduled job.
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT, related_name="+"
    )
    action = models.CharField(max_length=30, choices=AuditAction.choices)
    target_type = models.CharField(max_length=30)
    target_id = models.BigIntegerField()
    details = models.JSONField()

    class Meta:
        db_table = "audit_event"
        ordering = ["-occurred_at", "-id"]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Audit events are never updated")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Audit events are never deleted")


class Job(models.TextChoices):
    BACKUP = "BACKUP", "Günlük yedek"
    ANONYMIZE = "ANONYMIZE", "Anonimleştirme"
    REMINDERS = "REMINDERS", "Hatırlatmalar"
    EXPORT = "EXPORT", "Şifreli dışa aktarma"


class JobRun(models.Model):
    """One run of a scheduled job (KL-1); read by catch-up and the home page."""

    class Status(models.TextChoices):
        RUNNING = "RUNNING", "Çalışıyor"
        SUCCESS = "SUCCESS", "Başarılı"
        FAILED = "FAILED", "Başarısız"

    job = models.CharField(max_length=20, choices=Job.choices)
    run_on = models.DateField()
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=8, choices=Status.choices)
    detail = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "job_run"
        indexes = [models.Index(fields=["job", "run_on"], name="job_run_job_run_on")]
        constraints = [
            models.CheckConstraint(condition=Q(job__in=Job.values), name="job_run_job_valid"),
            models.CheckConstraint(
                condition=Q(status__in=["RUNNING", "SUCCESS", "FAILED"]),
                name="job_run_status_valid",
            ),
        ]
