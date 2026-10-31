"""Plain test-data builders (phase 4 small decision 11; no factory_boy)."""

from __future__ import annotations

from accounts.models import Role, StaffUser

# Ten characters or more and not a common password (KL-9).
DEFAULT_PASSWORD = "Kitap-Rafi-2026"


def make_staff(
    username: str = "ali",
    *,
    role: Role = Role.CLERK,
    password: str = DEFAULT_PASSWORD,
    full_name: str = "Ali Yılmaz",
    is_active: bool = True,
    must_change_password: bool = False,
) -> StaffUser:
    """Create a staff account. ``full_name`` is kept in ``first_name`` (plan §11, G02 (c))."""
    return StaffUser.objects.create_user(
        username=username,
        password=password,
        role=role,
        first_name=full_name,
        is_active=is_active,
        must_change_password=must_change_password,
    )
