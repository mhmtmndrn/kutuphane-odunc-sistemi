"""The ledger: entries and allocations (data-design §2.5, ADR-0016, ADR-0017).

Entries and allocations are append-only (I6): ``save`` refuses updates and
``delete`` refuses deletion. The single exception, retention clearing
``ledger_entry.loan_id`` (ADR-0018, G15), uses a queryset update.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class EntryKind(models.TextChoices):
    FINE = "FINE", "Ceza"
    FEE = "FEE", "Bedel"
    PAYMENT = "PAYMENT", "Ödeme"
    WAIVER = "WAIVER", "Af"
    CANCELLATION = "CANCELLATION", "İptal"
    REFUND = "REFUND", "Para iadesi"


TARGETED_KINDS = (EntryKind.WAIVER, EntryKind.CANCELLATION, EntryKind.REFUND)


class _AppendOnly(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Ledger rows are never updated (I6)")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Ledger rows are never deleted (I6)")


class LedgerEntry(_AppendOnly):
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="ledger_entries"
    )
    # Set for FINE and FEE; NULL after retention (ADR-0018).
    loan = models.ForeignKey(
        "circulation.Loan",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="ledger_entries",
    )
    kind = models.CharField(max_length=12, choices=EntryKind.choices)
    amount_kurus = models.PositiveIntegerField()  # the direction comes from the kind
    target_entry = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="targeted_by"
    )
    reason = models.CharField(max_length=500, null=True, blank=True)
    # Set in save() so the tests' FrozenClock applies (plan §11, G07).
    created_at = models.DateTimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )

    class Meta:
        db_table = "ledger_entry"
        verbose_name = "borç hareketi"
        verbose_name_plural = "borç hareketleri"
        constraints = [
            models.CheckConstraint(
                condition=Q(kind__in=EntryKind.values), name="ledger_entry_kind_valid"
            ),
            models.CheckConstraint(condition=Q(amount_kurus__gt=0), name="ledger_entry_amount_gt0"),
            models.CheckConstraint(
                condition=~Q(kind__in=TARGETED_KINDS) | Q(target_entry__isnull=False),
                name="ledger_entry_target_required",
            ),
            models.CheckConstraint(
                condition=~Q(kind=EntryKind.WAIVER) | (Q(reason__isnull=False) & ~Q(reason="")),
                name="ledger_entry_waiver_reason",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.kind} {self.amount_kurus}"

    def save(self, *args, **kwargs):
        if self.created_at is None:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)


class Allocation(_AppendOnly):
    """A credit (PAYMENT, WAIVER, CANCELLATION) settling part of a charge."""

    credit_entry = models.ForeignKey(
        LedgerEntry, on_delete=models.PROTECT, related_name="credit_allocations"
    )
    charge_entry = models.ForeignKey(
        LedgerEntry, on_delete=models.PROTECT, related_name="charge_allocations"
    )
    amount_kurus = models.PositiveIntegerField()

    class Meta:
        db_table = "allocation"
        constraints = [
            models.CheckConstraint(condition=Q(amount_kurus__gt=0), name="allocation_amount_gt0"),
            models.UniqueConstraint(
                fields=["credit_entry", "charge_entry"], name="allocation_credit_charge_unique"
            ),
        ]
