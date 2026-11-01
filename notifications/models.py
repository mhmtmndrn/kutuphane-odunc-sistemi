"""Reminder log (data-design §2.6, ADR-0039)."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from .domain import ReminderKind


class ReminderStatus(models.TextChoices):
    SENT = "SENT", "Gönderildi"
    FAILED = "FAILED", "Gönderilemedi"


class ReminderLog(models.Model):
    # No member column: the member comes from the loan (ADR-0018).
    loan = models.ForeignKey("circulation.Loan", on_delete=models.PROTECT, related_name="+")
    kind = models.CharField(max_length=10, choices=ReminderKind.choices)
    status = models.CharField(max_length=6, choices=ReminderStatus.choices)
    error = models.CharField(max_length=500, null=True, blank=True)
    sent_at = models.DateTimeField()  # time of the attempt
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="+"
    )  # set for MANUAL (FR-19)
    due_on = models.DateField()  # loan.due_on at the attempt, MANUAL too (ADR-0039)

    class Meta:
        db_table = "reminder_log"
        constraints = [
            models.CheckConstraint(
                condition=Q(kind__in=ReminderKind.values), name="reminder_log_kind_valid"
            ),
            models.CheckConstraint(
                condition=Q(status__in=ReminderStatus.values), name="reminder_log_status_valid"
            ),
            # FR-18 repeat guard, per due date (phase 3 small decision 7, ADR-0039).
            models.UniqueConstraint(
                fields=["loan", "kind", "due_on"],
                condition=Q(status="SENT") & ~Q(kind="MANUAL"),
                name="reminder_log_one_sent_per_due",
            ),
        ]

    def save(self, *args, **kwargs):
        # Set here, not as a field default, so frozen test clocks apply.
        if self.sent_at is None:
            self.sent_at = timezone.now()
        super().save(*args, **kwargs)
