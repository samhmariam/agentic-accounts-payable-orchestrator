# HUMAN APPROVAL CONTRACT

## Purpose

Define the formal contract between the agentic system and the human approver:
what the system commits to provide, what the human commits to respond with,
and what happens when either side fails.

## Required Headings

1. Contract scope — which approval step(s) this contract covers
2. System obligations — what the agent must provide to the approver before requesting a decision
3. Approver obligations — what the approver must provide and within what SLA
4. Approval envelope — structure of the approval request and response (see structural example)
5. Timeout and escalation path — what happens if no response is received within SLA
6. Override and bypass rules — conditions where the normal flow is suspended, with authority and audit requirements

## Guiding Questions

- What is the minimum information the approver needs to make a safe decision?
- What should the system do if an approval arrives after the SLA but before the timeout escalation fires?
- Who owns the SLA definition — the agent team, the approver role, or legal/compliance?
- What is the blast radius if an approval response is replayed or replayed with a stale context?

## Structural Example — Approval Envelope

```json
{
  "request_id": "<uuid>",
  "workflow_id": "<workflow context>",
  "requested_action": "<specific action awaiting approval>",
  "evidence_bundle": {
    "summary": "<one-paragraph plain-language summary for the approver>",
    "risk_assessment": "<risk level and key risk factors>",
    "policy_compliance_status": "<compliant | requires_exception>"
  },
  "sla_seconds": "<numeric SLA>",
  "expires_at": "<ISO 8601 timestamp>",
  "escalation_target": "<role name>"
}
```

## Acceptance Criteria

- Contract scope is explicit — does not say "all approvals" without listing them
- System obligations include specific evidence items, not just "relevant information"
- Approver obligations include response format and SLA in seconds or minutes
- Timeout path names a specific escalation target role and a specific fallback action
- Override rules include an authority role and an expiry condition
