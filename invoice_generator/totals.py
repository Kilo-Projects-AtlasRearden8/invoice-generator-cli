"""Totals and tax math helpers used across the package and CLI."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from .models import Invoice, Money


def tax_amount(subtotal: Money, tax_rate: Decimal) -> Money:
    """Compute tax for a subtotal at the given rate, rounded half-up to cents."""
    raw = (subtotal.amount * tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Money(raw)


def invoice_totals(invoice: Invoice) -> dict[str, Money]:
    """Return subtotal, tax, and total for an invoice."""
    subtotal = invoice.subtotal()
    tax = tax_amount(subtotal, invoice.tax_rate)
    total = Money((subtotal.amount + tax.amount).quantize(Decimal("0.01")))
    return {"subtotal": subtotal, "tax": tax, "total": total}


def format_money(amount: Money | Decimal) -> str:
    if isinstance(amount, Money):
        amount = amount.amount
    return f"{Decimal(amount):.2f}"
