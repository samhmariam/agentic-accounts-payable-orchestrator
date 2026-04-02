# OBO THREAT MODEL

## Purpose

Model the threat surface introduced by OBO (On-Behalf-Of) token flows and
document the controls that break each attack chain.

## Required Headings

1. OBO flow diagram — actors, token types, and exchange steps (can be ASCII or Mermaid)
2. Threat inventory — enumerated threats with attack path, target asset, and likelihood
3. Control mapping — for each threat, which control breaks the chain and at which step
4. Residual risk — threats where the control is incomplete or conditional
5. Test assertions — what tests must pass before OBO is used in production

## Guiding Questions

- Which step in the OBO flow is most likely to be mis-implemented by a developer?
- If the actor binding check is bypassed, which downstream service accepts the token without re-checking?
- What observable signal indicates an authority confusion attack is in progress?
- What is the blast radius of a token replay attack through the OBO endpoint?

## Threat Categories to Cover (minimum)

- Token replay
- Actor binding bypass
- Scope escalation through delegated token
- Identity confusion in multi-agent call chain
- Revoked token accepted by downstream service

## Structural Example — Threat Inventory Row

| Threat | Attack path | Target asset | Control that breaks the chain | Test assertion |
|---|---|---|---|---|
| Actor binding bypass | Caller submits forged `actor_oid` in message body and service trusts payload over token claims | Approval audit trail and finance authority | OBO token `oid` must be source of truth; payload actor field ignored | Integration test proves forged payload OID is rejected |
| Scope escalation | Front-end obtains broader delegated scope than intended and backend exchanges it | Protected approval actions | Entra app registration limits scopes; backend validates expected audience and scope | Token exchange test fails when scope set is broader than contract |
| Token replay | Captured delegated token reused after user action window | Write-path mutation endpoints | Short TTL, nonce/correlation checks, downstream audience validation | Replay test proves second submission is rejected or audited as suspicious |

## Anti-Patterns To Avoid

- Do not list threats without naming the exact control step that breaks the chain.
- Do not write "use Entra security" as a control; specify the claim, API, or check.
- Do not leave residual risk empty just because the design feels strong on paper.

## Acceptance Criteria

- All five threat categories addressed (may be combined if attack paths overlap)
- Control mapping ties each control to a specific implementation point
- Residual risk section is honest — not empty
- Test assertions are specific code-level or integration-level tests — not "we'll test it"
- Flow diagram covers at least four exchange steps
