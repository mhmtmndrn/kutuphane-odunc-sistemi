"""Staff accounts and roles (data-design §2.1, phase 3 small decision 1)."""

from __future__ import annotations

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class Role(models.TextChoices):
    ADMIN = "ADMIN", "Yönetici"
    CLERK = "CLERK", "Görevli"


class StaffUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        # The first administrator is created with ``createsuperuser``.
        extra_fields.setdefault("role", Role.ADMIN)
        return super().create_superuser(username, email, password, **extra_fields)


class StaffUser(AbstractUser):
    """A library staff account. ``first_name`` holds the full name (plan §11, G02 (c))."""

    role = models.CharField("rol", max_length=10, choices=Role.choices, default=Role.CLERK)
    # Set by create_staff and reset_password; cleared by the user's own change (ADR-0043).
    must_change_password = models.BooleanField("parola değişmeli", default=False)

    objects = StaffUserManager()

    class Meta:
        db_table = "staff_user"
        verbose_name = "personel"
        verbose_name_plural = "personel"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(role__in=Role.values),
                name="staff_user_role_valid",
            ),
        ]

