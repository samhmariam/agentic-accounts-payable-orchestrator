# EGRESS CONTROL POLICY

<!-- CAPSTONE_B: This artifact applies to both AP and claims intake transfer domain -->

## Purpose

Define all permitted egress paths from the system, the justification for each,
and the monitoring and enforcement mechanism.

## Required Headings

1. Default posture — what the default egress rule is (must be deny-all unless explicitly stated otherwise with rationale)
2. Permitted egress inventory (destination, port, protocol, justification, owner, expiry, monitoring signal)
3. Blocked destination classes — categories of destination that are blocked with no exception path
4. Egress monitoring — what alerts fire on unexpected or failed egress attempts
5. Policy change control — who approves a new permitted egress entry and what evidence is required

## Guiding Questions

- Which egress path is most likely to be added informally without a policy change?
- What is the blast radius of an unexpected outbound connection from the system?
- How is an expired egress permit monitored for non-removal?
- What would an external auditor find most suspicious in the current egress inventory?

## Structural Example — Permitted Egress Inventory Rows

| Destination | Port / protocol | Justification | Owner | Expiry | Monitoring signal |
|---|---|---|---|---|---|
| Azure OpenAI Private Endpoint FQDN | `443/TCP` | Primary inference path for invoice and claim reasoning | Platform engineering lead | Permanent, annual review | NSG flow logs + synthetic prompt probe |
| Azure AI Search Private Endpoint FQDN | `443/TCP` | Retrieval path for policy and vendor knowledge | Search service owner | Permanent, annual review | DNS resolution probe + query canary |
| Service Bus namespace over Private Link | `5671/TCP` | Async orchestration and DLQ drain workflow | Integration lead | Permanent, annual review | Queue depth alert + connection health check |
| Payer eligibility endpoint allowlist | `443/TCP` | Claims-intake dependency for adjudication enrichment | Claims integration owner | `2026-09-30` | Firewall egress logs + transaction failure alert |
| GitHub OIDC token exchange endpoints | `443/TCP` | CI/CD federation during deployment only | DevSecOps lead | Permanent, annual review | Workflow audit log + deployment health signal |

## Anti-Patterns To Avoid

- Do not list "internet" or "Azure services" as a destination class.
- Do not mark an entry as permanent unless it has an annual review owner.
- Do not justify an egress path with "needed by application" alone; say what breaks and who owns it.

## Acceptance Criteria

- Default posture is explicit and is deny-all (not "restrictive")
- Minimum 5 entries in permitted inventory
- Every entry has an expiry or a "permanent with annual review" designation
- Blocked destination classes are named categories (not "dangerous destinations")
- Policy change control names a role and requires evidence (not just approval)
