# Day 01

## Purpose

Day 01 defines the intake boundary for invoice processing.

It takes a raw `InvoicePackageInput`, asks a single extraction agent for a
string-heavy `ExtractedInvoiceCandidate`, and then deterministically converts
that candidate into a trusted `CanonicalInvoice`.

If the extracted values are missing, malformed, inconsistent, or unsupported,
Day 01 rejects the record instead of letting weak data flow downstream.

## Pipeline

```text
InvoicePackageInput
    ->
extract_candidate(...)
    ->
ExtractedInvoiceCandidate
    ->
to_canonical_invoice(...)
    ->
CanonicalInvoice

or

IntakeReject
```

The production path is `run_day_01_intake(...)` in
`src/aegisap/day_01/service.py`.

The deterministic test path is `canonicalize_with_candidate(...)`, which skips
the live model call and validates a supplied candidate directly.

## Core models

### `InvoicePackageInput`

Represents the upstream package handed to Day 01:

- `message_id`
- `email_subject`
- `email_body`
- `attachments[]`
- attachment metadata plus `extracted_text`

Day 01 assumes OCR or PDF-to-text has already happened upstream.

### `ExtractedInvoiceCandidate`

Represents the agent output.

It intentionally stays string-based so the model does not become the source of
truth for parsing, normalization, or business validation.

Amounts are carried as `EvidenceValue` objects so PDF and email evidence can be
compared independently.

### `CanonicalInvoice`

Represents the only object allowed to cross the Day 01 boundary.

It guarantees:

- normalized ISO currency code
- parsed invoice date
- normalized decimal amounts
- `net_amount + vat_amount == gross_amount`
- hashed bank details instead of raw bank text

## Deterministic normalization rules

Day 01 keeps business trust in Python, not in the model.

### Text evidence

Text fields must be present in the source package before they are accepted.

Structured identifiers such as:

- invoice number
- invoice date
- currency
- PO reference
- bank details

are validated with boundary-aware matching so partial prefixes do not count as
real evidence. This prevents values like `PO-` or a shortened IBAN fragment
from being accepted just because they appear inside a longer token.

### Money parsing

`parse_money(...)` accepts supported invoice formats and normalizes them to
two-decimal `Decimal` values.

Supported examples:

- `1250.00 GBP`
- `GBP 1500.00`
- `1.250,00 EUR`
- `EUR 1250`

Rejected examples:

- ambiguous single-separator values like `1.250` or `1,250`
- negative values
- malformed values with embedded OCR noise like `1O0.00 USD`

The parser only accepts a numeric core plus at most one recognized currency
token. It does not silently strip arbitrary letters.

### Cross-source reconciliation

For `net_amount`, `vat_amount`, and `gross_amount`, Day 01 compares PDF and
email evidence after deterministic parsing.

If both sources are present:

- matching normalized values are accepted
- conflicting normalized values are rejected

This allows harmless locale differences while blocking real disagreement.

### Bank details

Bank details must exist in the source text and be long enough to hash safely.
The canonical output stores only `bank_details_hash`.

## Rejection behavior

Failures from Pydantic validation or deterministic normalization are wrapped as
`IntakeReject`.

Typical rejection reasons include:

- required field missing
- evidence text not found in source text
- unsupported currency or date format
- invalid or ambiguous amount
- mismatch between PDF and email amount evidence
- gross amount not equal to net plus VAT

## Fixtures and tests

The current fixtures cover three baseline scenarios:

- `happy_path`
- `locale_mismatch`
- `missing_po`

The tests also include explicit regressions for:

- OCR-corrupted amounts being rejected
- truncated PO references being rejected
- truncated bank details being rejected

Run them with:

```bash
pytest -q tests/test_day_01_money.py tests/test_day_01_fixtures.py
```

## File map

- `src/aegisap/day_01/models.py`: data contracts
- `src/aegisap/day_01/agent.py`: Azure OpenAI extraction call
- `src/aegisap/day_01/normalizers.py`: deterministic normalization and evidence checks
- `src/aegisap/day_01/service.py`: intake entrypoints and rejection wrapping
- `src/aegisap/day_01/fixture_loader.py`: fixture helpers
- `tests/test_day_01_money.py`: money parser coverage
- `tests/test_day_01_fixtures.py`: end-to-end fixture coverage
