# SECURITY REVIEW PACKET

## Purpose

Provide the security team with everything they need to review and approve the
release from an identity, access, and secrets management perspective.

## Required Headings

1. Identity planes summary — workload identity, pipeline identity, admin identity, and their separation evidence
2. Secrets management inventory — every secret in scope, its store, rotation policy, and access control
3. Federated credential configuration — what federated credentials are configured, which identity they bind, and test evidence
4. Attack surface delta — what changed in the attack surface since the last approved release
5. Compensating controls — any open risk item with its compensating control and expiry

## Guiding Questions

- Which identity plane is most likely to be over-privileged in this design?
- If a federated credential is mis-configured, what is the earliest detection point?
- Which secret has the highest blast radius if leaked and what is the rotation SLA?
- What evidence would the CISO require to approve federated credentials replacing a service principal key?

## Acceptance Criteria

- All three identity planes explicitly addressed (missing a plane is an automatic gap)
- Secrets inventory has rotation policy and access control for every entry
- Federated credential section includes test evidence (not assertions)
- Attack surface delta is a diff — not a full system description
- Compensating controls include an expiry date or review trigger (not "until resolved")
