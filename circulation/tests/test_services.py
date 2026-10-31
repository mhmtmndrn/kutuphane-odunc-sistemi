"""Circulation service tests (G11, G12) and the ``Loan`` model's database
constraints (G10, KL-39; data-design §2.4, §4).
"""

from __future__ import annotations

from datetime import date

import pytest
from django.db import IntegrityError, connection, transaction

from accounts.models import StaffUser
from circulation.models import CloseReason, Loan
from tests.support.factories import make_copy, make_member, make_staff

pytestmark = pytest.mark.django_db


# --- Loan model constraints (G10, KL-39) ------------------------------------------


def _loan(**changes: object) -> Loan:
    values: dict[str, object] = {
        "copy": changes.pop("copy", None) or make_copy(),
        "member": make_member(),
        "loaned_on": date(2026, 11, 2),
        "due_on": date(2026, 11, 16),
        "daily_fine_kurus": 500,
        "fine_cap_kurus": 15000,
        "created_by": StaffUser.objects.first() or make_staff(),
    }
    values.update(changes)
    return Loan(**values)  # type: ignore[arg-type]


def _refused(loan: Loan) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        loan.save()


def test_loan_table_and_indexes() -> None:
    """data-design §4: partial unique copy index, (member, closed_on),
    partial due_on and closed_on indexes."""
    with connection.cursor() as cursor:
        indexes = connection.introspection.get_constraints(cursor, "loan")
    columns = {tuple(info["columns"]) for info in indexes.values() if info["index"]}
    assert ("member_id", "closed_on") in columns
    assert ("due_on",) in columns
    assert ("closed_on",) in columns
    with connection.cursor() as cursor:
        cursor.execute("SELECT sql FROM sqlite_master WHERE type = 'index' AND tbl_name = 'loan'")
        sql = " ".join(row[0] or "" for row in cursor.fetchall())
    assert 'CREATE UNIQUE INDEX "loan_one_open_per_copy" ON "loan" ("copy_id") WHERE "closed_on" IS NULL' in sql
    assert 'ON "loan" ("due_on") WHERE "closed_on" IS NULL' in sql


def test_open_loan_is_valid() -> None:
    loan = _loan()
    loan.save()
    assert loan.is_open
    assert loan.member_unlinked_at is None and loan.copy_found_on is None


def test_due_on_must_be_after_loaned_on() -> None:
    _refused(_loan(due_on=date(2026, 11, 2)))


def test_close_reason_and_closed_on_go_together() -> None:
    _refused(_loan(closed_on=date(2026, 11, 10)))
    _refused(_loan(close_reason=CloseReason.RETURNED))
    _refused(_loan(closed_on=date(2026, 11, 10), close_reason="STOLEN"))
    closed = _loan(closed_on=date(2026, 11, 10), close_reason=CloseReason.RETURNED)
    closed.save()
    assert not closed.is_open


def test_copy_found_on_only_for_lost_loans_on_or_after_closing() -> None:
    _refused(
        _loan(
            closed_on=date(2026, 11, 10),
            close_reason=CloseReason.DAMAGED,
            copy_found_on=date(2026, 11, 12),
        )
    )
    _refused(
        _loan(
            closed_on=date(2026, 11, 10),
            close_reason=CloseReason.LOST,
            copy_found_on=date(2026, 11, 9),
        )
    )
    _refused(_loan(copy_found_on=date(2026, 11, 12)))
    found = _loan(
        closed_on=date(2026, 11, 10),
        close_reason=CloseReason.LOST,
        copy_found_on=date(2026, 11, 10),
    )
    found.save()


def test_member_may_be_unlinked() -> None:
    """ADR-0018: the member link becomes NULL after retention."""
    loan = _loan(member=None, closed_on=date(2026, 11, 10), close_reason=CloseReason.RETURNED)
    loan.save()
    assert loan.member is None
