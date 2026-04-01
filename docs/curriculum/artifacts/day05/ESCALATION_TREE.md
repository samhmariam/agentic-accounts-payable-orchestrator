# ESCALATION TREE

## Purpose

Map every escalation path in the system so that any failure condition routes
to the right human role at the right tier without ambiguity.

## Required Headings

1. Escalation trigger table (trigger condition, tier, initial target role, SLA to respond, if-no-response target)
2. Tier definitions (Tier 1 / 2 / 3 with scope, authority, and escalation SLA per tier)
3. Out-of-hours coverage — which roles cover which tiers when primary is unavailable
4. De-escalation criteria — conditions under which an escalated workflow returns to normal flow
5. Audit log requirements — what must be recorded for every escalation event

## Guiding Questions

- Which escalation path is most likely to be under-staffed at 03:00 on a weekend?
- What is the blast radius if Tier 2 does not respond within SLA and no Tier 3 path exists?
- Who de-escalates a workflow that was escalated in error?
- What is the minimum audit record that would satisfy an external auditor reviewing an escalation incident?

## Acceptance Criteria

- Minimum 6 trigger conditions, covering both system failures and decision failures
- All three tiers defined with scope and authority boundaries
- Out-of-hours coverage names a backup role — not "TBD"
- De-escalation criteria are observable (not "when resolved")
- Audit log entry structure is specified with field names
