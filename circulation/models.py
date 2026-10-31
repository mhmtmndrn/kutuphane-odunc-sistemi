"""Loans (data-design §2.4). Created in G10 because billing references it (KL-39)."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import F, Q


class CloseReason(models.TextChoices):
    RETURNED = "RETURNED", "İade edildi"
    LOST = "LOST", "Kayıp"
    DAMAGED = "DAMAGED", "Hasarlı"


class Loan(models.Model):
    copy = models.ForeignKey("catalog.Copy", on_delete=models.PROTECT, related_name="loans")
    # NULL after the retention period (ADR-0018).
    member = models.ForeignKey(
        "members.Member", null=True, blank=True, on_delete=models.PROTECT, related_name="loans"
    )
    loaned_on = models.DateField()
    due_on = models.DateField()  # closed-day shift applied (FR-07)
    renewed_on = models.DateField(null=True, blank=True)  # set: renewal used (FR-10)
    # The fine rate at checkout (ADR-0023); kept on renewal (phase 3 small decision 5).
    daily_fine_kurus = models.PositiveIntegerField()
    fine_cap_kurus = models.PositiveIntegerField()
    closed_on = models.DateField(null=True, blank=True)  # NULL: the loan is open
    close_reason = models.CharField(
        max_length=10, choices=CloseReason.choices, null=True, blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="+"
    )
    member_unlinked_at = models.DateTimeField(null=True, blank=True)
    # Written by mark_found for a loan closed as LOST (ADR-0037).
    copy_found_on = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "loan"
        verbose_name = "ödünç"
        verbose_name_plural = "ödünçler"
        constraints = [
            # At most one open loan per copy (data-design §2.4).
            models.UniqueConstraint(
                fields=["copy"],
                condition=Q(closed_on__isnull=True),
                name="loan_one_open_per_copy",
            ),
            models.CheckConstraint(
                condition=Q(due_on__gt=F("loaned_on")), name="loan_due_after_loaned"
            ),
            models.CheckConstraint(
                condition=Q(close_reason__isnull=True) | Q(close_reason__in=CloseReason.values),
                name="loan_close_reason_valid",
            ),
            models.CheckConstraint(
                condition=Q(closed_on__isnull=True, close_reason__isnull=True)
                | Q(closed_on__isnull=False, close_reason__isnull=False),
                name="loan_closed_has_reason",
            ),
            models.CheckConstraint(
                condition=Q(copy_found_on__isnull=True)
                | Q(
                    closed_on__isnull=False,
                    close_reason=CloseReason.LOST,
                    copy_found_on__gte=F("closed_on"),
                ),
                name="loan_found_only_lost",
            ),
        ]
        indexes = [
            models.Index(fields=["member", "closed_on"], name="loan_member_closed"),
            models.Index(
                fields=["due_on"], condition=Q(closed_on__isnull=True), name="loan_open_due"
            ),
            models.Index(fields=["closed_on"], name="loan_closed_on"),
        ]

    def __str__(self) -> str:
        return f"{self.pk}"

    @property
    def is_open(self) -> bool:
        return self.closed_on is None
