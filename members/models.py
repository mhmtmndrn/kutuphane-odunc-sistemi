"""Members and consent history (data-design §2.2, ADR-0022, ADR-0047)."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from catalog.domain import normalize_tr

from .domain import phone_digits


class Member(models.Model):
    """A library member. Only the FR-01 personal fields are kept (NFR-08)."""

    member_no = models.PositiveIntegerField("üye no", unique=True)
    full_name = models.CharField("ad soyad", max_length=200, null=True, blank=True)
    phone = models.CharField("telefon", max_length=30, null=True, blank=True)
    phone_digits = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    email = models.EmailField("e-posta", max_length=254, null=True, blank=True)
    search_key = models.CharField(max_length=400)
    is_active = models.BooleanField(default=True)
    deactivated_on = models.DateField(null=True, blank=True)
    # Denormalized from the current consent event (ADR-0022).
    has_email_consent = models.BooleanField(default=False)
    archived_loan_count = models.PositiveIntegerField(default=0)  # ADR-0018
    anonymized_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "member"
        verbose_name = "üye"
        verbose_name_plural = "üyeler"
        constraints = [
            models.CheckConstraint(
                condition=Q(is_active=True) | Q(deactivated_on__isnull=False),
                name="member_inactive_has_date",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.member_no}"

    def save(self, *args, **kwargs):
        # The derived search columns are written in one place (ADR-0019).
        self.search_key = normalize_tr(self.full_name or "")
        self.phone_digits = phone_digits(self.phone) if self.phone is not None else None
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            kwargs["update_fields"] = {*update_fields, "search_key", "phone_digits"}
        super().save(*args, **kwargs)

    @property
    def is_anonymized(self) -> bool:
        return self.anonymized_at is not None


class ConsentAction(models.TextChoices):
    GIVEN = "GIVEN", "Rıza verildi"
    WITHDRAWN = "WITHDRAWN", "Rıza geri alındı"


# ADR-0047: the current state is the event with the largest
# (effective_on, recorded_at, id).
CONSENT_ORDER = ("-effective_on", "-recorded_at", "-id")


class ConsentEvent(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="consent_events")
    action = models.CharField(max_length=10, choices=ConsentAction.choices)
    effective_on = models.DateField()
    recorded_at = models.DateTimeField(default=timezone.now)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )

    class Meta:
        db_table = "consent_event"
        constraints = [
            models.CheckConstraint(
                condition=Q(action__in=ConsentAction.values), name="consent_event_action_valid"
            ),
        ]
