# Day 1 Data Flow

## Purpose

Day 1 isolates the smallest reliable intake slice in AegisAP:

1. accept an invoice package that already contains extracted document text
2. use a single agent to extract raw invoice evidence
3. normalize and validate that evidence into a trusted `CanonicalInvoice`
4. reject incomplete or inconsistent records at the intake boundary

This document makes the three-layer boundary explicit so the learner does not confuse:

- document text extraction
- model extraction
- business-safe canonicalization

## The three layers

```text
LAYER 0 — Upstream document extraction

  Email + PDF / image attachment
          |
          v
  OCR / PDF-to-text / document AI service
          |
          v
  Extracted attachment text + attachment metadata


LAYER 1 — Day 1 input package

  InvoicePackageInput
    - message_id
    - email_subject
    - email_body
    - attachments[]
        - filename
        - content_type
        - sha256
        - extracted_text
          |
          v
  Single-agent extraction
          |
          v
  ExtractedInvoiceCandidate
    - supplier_name_text
    - invoice_number_text
    - invoice_date_text
    - currency_text
    - net_amount.{pdf_text,email_text}
    - vat_amount.{pdf_text,email_text}
    - gross_amount.{pdf_text,email_text}
    - po_reference_text
    - bank_details_text


LAYER 2 — Deterministic canonicalization boundary

  deterministic normalization
    - money parsing
    - locale handling
    - currency normalization
    - date parsing
    - bank detail hashing
    - source evidence checks
    - cross-source reconciliation
          |
          v
  Pydantic validation boundary
          |
          +--> reject with explicit error
          |
          v
  CanonicalInvoice
    - supplier_name
    - invoice_number
    - invoice_date
    - currency
    - net_amount
    - vat_amount
    - gross_amount
    - po_reference
    - bank_details_hash
```

## Visual flow

```text
[Email body + attachment binaries]
              |
              v
[Upstream document extraction service]
              |
              v
[Attachment metadata + extracted_text]
              |
              v
[InvoicePackageInput]
              |
              v
[PydanticAI single-agent extraction]
              |
              v
[ExtractedInvoiceCandidate]
              |
              v
[Deterministic normalization + reconciliation]
              |
              v
[Pydantic CanonicalInvoice validation]
         /                \
        v                  v
   [Reject]       [CanonicalInvoice]
```

## What is in scope on Day 1

Day 1 starts **after** document text extraction has already happened.

In scope:

- invoice email plus attachment metadata
- agent extraction into a raw candidate object
- deterministic normalization of dates, currencies, and amounts
- schema validation with Pydantic
- rejection of malformed, missing, ambiguous, or inconsistent values

Out of scope:

- mailbox integration
- OCR model tuning
- PDF rendering
- document classification across multiple document types
- search / retrieval indexing
- ERP posting

## Why the upstream extraction step is separate

The Day 1 lesson is not “how to OCR a PDF.”
The lesson is “how to stop weak extraction from silently entering the finance workflow.”

That requires a clean separation between:

- **document extraction**, which turns files into text
- **agent extraction**, which identifies candidate invoice fields from that text
- **canonicalization**, which decides whether the business can trust the result

If these are merged too early, learners often let the LLM output act as both parser and validator, which is exactly the failure mode Day 1 is designed to expose.

## Upstream service options

Any service that can produce reliable attachment text can sit upstream of Day 1.
Typical options include:

### Managed document AI / OCR services

- **Azure AI Document Intelligence**
  - good fit if the wider stack is Azure-first
  - useful for layout-aware extraction and OCR on invoices and forms

- **AWS Textract**
  - good fit for AWS-native document pipelines
  - supports text extraction and structured form/table analysis

- **Google Document AI**
  - useful where the team wants Google’s document-processing stack
  - supports OCR and document parsing workflows

### Generic OCR / parsing components

- **Tesseract OCR**
  - low-cost option for scanned-image OCR
  - usually requires more engineering around quality control

- **PDF text parsers** such as `pypdf`, `pdfplumber`, or equivalent
  - suitable for digitally generated PDFs that already contain embedded text
  - often faster and cheaper than OCR when scans are not involved

### Hybrid approach

A common production pattern is:

- first try direct PDF text extraction for digitally generated PDFs
- fall back to OCR / document AI for scans or image-heavy documents
- persist both the raw file and the extracted text for auditability

## What the fixtures represent

The fixture set deliberately mirrors the boundary between upstream services and Day 1 processing.

### `fixtures/*/package.json`

This simulates the object handed to Day 1 **after** upstream extraction is complete.
It represents:

- email metadata
- email body text
- attachment metadata
- `extracted_text` for each attachment

So `package.json` is the stand-in for the output of:

```text
mail ingestion + attachment capture + OCR/PDF-to-text
```

### `fixtures/*/candidate.json`

This simulates the raw output of the single extraction agent.
It represents what the model thinks it found in the package, before deterministic business checks are applied.

So `candidate.json` is the stand-in for:

```text
InvoicePackageInput -> single-agent extraction -> ExtractedInvoiceCandidate
```

### Canonical output

The final canonical object is **not** stored as a fixture input because the whole point of the exercise is to derive it only after deterministic normalization and validation.

## How the three example fixtures map to the boundary

### 1. `happy_path`

- upstream extracted text is complete and consistent
- the agent candidate mirrors the source accurately
- deterministic normalization succeeds
- `CanonicalInvoice` is produced

### 2. `locale_mismatch`

- the PDF uses `1.250,00 EUR`
- the email uses `EUR 1250`
- the candidate preserves both representations
- deterministic parsing proves they mean the same amount
- `CanonicalInvoice` is produced

This is a formatting difference, not a business disagreement.

### 3. `missing_po`

- upstream extracted text does not contain a PO reference
- the candidate leaves `po_reference_text` empty or null
- the validation boundary rejects the record

This is intentional. The system refuses to manufacture completeness.

## Silent failure prevention on Day 1

The classic failure this design blocks is:

- PDF says `1.250,00 EUR`
- email says `EUR 1250`
- model returns `1.25`
- weak checks allow the value through

The Day 1 boundary prevents that by requiring all of the following:

1. source-backed evidence strings
2. deterministic amount parsing with locale-aware rules
3. rejection of ambiguous single-separator values such as `1.250`
4. reconciliation across PDF and email evidence
5. strict Pydantic validation on the final canonical object

## Practical repo mapping

```text
fixtures/
  happy_path/
    package.json
    candidate.json
  locale_mismatch/
    package.json
    candidate.json
  missing_po/
    package.json
    candidate.json

src/aegisap/day_01/
  models.py         # contracts for package, candidate, canonical invoice
  agent.py          # single-agent extraction boundary
  normalizers.py    # deterministic parsing and reconciliation
  service.py        # orchestration and reject-on-failure entry point
```

## Operating rule for Day 1

The system may use an LLM to identify candidate fields.
The system may not use the LLM as the final authority on:

- numeric amounts
- date normalization
- currency normalization
- mandatory field completeness
- arithmetic consistency
- whether the invoice is safe to pass downstream

That authority belongs to deterministic code plus a strict schema boundary.
