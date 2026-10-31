"""Books and copies (data-design §2.3)."""

from __future__ import annotations

from django.db import models
from django.db.models import Q
from django.db.models.functions import Length
from django.db.models.lookups import Exact
from django.utils import timezone

from .domain import normalize_tr


class Book(models.Model):
    title = models.CharField("başlık", max_length=300)
    author = models.CharField("yazar", max_length=300)
    # Hyphen-free, validated ISBN-13 (ADR-0008); not unique.
    isbn13 = models.CharField("ISBN", max_length=13, null=True, blank=True, db_index=True)
    publisher = models.CharField("yayınevi", max_length=200, null=True, blank=True)
    year = models.PositiveSmallIntegerField("yıl", null=True, blank=True)
    source_ol_id = models.CharField(max_length=30, null=True, blank=True)  # seed data (AC-29)
    search_key = models.CharField(max_length=700)

    class Meta:
        db_table = "book"
        verbose_name = "kitap"
        verbose_name_plural = "kitaplar"
        constraints = [
            models.CheckConstraint(
                condition=Q(isbn13__isnull=True) | Q(Exact(Length("isbn13"), 13)),
                name="book_isbn13_length",
            ),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        # The derived search column is written in one place (ADR-0019).
        self.search_key = normalize_tr(f"{self.title} {self.author}")
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            kwargs["update_fields"] = {*update_fields, "search_key"}
        super().save(*args, **kwargs)


class CopyStatus(models.TextChoices):
    """FR-05 copy states; transitions are in architecture §5.1 (G10, G12)."""

    ON_SHELF = "ON_SHELF", "Rafta"
    ON_LOAN = "ON_LOAN", "Ödünçte"
    LOST = "LOST", "Kayıp"
    DAMAGED = "DAMAGED", "Hasarlı"
    WITHDRAWN = "WITHDRAWN", "Kayıttan düşmüş"


class Copy(models.Model):
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="copies")
    # f"{id:08d}", set right after the insert in the same transaction
    # (phase 3 small decision 3).
    barcode = models.CharField("barkod", max_length=8, unique=True)
    status = models.CharField(
        "durum", max_length=12, choices=CopyStatus.choices, default=CopyStatus.ON_SHELF
    )
    # Set on insert and on every status change (plan G07).
    status_changed_at = models.DateTimeField()

    class Meta:
        db_table = "copy"
        verbose_name = "nüsha"
        verbose_name_plural = "nüshalar"
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=CopyStatus.values), name="copy_status_valid"
            ),
        ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._saved_status = None if self._state.adding else self.status

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._saved_status = instance.status
        return instance

    def __str__(self) -> str:
        return self.barcode

    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.status_changed_at is None:
                self.status_changed_at = timezone.now()
        elif self.status != self._saved_status:
            self.status_changed_at = timezone.now()
            update_fields = kwargs.get("update_fields")
            if update_fields is not None:
                kwargs["update_fields"] = {*update_fields, "status_changed_at"}
        super().save(*args, **kwargs)
        self._saved_status = self.status
