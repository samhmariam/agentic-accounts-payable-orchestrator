# SOURCE-OF-TRUTH CONFLICT RUNBOOK

## Purpose

Provide an actionable runbook for on-call engineers and escalation owners when
two data sources disagree, with decision trees for each conflict class.

## Required Headings

1. Conflict detection — how a conflict is detected (alerting, polling, or runtime exception)
2. Conflict classes — enumerated types of conflict with a detection signature for each
3. Decision tree per conflict class — step-by-step resolution with explicit decision points
4. Escalation criteria — when an on-call engineer escalates to a data owner or compliance
5. Post-incident actions — what must be documented after a conflict is resolved
6. Owner — who maintains this runbook and on what review cadence

## Guiding Questions

- Which conflict class is most likely to occur silently (no alert, no exception)?
- If the on-call engineer cannot determine which source is correct, what is the safe default action?
- Who owns the system-of-record write during a conflict — the engineer or the data owner?
- What is the audit evidence requirement if a conflict involved a payment recommendation?

## Acceptance Criteria

- Minimum 3 conflict classes with detection signatures
- Every decision tree has an explicit "escalate" exit path (not a loop)
- Safe default action is defined and is the most conservative option available
- Post-incident actions include an audit log entry with required fields
- Owner section names a role and a review cadence (not "reviewed periodically")
