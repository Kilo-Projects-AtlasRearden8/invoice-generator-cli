"""CSV export for invoices."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path

from .models import Invoice


def invoice_rows(invoice: Invoice) -> Iterable[list[str]]:
    """Yield CSV rows: header, one row per line item, then totals."""
    yield [
        "invoice_number",
        "invoice_date",
        "client_name",
        "client_email",
        "client_address",
        "description",
        "quantity",
        "unit_price",
        "line_total",
    ]
    for item in invoice.items:
        yield [
            invoice.invoice_number,
            invoice.invoice_date,
            invoice.client.name,
            invoice.client.email or "",
            invoice.client.address or "",
            item.description,
            str(item.quantity),
            str(item.unit_price.amount),
            str(item.line_total().amount),
        ]
    # Totals block
    from .totals import invoice_totals

    totals = invoice_totals(invoice)
    yield []
    yield ["subtotal", str(totals["subtotal"].amount)]
    yield [f"tax_rate_{invoice.tax_rate}", str(totals["tax"].amount)]
    yield ["total", str(totals["total"].amount)]


def export_csv(invoice: Invoice, output_path: str) -> str:
    """Write ``invoice`` to a CSV file at ``output_path``. Returns the path."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        for row in invoice_rows(invoice):
            writer.writerow(row)
    return str(path)
