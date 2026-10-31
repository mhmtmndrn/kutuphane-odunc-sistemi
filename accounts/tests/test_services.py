"""Service-level tests for accounts (G02: TC-11, TC-12; G04: TC-12, TC-27, TC-29, TC-250, TC-252)."""

from __future__ import annotations

import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction

from accounts import services
from accounts.models import Role, StaffUser
from accounts.permissions import require_role
from administration.audit import AuditAction
from administration.errors import RuleViolation
from administration.models import AuditEvent
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


# =============================================================================
# G04: staff management services (FR-21, FR-26, FR-41, KL-8, KL-32)
# =============================================================================

NEW_PASSWORD = "Yeni-Parola-2026"


def _staff_events() -> list[AuditEvent]:
    return list(AuditEvent.objects.filter(action=AuditAction.STAFF_CHANGED).order_by("id"))


@pytest.fixture
def admin() -> StaffUser:
    return make_staff("ayse.y", role=Role.ADMIN, full_name="Ayşe Yılmaz")


def test_tc27_create_then_promote(admin, client) -> None:
    ali = services.create_staff(admin, "ali", "Ali Yılmaz", Role.CLERK, NEW_PASSWORD)
    assert ali.role == Role.CLERK and ali.first_name == "Ali Yılmaz" and ali.is_active
    services.set_role(admin, ali, Role.ADMIN)
    ali.refresh_from_db()
    assert ali.role == Role.ADMIN

    response = client.post("/giris/", {"username": "ali", "password": NEW_PASSWORD})
    assert response.status_code == 302

    events = _staff_events()
    assert [e.details["change"] for e in events] == ["created", "role"]
    assert all(e.actor == admin and e.target_type == "staff_user" for e in events)
    assert all(e.target_id == ali.pk for e in events)
    assert events[1].details == {"change": "role", "old": "CLERK", "new": "ADMIN"}
    assert all(NEW_PASSWORD not in str(e.details) for e in events)


def test_create_staff_rejects_duplicate_username(admin) -> None:
    services.create_staff(admin, "ali", "Ali Yılmaz", Role.CLERK, NEW_PASSWORD)
    with pytest.raises(RuleViolation, match="kullanıcı adı"):
        services.create_staff(admin, "ali", "Ali Kaya", Role.CLERK, NEW_PASSWORD)
    assert StaffUser.objects.filter(username="ali").count() == 1


def test_create_staff_rejects_invalid_username_and_empty_name(admin) -> None:
    with pytest.raises(RuleViolation):
        services.create_staff(admin, "ali veli", "Ali Veli", Role.CLERK, NEW_PASSWORD)
    with pytest.raises(RuleViolation):
        services.create_staff(admin, "ali", "  ", Role.CLERK, NEW_PASSWORD)
    assert not StaffUser.objects.filter(username__startswith="ali").exists()


def test_tc29_reset_password(admin) -> None:
    ali = make_staff("ali")
    services.reset_password(admin, ali, NEW_PASSWORD)
    ali.refresh_from_db()
    assert not ali.check_password("Kitap-Rafi-2026")
    assert ali.check_password(NEW_PASSWORD)
    assert ali.must_change_password is True
    assert _staff_events()[-1].details == {"change": "password_reset"}


def test_tc12_create_staff_password_length(admin) -> None:
    with pytest.raises(RuleViolation):
        services.create_staff(admin, "ali", "Ali Yılmaz", Role.CLERK, "Kx7#mQ2vL")
    assert not StaffUser.objects.filter(username="ali").exists()
    assert _staff_events() == []
    services.create_staff(admin, "ali", "Ali Yılmaz", Role.CLERK, "Kx7#mQ2vLp")
    assert StaffUser.objects.filter(username="ali").exists()


def test_tc12_reset_password_length(admin) -> None:
    ali = make_staff("ali")
    with pytest.raises(RuleViolation):
        services.reset_password(admin, ali, "Kx7#mQ2vL")
    ali.refresh_from_db()
    assert ali.check_password("Kitap-Rafi-2026")
    assert ali.must_change_password is False
    services.reset_password(admin, ali, "Kx7#mQ2vLp")
    ali.refresh_from_db()
    assert ali.check_password("Kx7#mQ2vLp")


def test_tc250_must_change_flag_by_creation_path(admin) -> None:
    created = services.create_staff(admin, "ali", "Ali Yılmaz", Role.CLERK, NEW_PASSWORD)
    assert created.must_change_password is True

    veli = make_staff("veli")
    services.reset_password(admin, veli, NEW_PASSWORD)
    veli.refresh_from_db()
    assert veli.must_change_password is True

    call_command(
        "createsuperuser",
        interactive=False,
        username="kurucu",
        email="kurucu@example.invalid",
        verbosity=0,
    )
    founder = StaffUser.objects.get(username="kurucu")
    assert founder.must_change_password is False
    assert founder.role == Role.ADMIN


def test_change_own_password_clears_flag_and_audits_self() -> None:
    ali = make_staff("ali", must_change_password=True)
    services.change_own_password(ali, NEW_PASSWORD)
    ali.refresh_from_db()
    assert ali.check_password(NEW_PASSWORD)
    assert ali.must_change_password is False
    event = _staff_events()[-1]
    assert event.actor == ali
    assert event.details == {"change": "password_changed"}


def test_deactivate_staff(admin) -> None:
    ali = make_staff("ali")
    services.deactivate_staff(admin, ali)
    ali.refresh_from_db()
    assert ali.is_active is False
    assert _staff_events()[-1].details == {"change": "deactivated"}


def test_unlock_staff_resets_axes_attempts(admin, client) -> None:
    ali = make_staff("ali")
    for _ in range(5):
        client.post("/giris/", {"username": "ali", "password": "Yanlis-Parola-99"})
    assert client.post("/giris/", {"username": "ali", "password": "Kitap-Rafi-2026"}).status_code == 429
    services.unlock_staff(admin, ali)
    assert client.post("/giris/", {"username": "ali", "password": "Kitap-Rafi-2026"}).status_code == 302
    assert _staff_events()[-1].details == {"change": "unlocked"}


def test_set_same_role_writes_nothing(admin) -> None:
    ali = make_staff("ali")
    services.set_role(admin, ali, Role.CLERK)
    assert _staff_events() == []


@pytest.mark.parametrize(
    "call",
    [
        lambda actor, user: services.create_staff(actor, "yeni", "Yeni", Role.CLERK, NEW_PASSWORD),
        lambda actor, user: services.set_role(actor, user, Role.ADMIN),
        lambda actor, user: services.deactivate_staff(actor, user),
        lambda actor, user: services.reset_password(actor, user, NEW_PASSWORD),
        lambda actor, user: services.unlock_staff(actor, user),
    ],
)
def test_staff_services_require_admin(call) -> None:
    clerk = make_staff("ali")
    other = make_staff("veli")
    with pytest.raises(PermissionDenied):
        call(clerk, other)
    other.refresh_from_db()
    assert other.role == Role.CLERK and other.is_active
    assert _staff_events() == []


# --- TC-252: last admin and self-deactivation (KL-8) -------------------------


def test_tc252_single_admin_cannot_become_clerk(admin) -> None:
    with pytest.raises(RuleViolation) as excinfo:
        services.set_role(admin, admin, Role.CLERK)
    assert excinfo.value.message == "En az bir aktif yönetici kalmalı"
    admin.refresh_from_db()
    assert admin.role == Role.ADMIN
    assert _staff_events() == []


def test_tc252_one_of_two_admins_can_become_clerk(admin) -> None:
    other = make_staff("mehmet", role=Role.ADMIN)
    services.set_role(admin, other, Role.CLERK)
    other.refresh_from_db()
    assert other.role == Role.CLERK


def test_tc252_admin_cannot_deactivate_self(admin) -> None:
    make_staff("mehmet", role=Role.ADMIN)
    with pytest.raises(RuleViolation) as excinfo:
        services.deactivate_staff(admin, admin)
    assert excinfo.value.message == "Kendi hesabınızı pasifleştiremezsiniz"
    admin.refresh_from_db()
    assert admin.is_active
    assert _staff_events() == []


def test_inactive_admin_does_not_count_as_active(admin) -> None:
    # An inactive admin does not count (KL-8: "aktif").
    other = make_staff("mehmet", role=Role.ADMIN, is_active=False)
    clerk_admin = make_staff("veli", role=Role.ADMIN)
    services.deactivate_staff(admin, clerk_admin)
    with pytest.raises(RuleViolation, match="En az bir aktif yönetici kalmalı"):
        services.set_role(admin, admin, Role.CLERK)
    other.refresh_from_db()
    assert other.is_active is False
