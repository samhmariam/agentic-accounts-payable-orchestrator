# CAB PACKET

## Purpose

Provide the Change Advisory Board with all evidence required to approve a
production release, formatted for a non-technical reviewer.

## Required Headings

1. Executive summary — one paragraph, plain language, no acronyms
2. Release scope — what is changing, what is not changing
3. Gate evidence summary — pass/fail against each mandatory gate (health, trace, cost, accuracy, refusal, replay)
4. Risk assessment — top three risks with likelihood, impact, and mitigation
5. Rollback procedure — step-by-step with a time estimate and the condition that triggers rollback
6. Approval chain — roles required to approve this release, with signature/confirmation fields

## Guiding Questions

- Which gate evidence is weakest and how do you address that in the risk section?
- If the CAB chair asks "what happens if this goes wrong in the first 24 hours", what is your answer?
- What is the single most important thing a non-technical board member needs to understand about this release?
- Who holds rollback authority after the release is declared successful?

## Structural Example — CAB Summary Shape

Executive summary pattern:

`This release introduces automated invoice triage for low-risk cases while preserving human approval for high-value or exception invoices. The change does not alter the ERP posting contract, vendor master ownership, or payment execution authority. Release promotion is blocked automatically if security, accuracy, refusal, replay-safety, budget, or health evidence is missing or red.`

Risk table pattern:

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Slice regression on high-value invoices | Medium | High | Block release if Day 8 baseline regresses on protected slice |
| Identity drift in deployment path | Low | High | OIDC federation + managed identity; no long-lived secrets |
| Replay duplicate on resumed workflow | Low | High | Day 5 resume-safety gate + rollback to prior revision |

Rollback procedure pattern:

1. Confirm which gate or live signal failed and record the timestamp.
2. Route 100% traffic back to the last known-good ACA revision.
3. Re-run the gate suite against the restored stable revision.
4. Notify CAB approver chain and attach the updated release envelope.
5. Open incident follow-up if the rollback was caused by a production-only condition.

## Acceptance Criteria

- Executive summary is ≤ 200 words and contains no acronyms
- Gate evidence section has a pass/fail status for every mandatory gate (not a narrative)
- Risk assessment has likelihood and impact for each risk (not just a description)
- Rollback procedure is step-by-step (not "we can roll back")
- Approval chain includes at least three distinct roles
