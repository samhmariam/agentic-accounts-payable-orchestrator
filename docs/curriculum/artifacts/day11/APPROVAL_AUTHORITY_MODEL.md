# APPROVAL AUTHORITY MODEL

## Purpose

Define which identity or role can approve which action class, making the
authority delegation chain explicit and auditable.

## Required Headings

1. Authority hierarchy — the delegation chain from root authority to action-level approver
2. Approval scope table (action class, minimum authority, co-approval required, evidence required, audit log required)
3. Delegation boundaries — what authority cannot be delegated and why
4. Authority confusion scenarios — at least two scenarios where the wrong identity claims approval rights
5. Revocation procedure — how an explicitly delegated authority is revoked

## Guiding Questions

- Which approval is most likely to be claimed by the wrong identity in a multi-agent scenario?
- If the delegated authority token expires mid-workflow, what is the safe default action?
- Who is authorised to grant a new delegation, and can that authority be further delegated?
- What is the audit record that proves a delegation was legitimate at the time it was exercised?

## Acceptance Criteria

- Hierarchy is a directed graph or numbered list (not prose)
- Non-delegatable authorities are explicitly called out with a rationale
- Authority confusion scenarios name the specific attack or mistake, not just "confusion"
- Revocation procedure includes a propagation mechanism (how downstream components learn of the revocation)
- Approval scope table covers at least 5 action classes
