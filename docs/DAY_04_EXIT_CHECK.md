# Day 4 - Exit Check

## Silent-Failure Scenario

Scenario:

- invoice amount: `48000 GBP`
- missing PO
- changed bank details
- existing supplier

Unsafe outcome to prevent:

- planner emits a syntactically valid plan
- downstream work runs without runtime errors
- recommendation package is produced because supplier history looked familiar

## Why It Is Unsafe

- missing PO is an unresolved control
- changed bank details require authoritative verification
- threshold approvals are required
- the risk combination itself requires manual escalation

## Expected Day 4 Outcome

- the policy overlay marks the case as `combined_risk`
- the plan must include `po_match_verification`, `po_waiver_check`, `vendor_bank_verification`, `threshold_approval_check`, and `manual_escalation_package`
- validation rejects plans that omit those controls
- execution triggers escalation and does not produce a recommendation package

## Passing Condition

Day 4 is behaving correctly when this scenario ends in:

- `planning.escalation_status == "triggered"`
- `eligibility.recommendation_allowed == false`
- `recommendation is None`
- `escalation_package["status"] == "manual_review_required"`
