"""Audit log writer (FR-26). Called inside the caller's transaction."""

from __future__ import annotations

from typing import Any

from .models import AuditAction, AuditEvent

__all__ = ["AuditAction", "record_audit"]

# Small decision 10: a single event never names both a member and a loan.
_MEMBER_KEYS = frozenset({"member", "member_no", "member_id"})
_LOAN_KEYS = frozenset({"loan", "loan_id"})


def record_audit(
    actor: Any,
    action: AuditAction,
    target_type: str,
    target_id: int,
    details: dict[str, Any],
) -> AuditEvent:
    """Write one audit event. ``actor`` is None for scheduled jobs."""
    if _MEMBER_KEYS & details.keys() and _LOAN_KEYS & details.keys():
        raise ValueError("Audit details must not hold both a member and a loan")
    return AuditEvent.objects.create(
        actor=actor,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details,
    )
