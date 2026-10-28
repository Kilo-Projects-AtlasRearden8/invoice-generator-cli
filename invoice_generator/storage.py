"""Local JSON draft storage for invoices."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from .models import Client, Invoice, LineItem, Money


@dataclass
class DraftRecord:
    filename: str
    invoice_number: str
    client_name: str
    invoice_date: str


class DraftStore:
    """Persists invoices as JSON files in a local drafts directory."""

    def __init__(self, drafts_dir: str | os.PathLike[str] = "drafts") -> None:
        self.drafts_dir = Path(drafts_dir)
        self.drafts_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, invoice_number: str) -> Path:
        safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in invoice_number)
        return self.drafts_dir / f"{safe}.json"

    def save(self, invoice: Invoice, filename: str | None = None) -> Path:
        path = Path(filename) if filename else self._path(invoice.invoice_number)
        if not path.is_absolute():
            path = self.drafts_dir / path.name
        path.parent.mkdir(parents=True, exist_ok=True)

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
                    "description": item.description,
                    "quantity": str(item.quantity),
                    "unit_price": str(item.unit_price.amount),
                }
                for item in invoice.items
            ],
        }
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return path

    def load(self, filename: str) -> Invoice:
        path = Path(filename)
        if not path.is_absolute():
            path = self.drafts_dir / path
        payload = json.loads(path.read_text(encoding="utf-8"))
        return _payload_to_invoice(payload)

    def list_drafts(self) -> list[DraftRecord]:
        records: list[DraftRecord] = []
        for path in sorted(self.drafts_dir.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            records.append(
                DraftRecord(
                    filename=path.name,
                    invoice_number=payload.get("invoice_number", path.stem),
                    client_name=payload.get("client", {}).get("name", ""),
                    invoice_date=payload.get("invoice_date", ""),
                )
            )
        return records

    def delete(self, filename: str) -> Path:
        path = Path(filename)
        if not path.is_absolute():
            path = self.drafts_dir / path
        path.unlink()
        return path


def _payload_to_invoice(payload: dict) -> Invoice:
    client = Client(
        name=payload["client"]["name"],
        email=payload["client"].get("email"),
        address=payload["client"].get("address"),
    )
    items = [
        LineItem(
            description=it["description"],
            quantity=Decimal(it["quantity"]),
            unit_price=Money(Decimal(it["unit_price"])),
        )
        for it in payload.get("items", [])
    ]
    return Invoice(
        invoice_number=payload["invoice_number"],
        invoice_date=payload["invoice_date"],
        client=client,
        items=items,
        tax_rate=Decimal(payload.get("tax_rate", "0")),
    )
