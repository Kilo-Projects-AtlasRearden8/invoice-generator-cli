"""Command-line interface for the Asdale Dynamics invoice generator.

Local-first: drafts are JSON files on disk, PDFs and CSVs are written to
paths you choose. No network, no API keys, no personal data stored by the
tool itself.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from decimal import Decimal

from .csv_export import export_csv
from .models import Client, Invoice, LineItem, Money, build_invoice
from .pdf import generate_pdf
from .storage import DraftStore


def _parse_item(value: str) -> LineItem:
    """Parse a single ``desc|qty|unit_price`` item string."""
    parts = value.split("|")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(
            f"item must be desc|qty|unit_price, got: {value!r}"
        )
    description, qty, price = parts
    return LineItem(
        description=description,
        quantity=Decimal(qty),
        unit_price=Money(Decimal(price)),
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="invoice-cli",
        description="Generate invoice PDFs from client info and line items "
        "(local JSON drafts, CSV export).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ---- create ----
    p_create = sub.add_parser("create", help="Build an invoice from flags.")
    p_create.add_argument("--invoice-number", required=True)
    p_create.add_argument("--invoice-date", required=True)
    p_create.add_argument("--client", required=True, help="Client name")
    p_create.add_argument("--client-email", default=None)
    p_create.add_argument("--client-address", default=None)
    p_create.add_argument(
        "--tax-rate", default="0.00", help="Tax rate as decimal, e.g. 0.08"
    )
    p_create.add_argument(
        "--item",
        action="append",
        type=_parse_item,
        default=[],
        help="Line item as desc|qty|unit_price (repeatable)",
    )
    p_create.add_argument("--pdf-out", default=None, help="Write PDF to this path")
    p_create.add_argument(
        "--draft-out", default=None, help="Save JSON draft to this path"
    )
    p_create.set_defaults(func=_cmd_create)

    # ---- draft ----
    p_draft = sub.add_parser("draft", help="Manage local JSON drafts.")
    p_draft.add_argument("--drafts-dir", default="drafts")
    dsub = p_draft.add_subparsers(dest="draft_command", required=True)

    p_save = dsub.add_parser("save", help="Save an invoice to a draft file.")
    p_save.add_argument("--invoice-number", required=True)
    p_save.add_argument("--invoice-date", required=True)
    p_save.add_argument("--client", required=True)
    p_save.add_argument("--client-email", default=None)
    p_save.add_argument("--client-address", default=None)
    p_save.add_argument("--tax-rate", default="0.00")
    p_save.add_argument("--item", action="append", type=_parse_item, default=[])
    p_save.add_argument("--out", default=None, help="Draft file path")
    p_save.set_defaults(func=_cmd_draft_save)

    p_load = dsub.add_parser("load", help="Load and print a draft as JSON.")
    p_load.add_argument("file")
    p_load.set_defaults(func=_cmd_draft_load)

    p_list = dsub.add_parser("list", help="List drafts in the drafts directory.")
    p_list.set_defaults(func=_cmd_draft_list)

    p_delete = dsub.add_parser("delete", help="Delete a draft file.")
    p_delete.add_argument("file")
    p_delete.set_defaults(func=_cmd_draft_delete)

    # ---- export ----
    p_export = sub.add_parser("export", help="Export an invoice to CSV.")
    p_export.add_argument("--invoice-number", required=True)
    p_export.add_argument("--invoice-date", required=True)
    p_export.add_argument("--client", required=True)
    p_export.add_argument("--client-email", default=None)
    p_export.add_argument("--client-address", default=None)
    p_export.add_argument("--tax-rate", default="0.00")
    p_export.add_argument("--item", action="append", type=_parse_item, default=[])
    p_export.add_argument("--out", required=True, help="CSV output path")
    p_export.set_defaults(func=_cmd_export)

    # ---- pdf ----
    p_pdf = sub.add_parser("pdf", help="Render an invoice to PDF.")
    p_pdf.add_argument("--invoice-number", required=True)
    p_pdf.add_argument("--invoice-date", required=True)
    p_pdf.add_argument("--client", required=True)
    p_pdf.add_argument("--client-email", default=None)
    p_pdf.add_argument("--client-address", default=None)
    p_pdf.add_argument("--tax-rate", default="0.00")
    p_pdf.add_argument("--item", action="append", type=_parse_item, default=[])
    p_pdf.add_argument("--out", default=None, help="PDF output path")
    p_pdf.set_defaults(func=_cmd_pdf)

    return parser


def _invoice_from_args(args) -> Invoice:
    client = Client(
        name=args.client,
        email=args.client_email,
        address=args.client_address,
    )
    return build_invoice(
        invoice_number=args.invoice_number,
        invoice_date=args.invoice_date,
        client=client,
        items=list(args.item),
        tax_rate=args.tax_rate,
    )


def _cmd_create(args) -> int:
    invoice = _invoice_from_args(args)
    messages = []
    if args.pdf_out:
        generate_pdf(invoice, args.pdf_out)
        messages.append(f"PDF written: {args.pdf_out}")
    if args.draft_out:
        DraftStore().save(invoice, args.draft_out)
        messages.append(f"Draft saved: {args.draft_out}")
    if not messages:
        from .totals import invoice_totals

        totals = invoice_totals(invoice)
        print(f"Invoice {invoice.invoice_number} for {invoice.client.name}")
        print(f"  Subtotal: {totals['subtotal']}")
        print(f"  Tax:      {totals['tax']}")
        print(f"  Total:    {totals['total']}")
        print("Use --pdf-out or --draft-out to write a file.")
    for m in messages:
        print(m)
    return 0


def _cmd_draft_save(args) -> int:
    invoice = _invoice_from_args(args)
    store = DraftStore(args.drafts_dir)
    path = store.save(invoice, args.out)
    print(f"Draft saved: {path}")
    return 0


def _cmd_draft_load(args) -> int:
    store = DraftStore()
    invoice = store.load(args.file)
    import json

    payload = {
        "invoice_number": invoice.invoice_number,
        "invoice_date": invoice.invoice_date,
        "client": {
            "name": invoice.client.name,
            "email": invoice.client.email,
            "address": invoice.client.address,
        },
        "tax_rate": str(invoice.tax_rate),
        "items": [
            {
                "description": it.description,
                "quantity": str(it.quantity),
                "unit_price": str(it.unit_price.amount),
            }
            for it in invoice.items
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0


def _cmd_draft_list(args) -> int:
    store = DraftStore(args.drafts_dir)
    records = store.list_drafts()
    if not records:
        print("No drafts found.")
        return 0
    print("filename\tinvoice_number\tclient\tdate")
    for r in records:
        print(f"{r.filename}\t{r.invoice_number}\t{r.client_name}\t{r.invoice_date}")
    return 0


def _cmd_draft_delete(args) -> int:
    store = DraftStore()
    path = store.delete(args.file)
    print(f"Deleted: {path}")
    return 0


def _cmd_export(args) -> int:
    invoice = _invoice_from_args(args)
    path = export_csv(invoice, args.out)
    print(f"CSV exported: {path}")
    return 0


def _cmd_pdf(args) -> int:
    invoice = _invoice_from_args(args)
    path = generate_pdf(invoice, args.out)
    print(f"PDF generated: {path}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
