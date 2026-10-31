"""Staff account services (plan G04, FR-21, FR-41, ADR-0043, KL-8).

Every function writes a STAFF_CHANGED audit event whose ``details["change"]``
names the operation; a password never reaches the audit log.
"""

from __future__ import annotations

from axes.utils import reset as reset_axes_attempts
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from administration.audit import AuditAction, record_audit
from administration.errors import RuleViolation

from .models import Role, StaffUser
from .permissions import require_role

LAST_ADMIN_MESSAGE = "En az bir aktif yönetici kalmalı"
SELF_DEACTIVATE_MESSAGE = "Kendi hesabınızı pasifleştiremezsiniz"


def _audit(actor: StaffUser, user: StaffUser, change: str, **extra: object) -> None:
    record_audit(
        actor, AuditAction.STAFF_CHANGED, "staff_user", user.pk, {"change": change, **extra}
    )


def _check_password(password: str, user: StaffUser) -> None:
    try:
        validate_password(password, user)
    except ValidationError as exc:
        raise RuleViolation(" ".join(exc.messages)) from None


def _other_active_admins(user: StaffUser) -> bool:
    return (
        StaffUser.objects.filter(role=Role.ADMIN, is_active=True).exclude(pk=user.pk).exists()
    )


@require_role(Role.ADMIN)
@transaction.atomic
def create_staff(
    actor: StaffUser, username: str, full_name: str, role: Role, password: str
) -> StaffUser:
    username = username.strip()
    full_name = full_name.strip()
    if not full_name:
        raise RuleViolation("Ad soyad boş olamaz")
    try:
        StaffUser.username_validator(username)
    except ValidationError:
        raise RuleViolation(
            "Kullanıcı adı yalnız harf, rakam ve @ . + - _ karakterlerinden oluşabilir"
        ) from None
    if StaffUser.objects.filter(username=username).exists():
        raise RuleViolation("Bu kullanıcı adı zaten kullanılıyor")
    user = StaffUser(username=username, first_name=full_name, role=role, must_change_password=True)
    _check_password(password, user)
    user.set_password(password)
    user.save()
    _audit(actor, user, "created", username=username, role=str(role))
    return user


@require_role(Role.ADMIN)
@transaction.atomic
def set_role(actor: StaffUser, user: StaffUser, role: Role) -> None:
    if user.role == role:
        return
    if user.role == Role.ADMIN and user.is_active and not _other_active_admins(user):
        raise RuleViolation(LAST_ADMIN_MESSAGE)
    old = user.role
    user.role = role
    user.save(update_fields=["role"])
    _audit(actor, user, "role", old=str(old), new=str(role))


@require_role(Role.ADMIN)
@transaction.atomic
def deactivate_staff(actor: StaffUser, user: StaffUser) -> None:
    """Deactivate an account; its open session ends on the next request (KL-45)."""
    if user.pk == actor.pk:
        raise RuleViolation(SELF_DEACTIVATE_MESSAGE)
    if not user.is_active:
        return
    if user.role == Role.ADMIN and not _other_active_admins(user):
        raise RuleViolation(LAST_ADMIN_MESSAGE)
    user.is_active = False
    user.save(update_fields=["is_active"])
    _audit(actor, user, "deactivated")


@require_role(Role.ADMIN)
@transaction.atomic
def reset_password(actor: StaffUser, user: StaffUser, new_password: str) -> None:
    """Set a password the staff member must change at first login (ADR-0043)."""
    _check_password(new_password, user)
    user.set_password(new_password)
    user.must_change_password = True
    user.save(update_fields=["password", "must_change_password"])
    _audit(actor, user, "password_reset")


@require_role(Role.ADMIN)
@transaction.atomic
def unlock_staff(actor: StaffUser, user: StaffUser) -> None:
    """Lift the login lockout without waiting 15 minutes (ADR-0009)."""
    reset_axes_attempts(username=user.username)
    _audit(actor, user, "unlocked")


@require_role(Role.CLERK)
@transaction.atomic
def change_own_password(user: StaffUser, new_password: str) -> None:
    """The staff member's own change (KL-32); the view validates the form first."""
    _check_password(new_password, user)
    user.set_password(new_password)
    user.must_change_password = False
    user.save(update_fields=["password", "must_change_password"])
    _audit(user, user, "password_changed")


@require_role(Role.ADMIN)
@transaction.atomic
def staff_list(actor: StaffUser) -> list[StaffUser]:
    return list(StaffUser.objects.order_by("username"))


@require_role(Role.ADMIN)
@transaction.atomic
def get_staff(actor: StaffUser, pk: int) -> StaffUser:
    """Raises ``StaffUser.DoesNotExist``; the view turns it into 404."""
    return StaffUser.objects.get(pk=pk)
