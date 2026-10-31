"""Plain test-data builders (phase 4 small decision 11; no factory_boy)."""

from __future__ import annotations

from datetime import date, datetime, timezone as dt_timezone

from django.db.models import Max

from accounts.models import Role, StaffUser
from members.models import Member

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


def make_member(
    full_name: str | None = "Ayşe Yılmaz",
    phone: str | None = "0555 111 22 33",
    email: str | None = None,
    *,
    member_no: int | None = None,
    is_active: bool = True,
    deactivated_on: date | None = None,
    anonymized: bool = False,
) -> Member:
    """Create a member directly (no actor, no audit).

    ``member_no`` defaults to the next free number. An inactive member gets
    ``deactivated_on`` 2026-10-01 unless given. ``anonymized=True`` builds
    the state that anonymization leaves (FR-25): inactive, personal fields
    NULL, ``anonymized_at`` set.
    """
    if member_no is None:
        member_no = (Member.objects.aggregate(top=Max("member_no"))["top"] or 0) + 1
    anonymized_at = None
    if anonymized:
        full_name = phone = email = None
        is_active = False
        anonymized_at = datetime(2026, 1, 1, tzinfo=dt_timezone.utc)
    if not is_active and deactivated_on is None:
        deactivated_on = date(2026, 10, 1)
    return Member.objects.create(
        member_no=member_no,
        full_name=full_name,
        phone=phone,
        email=email,
        is_active=is_active,
        deactivated_on=deactivated_on,
        anonymized_at=anonymized_at,
    )
