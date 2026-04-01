# EVAL GOVERNANCE POLICY

## Purpose

Define the rules under which evaluation results determine a release decision,
including slice-level requirements and zero-tolerance metric handling.

## Required Headings

1. Release criteria — the exact metric thresholds that must be met for a release to proceed
2. Zero-tolerance metrics — metrics where any regression triggers an automatic block, not a judgement call
3. Slice governance rules — which slices require independent evaluation and what to do on slice regression
4. Override authority — who can approve a release despite a metric regression and what evidence is required
5. Evidence retention — what eval outputs must be retained and for how long

## Guiding Questions

- Which metric is most likely to regress silently when a new model version is deployed?
- What is the procedure when the aggregate score improves but a critical slice regresses?
- Who has authority to approve a release when a borderline metric is "close enough"?
- How long must eval evidence be retained to satisfy a financial audit?

## Acceptance Criteria

- Release criteria table has numeric thresholds (not "good performance")
- Zero-tolerance metrics list is explicit — not "critical metrics"
- Slice governance section covers the aggregate-passes / slice-fails conflict explicitly
- Override authority names a role, requires evidence, and limits the number of consecutive overrides
- Evidence retention specifies a duration and a storage location
