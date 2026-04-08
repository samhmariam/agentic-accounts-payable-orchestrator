# Customer Escalation: Day 1 Trust Boundary Failure

Finance ops is blocked on a valid supplier invoice from a German vendor.

The OCR payload contains mixed separators like `1.250,00 EUR`, and the trust boundary is now rejecting the case instead of canonicalizing it. This started after the last extractor-related change.

What I need from engineering today:

- prove whether the failure is in extraction or deterministic normalization
- restore safe intake for mixed-separator amounts without weakening the boundary
- show me the exact test evidence before you ask AP to retry the invoice
