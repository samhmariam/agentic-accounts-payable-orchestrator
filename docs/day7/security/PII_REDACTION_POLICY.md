# PII Redaction Policy

All structured logs and audit summaries must pass through the shared Day 7
redaction layer before emission.

## Masked Patterns

- email addresses
- phone numbers
- VAT or tax identifiers
- bank or account-like strings
- postal address fragments
- overly long freeform evidence excerpts

## Preserved References

- invoice IDs
- supplier IDs
- PO IDs
- policy IDs
- document or evidence IDs

## Operational Rule

If a developer needs raw evidence for debugging, they should retrieve it from
the source system or controlled fixture, not from logs or audit summaries.
