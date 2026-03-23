# Fixture dataset

Each fixture case includes:

- `package.json`: the Day 1 input package
- `candidate.json`: a plausible extraction result from the Day 1 agent

The cases are intentionally small and text-only. They assume OCR or PDF-to-text has already happened upstream.

## Cases

### happy_path
A valid invoice package with consistent formatting and all required business fields.

### locale_mismatch
A valid invoice package where the PDF uses continental formatting (`1.250,00 EUR`) and the email uses plain formatting (`EUR 1250`). The candidate preserves both raw values, and deterministic normalization reconciles them to the same numeric value.

### missing_po
An invalid invoice package with no PO reference in the source package. The candidate leaves `po_reference_text` as `null`, and canonicalization must reject it.
