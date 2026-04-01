# DATA AUTHORITY CHART

## Purpose

Define the authoritative source for every class of data the system reads or
writes, resolve conflicts before they occur, and assign a human owner to each
source.

## Required Headings

1. Data class inventory (data class, authoritative source, secondary sources allowed, owner role, update mechanism)
2. Conflict resolution hierarchy — when sources disagree, the numbered order of precedence
3. Degraded-mode behaviour — which data classes can tolerate stale reads and for how long
4. Write-back rules — which data can the agent write back to, through what mechanism, and with what approval
5. Cross-boundary data flow — any data that crosses an external system boundary and the controls applied

## Guiding Questions

- Which data class conflict is most likely to cause an incorrect payment recommendation?
- If the authoritative source is unavailable, which secondary source is acceptable and for how long?
- Who owns the conflict resolution hierarchy — is it documented outside this artifact?
- What is the blast radius if the agent writes stale data back to the system of record?

## Acceptance Criteria

- Minimum 6 data classes (invoice data, vendor data, policy rules, audit log, user identity, approval status are starting points)
- Conflict resolution hierarchy is a numbered list (not prose)
- Degraded-mode behaviour specifies a time bound, not just "temporarily"
- Write-back rules specify the approval step — not just "authorised users"
- Cross-boundary section is present even if the answer is "no cross-boundary flows in this design"
