# NETWORK DEPENDENCY REGISTER

<!-- CAPSTONE_B: This artifact applies to both AP and claims intake transfer domain -->

## Purpose

Enumerate every network-layer dependency required by the system, with approval
status, lead time, and contingency for each.

## Required Headings

1. Dependency inventory table (ID, dependency, type, required by date, approval owner, status, lead time, contingency)
2. Critical path dependencies — which dependencies block go-live if unresolved
3. Private endpoint requirement map — which endpoints must be private-endpoint-only and why
4. Egress permit inventory — any permitted outbound traffic with its justification and expiry
5. Dependency risk summary — top two risks and their mitigations

## Dependency Types

- Private endpoint (PE)
- DNS resolution
- Firewall rule opening
- VNet peering
- Service endpoint policy
- DNS-private-zone link

## Guiding Questions

- Which dependency has the longest approval lead time and what is the contingency if it slips?
- Which dependency is most likely to be mis-classified as low priority?
- What is the blast radius if a private endpoint approval is not obtained before cutover?
- Who holds the network dependency register during the deployment window?

## Structural Example — Dependency Inventory Rows

| ID | Dependency | Type | Required by | Approval owner | Status | Lead time | Contingency |
|---|---|---|---|---|---|---|---|
| NET-01 | Azure OpenAI private endpoint approval | PE | 10 business days before staging cutover | Platform networking manager | Approved | 7 business days | Hold go-live; no public fallback permitted |
| NET-02 | Private DNS zone link for `privatelink.openai.azure.com` | DNS-private-zone link | 5 business days before probe run | Cloud platform lead | In progress | 3 business days | Manual hosts-file validation in staging only, then re-run automated probe |
| NET-03 | Service Bus namespace firewall exception for build agent subnet | Firewall rule opening | 3 business days before release rehearsal | Messaging owner | Approved | 2 business days | Shift rehearsal to self-hosted runner in approved subnet |
| NET-04 | Payer portal VNet peering for claims transfer domain | VNet peering | 15 business days before UAT | Enterprise network architect | Requested | 10 business days | Use recorded fixture responses for training only; cannot count as production evidence |
| NET-05 | Storage account private endpoint for document blobs | PE | 7 business days before validation run | Data platform owner | Approved | 5 business days | Block ingestion tests until PE resolves privately |

## Anti-Patterns To Avoid

- Do not mark every dependency as critical path; reserve that label for actual go-live blockers.
- Do not treat a training-only contingency as an acceptable production workaround.
- Do not leave approval owner blank because "the network team" is known informally.

## Acceptance Criteria

- Minimum 5 dependencies registered
- Critical path section is explicit — not every dependency is critical
- Private endpoint requirement map covers all AI and storage services
- Egress permits have expiry dates and a renewal owner
- Dependency risk summary is in business language (not "firewall rule not opened")
