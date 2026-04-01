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

## Acceptance Criteria

- All five threat categories addressed (may be combined if attack paths overlap)
- Control mapping ties each control to a specific implementation point
- Residual risk section is honest — not empty
- Test assertions are specific code-level or integration-level tests — not "we'll test it"
- Flow diagram covers at least four exchange steps
