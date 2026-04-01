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

## Acceptance Criteria

- Default posture is explicit and is deny-all (not "restrictive")
- Minimum 5 entries in permitted inventory
- Every entry has an expiry or a "permanent with annual review" designation
- Blocked destination classes are named categories (not "dangerous destinations")
- Policy change control names a role and requires evidence (not just approval)
