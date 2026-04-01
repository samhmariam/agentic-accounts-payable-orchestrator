# SLICE REGRESSION DECISION LOG

## Purpose

Record every slice regression decision made during the programme, with the
reasoning, the approver, and the outcome — especially when a slice regression
is discovered after an aggregate score improvement.

## Required Headings

1. Decision log table (run ID, date, slice name, metric, previous value, current value, aggregate delta, decision, approver, rationale)
2. Decision classification — block / release with monitoring / escalate to override authority
3. Pattern analysis — any repeat regressions in the same slice and what they indicate
4. Remediation actions — what was done to address the regression before the next release

## Guiding Questions

- Which slice is most likely to regress without surfacing in aggregate metrics?
- If a slice tied to a compliance requirement regresses by 1%, is that a block or a monitored release?
- Who reviews the decision log before a CAB submission?
- What pattern of slice regressions would trigger a mandatory architecture review?

## Structural Example — Decision Log Entry

| Field | Value |
|---|---|
| Run ID | `<eval run identifier>` |
| Date | `<YYYY-MM-DD>` |
| Slice | `<slice name, e.g., high_value_invoice_gbp>` |
| Metric | `<metric name, e.g., extraction_f1>` |
| Previous | `<numeric>` |
| Current | `<numeric>` |
| Aggregate delta | `<+ or - numeric>` |
| Decision | `<block \| release_with_monitoring \| escalate>` |
| Approver | `<role>` |
| Rationale | `<one sentence>` |

## Acceptance Criteria

- At least two entries in the log (can be hypothetical scenarios from the lab)
- Every entry has a decision and an approver (not blank)
- Pattern analysis is present even if no pattern is identified (note "no pattern observed to date")
- Remediation actions are specific — not "we will investigate"
