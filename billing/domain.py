"""Pure ledger rules (plan G09): balance and FIFO allocation.

No ORM, HTTP or clock calls (ADR-0015). Amounts are integer kuruş (ADR-0016).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

__all__ = ["CHARGE_KINDS", "CREDIT_KINDS", "OpenCharge", "allocate_fifo", "balance"]

CHARGE_KINDS = frozenset({"FINE", "FEE"})
CREDIT_KINDS = frozenset({"PAYMENT", "WAIVER", "CANCELLATION"})
# REFUND is balance-neutral (ADR-0020).
_NEUTRAL_KINDS = frozenset({"REFUND"})


@dataclass(frozen=True)
class OpenCharge:
    """A FINE or FEE with its unpaid part (I4)."""

    id: int
    unpaid: int


def balance(entries: Iterable[tuple[str, int]]) -> int:
    """Σ FINE, FEE − Σ PAYMENT, WAIVER, CANCELLATION; REFUND counts 0 (I1)."""
    total = 0
    for kind, amount in entries:
        if kind in CHARGE_KINDS:
            total += amount
        elif kind in CREDIT_KINDS:
            total -= amount
        elif kind not in _NEUTRAL_KINDS:
            raise ValueError(f"unknown ledger kind: {kind!r}")
    return total


def allocate_fifo(open_charges: list[OpenCharge], amount: int) -> list[tuple[int, int]]:
    """Spread ``amount`` over the charges in the given order (ADR-0017); O(k).

    Raises ``ValueError`` when ``amount <= 0`` or ``amount > Σ unpaid``.
    """
    if amount <= 0:
        raise ValueError("amount must be positive")
    if amount > sum(charge.unpaid for charge in open_charges):
        raise ValueError("amount exceeds the open charges")
    allocations: list[tuple[int, int]] = []
    rest = amount
    for charge in open_charges:
        if rest == 0:
            break
        part = min(charge.unpaid, rest)
        if part > 0:
            allocations.append((charge.id, part))
            rest -= part
    return allocations
