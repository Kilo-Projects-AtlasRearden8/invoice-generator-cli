# Invoice Generator CLI

A small, local-first Python CLI that turns client info and line items into
polished invoice PDFs. It also keeps local JSON drafts and can export any
invoice to CSV. No network, no API keys, no subscriptions — just your computer
and your data.

Built by **Asdale Dynamics, LLC** (Indiana, formed Oct 2026), the indie
publishing and AI-education vehicle of Dylan Asdale, a registered nurse turned
AI author. Dylan's book *The Massive AI Manual* and hub site
dylanasdale.github.io explain AI "like a friend would": plain English, step by
step, never condescending. This tool is part of the LLC's small-business and
author tooling line — practical software for freelancers, authors, and anyone
who needs to send a professional invoice without the fuss.

## Who this is for

- Freelancers and consultants who need to bill clients
- Authors and creators sending invoices for books, editing, or design work
- Small-business owners who want a simple, private bookkeeping helper
- Anyone who prefers their data to stay on their own computer

## Install

You'll need Python 3.9 or newer.

```bash
git clone <this-repo>
cd invoice-generator-cli
pip install -e .
```

That installs the `invoice-cli` command. If you'd rather not install, you can
run it straight from the folder:

```bash
python -m invoice_generator.cli --help
```

## Your first invoice

Let's walk through creating an invoice, step by step.

Say you did 3 hours of consulting at $125/hour and one editing job at $200,
with an 8% tax rate. Here's the command:

```bash
invoice-cli create \
  --invoice-number INV-001 \
  --invoice-date 2026-10-28 \
  --client "Acme Co" \
  --client-email billing@acme.example \
  --client-address "123 Main St, Indianapolis, IN" \
  --tax-rate 0.08 \
  --item "Consulting|3|125.00" \
  --item "Editing|1|200.00" \
  --pdf-out invoice-INV-001.pdf
```

What just happened?

- `--invoice-number` and `--invoice-date` label your invoice.
- `--client`, `--client-email`, and `--client-address` describe who you're
  billing.
- `--tax-rate 0.08` sets an 8% tax rate.
- Each `--item` is a line item in the form `description|quantity|unit_price`.
- `--pdf-out` writes a PDF to the path you chose.

You should now have a file named `invoice-INV-001.pdf` with a clean,
professional invoice: your business (Asdale Dynamics, LLC), the client, a line
item table, and subtotal / tax / total.

## Save and load drafts (JSON)

Sometimes you want to save an invoice and come back to it later. Drafts are
plain JSON files stored locally — nothing goes to the cloud.

Save a draft:

```bash
invoice-cli create \
  --invoice-number INV-002 \
  --invoice-date 2026-10-28 \
  --client "Dylan Asdale" \
  --item "Book royalties|1|450.00" \
  --draft-out drafts/INV-002.json
```

List your drafts:

```bash
invoice-cli draft list
```

View a draft's contents:

```bash
invoice-cli draft load drafts/INV-002.json
```

Delete a draft you no longer need:

```bash
invoice-cli draft delete drafts/INV-002.json
```

Drafts live in a `drafts/` folder by default. Use `--drafts-dir` to put them
elsewhere.

## Export to CSV

Need your invoice data in a spreadsheet or accounting tool? Export it:

```bash
invoice-cli export \
  --invoice-number INV-001 \
  --invoice-date 2026-10-28 \
  --client "Acme Co" \
  --tax-rate 0.08 \
  --item "Consulting|3|125.00" \
  --item "Editing|1|200.00" \
  --out invoice-INV-001.csv
```

The CSV includes one row per line item, plus subtotal, tax, and total at the
bottom.

## Commands at a glance

| Command | What it does |
|---------|--------------|
| `create` | Build an invoice from flags; write `--pdf-out` and/or `--draft-out`. |
| `draft save` | Save an invoice to a local JSON draft file. |
| `draft list` | List drafts in your drafts folder. |
| `draft load <file>` | Print a draft as JSON. |
| `draft delete <file>` | Delete a draft file. |
| `export` | Write an invoice to CSV. |
| `pdf` | Render an invoice to PDF. |

## How totals and tax work

All money math uses Python's `decimal.Decimal`, so totals are exact — no
floating-point surprises.

- **Subtotal** = sum of `quantity × unit_price` across all line items.
- **Tax** = `subtotal × tax_rate`, rounded half-up to the nearest cent.
- **Total** = subtotal + tax.

For example, subtotal $575.00 at 8% tax gives $46.00 tax and a $621.00 total.

Tests live in `tests/` and cover subtotals, multi-item invoices, tax rounding,
and empty invoices:

```bash
pytest
```

## Local-first, private by design

This tool never phones home. There are no API keys, no accounts, no tracking,
and no cloud storage. Your invoices and drafts are ordinary files on your own
computer. The tool itself does not collect or store any personal data — the
client names and addresses you type in are yours alone and never leave your
machine.

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.

## About Asdale Dynamics, LLC

Asdale Dynamics, LLC is the small-business and AI-education project of Dylan
Asdale, a registered nurse turned AI author and founder. Through *The Massive
AI Manual* and dylanasdale.github.io, Dylan explains AI like a friend would —
plain English, step by step, never condescending. The LLC publishes beginner
manuals, open-source tools, and small-business helpers just like this one.

---

Made with care for freelancers, authors, and small businesses who want their
invoicing simple, local, and theirs.
