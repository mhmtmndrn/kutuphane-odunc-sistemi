"""Unit tests for the billing domain (G09): TC-76…TC-79, plus the input
checks of ``allocate_fifo`` (plan G09)."""

from __future__ import annotations

import pytest

from billing.domain import OpenCharge, allocate_fifo, balance

C1, C2 = 11, 12


def test_tc76_balance_of_fine_payment_and_waiver() -> None:
    assert balance([("FINE", 1500), ("PAYMENT", 500), ("WAIVER", 500)]) == 500


def test_tc77_refund_is_balance_neutral_cancellation_is_a_credit() -> None:
    entries = [("FINE", 1500), ("PAYMENT", 500), ("WAIVER", 500), ("REFUND", 2000)]
    assert balance(entries) == 500
    assert balance([*entries, ("CANCELLATION", 300)]) == 200


def test_balance_counts_fees_and_rejects_unknown_kinds() -> None:
    assert balance([("FINE", 100), ("FEE", 12000)]) == 12100
    assert balance([]) == 0
    with pytest.raises(ValueError):
        balance([("BONUS", 1)])


def test_tc78_fifo_fills_the_oldest_charge_first() -> None:
    charges = [OpenCharge(C1, 1500), OpenCharge(C2, 1000)]
    assert allocate_fifo(charges, 2000) == [(C1, 1500), (C2, 500)]


@pytest.mark.parametrize(
    ("amount", "expected"),
    [(1, [(C1, 1)]), (2500, [(C1, 1500), (C2, 1000)])],
)
def test_tc79_fifo_bounds(amount: int, expected: list[tuple[int, int]]) -> None:
    assert allocate_fifo([OpenCharge(C1, 1500), OpenCharge(C2, 1000)], amount) == expected


@pytest.mark.parametrize("amount", [2501, 0, -1])
def test_tc79_fifo_refuses_zero_negative_and_more_than_open(amount: int) -> None:
    with pytest.raises(ValueError):
        allocate_fifo([OpenCharge(C1, 1500), OpenCharge(C2, 1000)], amount)


def test_fifo_keeps_input_order_and_skips_settled_charges() -> None:
    """The input is already ordered (S4); a zero unpaid part gets no allocation."""
    charges = [OpenCharge(C2, 300), OpenCharge(C1, 0), OpenCharge(C1 + 10, 700)]
    assert allocate_fifo(charges, 800) == [(C2, 300), (C1 + 10, 500)]
    with pytest.raises(ValueError):
        allocate_fifo([], 1)
