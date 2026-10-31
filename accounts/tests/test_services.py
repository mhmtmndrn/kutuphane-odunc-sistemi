"""Service-level tests for accounts (G02: TC-11, TC-12; G04 adds staff services)."""

from __future__ import annotations

import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction

from accounts.models import Role, StaffUser
from accounts.permissions import require_role
from tests.support.factories import make_staff

pytestmark = pytest.mark.django_db


@require_role(Role.ADMIN)
def _rename_staff(actor: StaffUser, user: StaffUser, full_name: str) -> None:
    """A stand-in admin service: changes data only when the role check passes."""
    user.first_name = full_name
    user.save(update_fields=["first_name"])


@require_role(Role.CLERK)
def _staff_service(actor: StaffUser) -> str:
    return "ok"


# TC-11 (FR-22, NFR-07): decision table, CLERK vs ADMIN actor.


def test_tc11_clerk_actor_is_denied_and_data_is_unchanged() -> None:
    clerk = make_staff("ali", role=Role.CLERK)
    target = make_staff("veli", full_name="Veli Kaya")
    with pytest.raises(PermissionDenied):
        _rename_staff(clerk, target, "Değişti")
    target.refresh_from_db()
    assert target.first_name == "Veli Kaya"


def test_tc11_admin_actor_performs_the_operation() -> None:
    admin = make_staff("ayse", role=Role.ADMIN)
    target = make_staff("veli", full_name="Veli Kaya")
    _rename_staff(admin, target, "Veli Demir")
    target.refresh_from_db()
    assert target.first_name == "Veli Demir"


def test_require_role_marks_the_wrapped_function() -> None:
    assert _rename_staff.required_role == Role.ADMIN
    assert _staff_service.required_role == Role.CLERK
    assert _rename_staff.__name__ == "_rename_staff"


@pytest.mark.parametrize("role", [Role.CLERK, Role.ADMIN])
def test_clerk_level_service_accepts_every_active_staff(role: Role) -> None:
    assert _staff_service(make_staff("ali", role=role)) == "ok"


@pytest.mark.parametrize("required", [_staff_service, _rename_staff])
def test_inactive_actor_is_denied(required) -> None:
    admin = make_staff("ayse", role=Role.ADMIN, is_active=False)
    args = (admin,) if required is _staff_service else (admin, admin, "x")
    with pytest.raises(PermissionDenied):
        required(*args)


@pytest.mark.parametrize("actor", [None, AnonymousUser()])
def test_missing_or_anonymous_actor_is_denied(actor) -> None:
    with pytest.raises(PermissionDenied):
        _staff_service(actor)


# TC-12 (FR-21, FR-27, small decision 9): password length boundary, G02 part.


def test_tc12_nine_character_password_is_rejected() -> None:
    with pytest.raises(ValidationError) as excinfo:
        validate_password("Kx7#mQ2vL")
    assert any(error.code == "password_too_short" for error in excinfo.value.error_list)


def test_tc12_ten_character_password_is_accepted() -> None:
    validate_password("Kx7#mQ2vLp")


# StaffUser model (data-design §2.1, plan G02 interfaces).


def test_create_superuser_gets_admin_role() -> None:
    user = StaffUser.objects.create_superuser(username="kurucu", password="Kx7#mQ2vLp")
    assert user.role == Role.ADMIN
    assert user.must_change_password is False


def test_create_user_defaults_to_clerk_without_forced_change() -> None:
    user = StaffUser.objects.create_user(username="ali", password="Kx7#mQ2vLp")
    assert user.role == Role.CLERK
    assert user.must_change_password is False


def test_role_check_constraint_rejects_unknown_value() -> None:
    user = make_staff("ali")
    with pytest.raises(IntegrityError), transaction.atomic():
        StaffUser.objects.filter(pk=user.pk).update(role="ROOT")


def test_role_labels_are_turkish() -> None:
    assert Role.ADMIN.label == "Yönetici"
    assert Role.CLERK.label == "Görevli"
