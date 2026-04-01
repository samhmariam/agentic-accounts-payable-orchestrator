# PAUSE–RESUME GOVERNANCE

## Purpose

Define the rules under which the system pauses, how durable state is managed
during the pause, and the conditions under which resumption is safe.

## Required Headings

1. Pause triggers — enumerated list of conditions that trigger a pause
2. Durable state contract — what must be persisted, in what format, and with what consistency guarantee
3. Safe resumption conditions — what must be verified before the workflow resumes
4. Stale-context handling — what happens if the context has changed during the pause
5. Replay safety — which actions must not replay on resume and how that is enforced
6. Governance owner — who decides whether a paused workflow is resumed, abandoned, or escalated

## Guiding Questions

- Which pause trigger is most likely to occur, and is it fully covered?
- If the workflow resumes 72 hours after pausing, which state fields may be stale?
- What is the blast radius of resuming with a stale approval decision?
- Who has the authority to resume a paused workflow outside the normal SLA?

## Acceptance Criteria

- At least four pause triggers enumerated
- Durable state contract names specific fields, not just "workflow state"
- Safe resumption conditions include at least one freshness check
- Stale-context handling has a defined outcome (not "handle it somehow")
- Replay-safety section names the specific actions that must not replay and the enforcement mechanism
- Governance owner is a role, not a system
