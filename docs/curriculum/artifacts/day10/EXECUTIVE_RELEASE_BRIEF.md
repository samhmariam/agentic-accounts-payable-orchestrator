# EXECUTIVE RELEASE BRIEF

## Purpose

Provide a one-page release summary for the CTO or VP-level sponsor, focused on
business outcomes, risk, and decision — not technical implementation.

## Required Headings

1. Release headline — one sentence: what is releasing, when, and what it delivers to the business
2. Business value — what the release enables or improves, with a measurable claim where possible
3. Risk and mitigations — two or three risks in business language with their mitigations
4. Decision required — what the executive must decide or confirm before release proceeds
5. Rollback position — what happens to the business if rollback is required

## Guiding Questions

- Can a finance controller read this and understand both the value and the risk?
- What is the one thing the executive will ask that is not covered in the current draft?
- How do you quantify business value without overpromising?
- What is the rollback impact in business terms (not technical terms)?

## Structural Example — Brief Shape

- Release headline: `Tomorrow's release moves low-value invoice recommendations into managed staging approval, reducing manual triage time while keeping high-value cases under finance control.`
- Business value: `If the guarded rollout behaves as expected, AP analysts recover 6-8 hours per day of manual triage time without changing current approval authority.`
- Risk and mitigations: `Primary risks are regression in compliance-sensitive routing, deployment drift, and rollout cost variance; each is covered by pre-release gates, named owners, and rollback within the same shift.`
- Decision required: `Approve staging-to-production promotion only if all six gates stay green through the observation window and no exception request is opened.`
- Rollback position: `If rollback is required, analysts continue the existing manual process and no supplier-facing workflow changes are exposed.`

## Anti-Patterns To Avoid

- Do not write a technical status report and rename it an executive brief.
- Do not describe rollback as "revert to previous revision" without the business effect.
- Do not claim business value with fake precision if the baseline is not yet measured.

## Acceptance Criteria

- Total length: 1 page or fewer (approximately 400 words maximum)
- No code, no technical architecture in the main body
- Business value includes a measurable claim or an explicit acknowledgement that measurement is TBD
- Decision required is specific — not "please approve"
- Rollback position is in business terms (e.g., "existing manual process resumes")
