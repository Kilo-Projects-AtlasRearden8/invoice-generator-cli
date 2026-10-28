"""Core data models for invoices, clients, and line items.

All currency math uses :class:`decimal.Decimal` so totals and tax are exact
and never suffer from floating-point drift.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

CENT = Decimal("0.01")


@dataclass
class Money:
    """A monetary value stored as a Decimal."""

    amount: Decimal

    @classmethod
    def from_str(cls, value: str) -> Money:
        return cls(Decimal(value))

    def quantized(self) -> Money:
        return Money(self.amount.quantize(CENT))

    def __add__(self, other: Money) -> Money:
        return Money(self.amount + other.amount)

    def __mul__(self, factor: Decimal) -> Money:
        return Money(self.amount * factor)

    def __str__(self) -> str:
        return f"{self.amount:.2f}"

    def __repr__(self) -> str:
        return f"Money({self.amount!r})"


@dataclass
class LineItem:
    """A single line on an invoice."""

    description: str
    quantity: Decimal
    unit_price: Money

    def line_total(self) -> Money:
        return Money((self.quantity * self.unit_price.amount).quantize(CENT))


@dataclass
class Client:
    """The client being billed."""

    name: str
    email: str | None = None
    address: str | None = None


@dataclass
class Invoice:
    """An invoice with client info, line items, and a tax rate."""

    invoice_number: str
    invoice_date: str
    client: Client
    items: list[LineItem] = field(default_factory=list)
    tax_rate: Decimal = Decimal("0.00")

    def subtotal(self) -> Money:
        total = Decimal(0)
        for item in self.items:
            total += item.line_total().amount
        return Money(total.quantize(CENT))

    def tax(self) -> Money:
        return Money((self.subtotal().amount * self.tax_rate).quantize(CENT))

    def total(self) -> Money:
        return self.subtotal() + self.tax()


def build_invoice(
    invoice_number: str,
    invoice_date: str,
    client: Client,
    items: list[LineItem],
    tax_rate: str | Decimal = "0.00",
) -> Invoice:
    rate = tax_rate if isinstance(tax_rate, Decimal) else Decimal(str(tax_rate))
    return Invoice(
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        client=client,
        items=list(items),
        tax_rate=rate,
    )
