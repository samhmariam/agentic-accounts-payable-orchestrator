# ADR-002 Irreversible Actions and HITL

- Status: accepted
- Date: 2026-04-08

## Context

The sponsor requested automated payment release with no human pause so the team
could accelerate close. That request crosses the irreversible-action boundary
for a regulated finance workflow.

## Decision

We will not allow the agent to issue payments or release funds without an
explicit human approval step. The system must fail closed and preserve the pause
state when evidence is incomplete, authority is ambiguous, or policy confidence
is below threshold.

## Rationale

- Payment release is irreversible once the downstream treasury process begins.
- A false positive creates direct financial loss, audit exposure, and CAB
  escalation.
- Human-in-the-loop approval preserves accountability and supports exception
  handling without weakening the automation path for reversible steps.

## Approved Design

- Agent may classify, route, summarize, and prepare an approval recommendation.
- Human approver must confirm before any payment-release action is executed.
- The approval artifact must capture actor identity, evidence references, and
  the exact policy trigger that forced the pause.

## Rejected Alternative

Full auto-release with post-hoc audit logging was rejected because auditability
after an irreversible payment is not an adequate compensating control.

## Consequences

- The workflow keeps a deliberate pause on high-risk and payment-release paths.
- Throughput is slightly lower, but blast radius is materially reduced.
- Any future request to relax this boundary requires CAB review and explicit
  exception authority.
