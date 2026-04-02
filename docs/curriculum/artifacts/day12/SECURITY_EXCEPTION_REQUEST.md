# SECURITY EXCEPTION REQUEST

<!-- CAPSTONE_B: This artifact applies to both AP and claims intake transfer domain -->

## Purpose

Demonstrate the complete security exception request for a temporary public
endpoint or network control relaxation required during development or testing.

## Required Headings

1. Exception scope — the specific control being relaxed and in which environment
2. Business justification — time-bounded, with a specific end date
3. Compensating controls — what maintains the security posture during the exception period
4. Risk statement — what specific risk is being accepted and who accepts it
5. Expiry and removal obligation — who is obligated to remove the exception and by when
6. Approver chain — who must approve, who must be informed, and post-approval audit requirement

## Guiding Questions

- What is the minimum scope for this exception (what can be protected even during the exception period)?
- What is the blast radius if the exception is not removed on the expiry date?
- Who monitors for the exception being extended without a fresh approval?
- What audit evidence must exist to prove the exception was removed as required?

## Structural Example — Exception Summary Shape

| Field | Example shape |
|---|---|
| Exception scope | Temporary public access to Azure AI Search in isolated staging only while private DNS link is repaired |
| Business justification | Required to complete a time-boxed deployment rehearsal for `2026-04-18` CAB decision; expires `2026-04-20` |
| Compensating controls | IP allowlist to build subnet, test dataset only, elevated monitoring, daily review by security lead |
| Risk acceptor | Director of platform security accepts temporary search endpoint exposure in staging |
| Removal obligation | Platform engineer removes exception by `2026-04-20 18:00 UTC`; security lead verifies via posture probe artifact |
| Audit proof | Ticket link, approval chain, before/after probe outputs, and closure comment in change record |

## Anti-Patterns To Avoid

- Do not ask for an exception on behalf of "the team"; name the risk acceptor and removal owner.
- Do not describe an exception as temporary without a calendar expiry and verification method.
- Do not use broader scope than necessary; "all AI services public for testing" is a design failure, not an exception request.

## Acceptance Criteria

- Exception scope names the specific control and environment (not "dev environment networking")
- Compensating controls are specific and verifiable
- Risk statement names a role as the risk acceptor
- Expiry date is a specific calendar date — not "when development is complete"
- Removal obligation is assigned to a named role with a verification mechanism
- Approver chain has a CISO or platform security lead at minimum

## Note on Zero-Tolerance

A security exception that describes any public endpoint as acceptable in production
is a zero-tolerance hard fail regardless of compensating controls.
