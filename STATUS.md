# STATUS

## What was built

A local-first Python CLI (`invoice-cli`) that generates invoice PDFs from
client info and line items, with local JSON drafts and CSV export. Built for
Asdale Dynamics, LLC (Indiana, formed Oct 2026) as a small-business / author
tool.

Project contents:
- `invoice_generator/models.py` — `Client`, `LineItem`, `Invoice`, `Money`
  data models; all currency math uses `decimal.Decimal` for exact totals and
  tax.
- `invoice_generator/totals.py` — `invoice_totals()` and `tax_amount()`:
  subtotal, tax (rounded half-up to cents), total.
- `invoice_generator/pdf.py` — ReportLab-rendered invoice PDF (business block,
  client meta, line-item table, subtotal/tax/total).
- `invoice_generator/storage.py` — `DraftStore`: save/load/list/delete local
  JSON drafts.
- `invoice_generator/csv_export.py` — CSV export with per-item rows plus
  subtotal/tax/total block.
- `invoice_generator/cli.py` — argparse CLI: `create`, `draft save/list/load/delete`, `export`, `pdf`.
- `tests/test_totals.py` — 7 tests covering subtotals, multi-item invoices,
  tax rounding, total = subtotal + tax, empty invoice.
- `pyproject.toml` — packaging with `invoice-cli` console script; depends on
  `reportlab>=3.5`.
- `LICENSE` — MIT, copyright line exactly
  `Copyright (c) 2026 Asdale Dynamics, LLC`.
- `README.md` — install, step-by-step usage, command reference, tax math,
  local-first/privacy notes, credit to Asdale Dynamics, LLC.

## How to run it

Install:

```bash
pip install -e .
```

Create an invoice and write a PDF:

```bash
invoice-cli create \
  --invoice-number INV-001 \
  --invoice-date 2026-10-28 \
  --client "Acme Co" \
  --tax-rate 0.08 \
  --item "Consulting|3|125.00" \
  --item "Editing|1|200.00" \
  --pdf-out invoice-INV-001.pdf
```

Save a JSON draft:

```bash
invoice-cli create \
  --invoice-number INV-002 \
  --client "Dylan Asdale" \
  --item "Book royalties|1|450.00" \
  --draft-out drafts/INV-002.json
```

Manage drafts:

```bash
invoice-cli draft list
invoice-cli draft load drafts/INV-002.json
invoice-cli draft delete drafts/INV-002.json
```

Export to CSV:

```bash
invoice-cli export --invoice-number INV-001 --client "Acme Co" \
  --item "Consulting|3|125.00" --out invoice-INV-001.csv
```

Run tests:

```bash
pytest
```

Run lint/format:

```bash
ruff check .
ruff format --check .
```

## Verification results

- `pytest`: 7 passed (subtotals, multi-item, tax at 8%, half-up cent rounding,
  total = subtotal + tax, empty invoice, direct tax_amount helper).
- `ruff check .`: all checks passed.
- `ruff format --check .`: all files formatted.
- `python -m py_compile` on all package modules: OK.
- End-to-end manual run: `invoice-cli create` produced a valid PDF
  (starts with `%PDF-`), saved a JSON draft, `draft list` listed it, and
  `export` produced a CSV with correct subtotal/tax/total
  (e.g. subtotal 575.00, 8% tax 46.00, total 621.00).
- Installed with `pip install -e .` (requires `--break-system-packages` on this
  PEP 668-managed Python; this is an environment constraint, not a project
  issue).

## Known gaps

- No test coverage yet for PDF rendering, CSV export, draft storage, or CLI
  invocation — only `totals` math is tested. Adding tests for those modules
  would strengthen confidence.
- PDF uses a fixed "Asdale Dynamics, LLC" business block hardcoded in
  `pdf.py`; there's no flag to override the business name/address. A `--from`
  or business-profile option would make it more reusable.
- CLI item parsing (`desc|qty|unit_price`) cannot handle descriptions
  containing `|`. A different delimiter or quoted format would be more robust.
- `pyproject.toml` requires `--break-system-packages` to install on this
  PEP 668-managed system; in a normal virtualenv `pip install -e .` works
  without it.
- No `.github/workflows` (intentionally omitted per requirements) — CI would
  need to be added separately if desired.
- Draft file names are sanitized; very long invoice numbers produce long file
  names, which is fine for local use.

## Maintenance notes

- Python 3.13.5 used for development; `requires-python = ">=3.9"`.
- Commit identity: Dylan Asdale <dylanasdale@users.noreply.github.com>
  (existing repo identity; no Co-authored-by trailers).
- No secrets, API keys, or personal data committed. Sample client names in
  README/commands are illustrative only.
