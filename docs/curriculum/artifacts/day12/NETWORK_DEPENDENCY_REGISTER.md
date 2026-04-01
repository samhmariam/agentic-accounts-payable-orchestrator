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

## Acceptance Criteria

- Minimum 5 dependencies registered
- Critical path section is explicit — not every dependency is critical
- Private endpoint requirement map covers all AI and storage services
- Egress permits have expiry dates and a renewal owner
- Dependency risk summary is in business language (not "firewall rule not opened")
