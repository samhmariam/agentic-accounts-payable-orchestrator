# COST GOVERNANCE POLICY

## Purpose

Define the rules for monitoring, controlling, and approving changes to AI model
spending — so that cost optimisation cannot silently remove safety controls.

## Required Headings

1. Cost attribution model — how cost is allocated per capability, per run, and per period
2. Budget thresholds — alert, soft ceiling, and hard ceiling per period, with owner and action per level
3. Optimisation permission matrix — which capabilities can be optimised without approval, which require review, which are locked
4. Cost escalation procedure — steps when a threshold is breached
5. Governance owner — role accountable for this policy and review cadence

## Guiding Questions

- Which capability's cost is most variable and hardest to predict?
- What is the blast radius of hitting the hard ceiling in production during a peak processing period?
- Who has authority to approve an emergency PTU commitment outside the normal budget cycle?
- What observability evidence would a finance controller need to audit AI spending for one month?

## Acceptance Criteria

- Attribution model specifies granularity (capability-level is minimum)
- All three threshold levels present with specific actions for each
- Optimisation permission matrix has three tiers (approved/review-required/locked) with examples in each
- Escalation procedure names a role at each step and includes a time bound
- Governance owner and review cadence are specific (not "regularly reviewed")
