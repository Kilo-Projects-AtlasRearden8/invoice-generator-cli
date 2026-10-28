"""Tests for invoice totals and tax math."""

from __future__ import annotations

from decimal import Decimal

from invoice_generator.models import Client, Invoice, LineItem, Money
from invoice_generator.totals import invoice_totals, tax_amount


def _invoice(items, tax_rate="0.00"):
    return Invoice(
        invoice_number="INV-001",
        invoice_date="2026-10-01",
        client=Client(name="Test Client"),
        items=items,
        tax_rate=Decimal(tax_rate),
    )


def test_subtotal_single_item():
    inv = _invoice([LineItem("Widget", Decimal(2), Money(Decimal("10.00")))])
    totals = invoice_totals(inv)
    assert totals["subtotal"] == Money(Decimal("20.00"))


def test_subtotal_multiple_items():
    inv = _invoice(
        [
            LineItem("A", Decimal(1), Money(Decimal("5.00"))),
            LineItem("B", Decimal(3), Money(Decimal("2.50"))),
            LineItem("C", Decimal(2), Money(Decimal("7.00"))),
        ]
    )
    totals = invoice_totals(inv)
    assert totals["subtotal"] == Money(Decimal("26.50"))


def test_tax_at_8_percent():
    inv = _invoice([LineItem("Widget", Decimal(1), Money(Decimal("100.00")))], "0.08")
    totals = invoice_totals(inv)
    assert totals["tax"] == Money(Decimal("8.00"))


def test_tax_rounds_half_up_to_cents():
    # 0.005 rounds up to 0.01
    inv = _invoice([LineItem("X", Decimal(1), Money(Decimal("0.05")))], "0.10")
    totals = invoice_totals(inv)
    assert totals["tax"] == Money(Decimal("0.01"))


def test_total_is_subtotal_plus_tax():
    inv = _invoice(
        [
            LineItem("A", Decimal(2), Money(Decimal("10.00"))),
            LineItem("B", Decimal(1), Money(Decimal("5.50"))),
        ],
        "0.10",
    )
    totals = invoice_totals(inv)
    assert totals["total"] == Money(Decimal("25.50") + Decimal("2.55"))


def test_empty_invoice_totals_zero():
    inv = _invoice([], "0.08")
    totals = invoice_totals(inv)
    assert totals["subtotal"] == Money(Decimal("0.00"))
    assert totals["tax"] == Money(Decimal("0.00"))
    assert totals["total"] == Money(Decimal("0.00"))


def test_tax_amount_helper_direct():
    assert tax_amount(Money(Decimal("100.00")), Decimal("0.08")) == Money(
        Decimal("8.00")
    )
    assert tax_amount(Money(Decimal("33.33")), Decimal("0.07")) == Money(
        Decimal("2.33")
    )
