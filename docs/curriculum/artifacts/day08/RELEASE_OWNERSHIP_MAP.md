# RELEASE OWNERSHIP MAP

## Purpose

Name the human owner of every element of the release process, so there is no
ambiguity about who holds accountability when a release degrades or must roll back.

## Required Headings

1. Release ownership table (release element, owner role, deputy, decision authority, escalation if unavailable)
2. Release machinery components — IaC, pipeline, secrets, identity, monitoring
3. Break-glass access ownership — who holds break-glass credentials, under what conditions, and with what audit requirement
4. Handoff points — moments where ownership transfers from one role to another, with a formal handoff record requirement
5. Post-release ownership — who owns monitoring and rollback authority after go-live

## Guiding Questions

- If the pipeline identity drifts at 02:00 and the primary owner is unavailable, who holds the first response?
- Which release element is most likely to have ownership ambiguity after a team reorganisation?
- What is the blast radius if break-glass is used without audit logging?
- Who owns the decision to roll back — the platform team, the product team, or the CAB chair?

## Structural Example — Ownership Rows

| Release element | Owner role | Deputy | Decision authority | Escalation if unavailable |
|---|---|---|---|---|
| GitHub Actions deployment pipeline | Platform engineer | DevSecOps lead | Pause or re-run workflow | CAB chair for cutover delay |
| ACA revision traffic shift | Operations lead | Platform engineer | Promote, pause, or rollback | Incident commander once live traffic is affected |
| Gate exception record | Service owner | Product director | Request exception, not self-approve | CAB chair plus security lead |
| Break-glass credential use | Platform security lead | Operations manager | Authorize emergency use only | CTO delegate if both unavailable |

## Anti-Patterns To Avoid

- Do not name a deputy who cannot actually exercise the authority.
- Do not describe ownership transfer as "deployment team takes over" without a specific moment and record.
- Do not let rollback authority float between teams during the highest-risk window.

## Acceptance Criteria

- Every release element has an owner and a deputy (not "TBD")
- Break-glass section has an explicit audit requirement (who logs, what fields, when)
- Handoff points are discrete, named moments — not "during deployment"
- Post-release ownership specifies a duration (e.g., "owner holds rollback authority for 72 hours post-deploy")
- Table uses roles from the STAKEHOLDER_MAP for consistency
