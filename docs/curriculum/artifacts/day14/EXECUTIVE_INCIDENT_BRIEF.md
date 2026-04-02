# EXECUTIVE INCIDENT BRIEF

<!-- CAPSTONE_B: This artifact applies to both AP and claims intake transfer domain -->

## Purpose

Produce the one-page executive communication during or immediately after a
production incident — structured for a CTO, CFO, or board audience with no
technical background.

## Required Headings

1. Headline — one sentence: what happened, current status, business impact
2. Customer / business impact — what users or business processes are affected and since when
3. Current status — what is being done right now and by whom
4. Root cause (if known) — plain language, one paragraph
5. Recovery timeline — estimated time to full restoration (must be a range, not "soon")
6. Risk of continued operation — if service is partially running, what the risk is
7. Actions required from this audience — any decision or resource the executive must provide

## Guiding Questions

- What is the first question a CFO would ask that this brief does not answer?
- How do you convey urgency without creating panic?
- What is the worst thing to leave out of this brief?
- At what point of recovery do you send a follow-up brief, and who owns that trigger?

## Structural Example — Executive Brief Shape

- Headline: `Claims intake automation is operating in degraded mode, no data loss is confirmed, and 18% of new submissions are waiting for manual review as of 14:20 UTC.`
- Customer / business impact: `Provider-submitted claims are still being received, but exceptions are taking 25-40 minutes longer to route. No payments have been released incorrectly.`
- Current status: `The incident commander has halted the canary rollout, restored traffic to the prior version, and assigned platform and integration leads to verify queue recovery and private connectivity.`
- Recovery timeline: `We expect a stable state in 30-60 minutes if the rollback holds; otherwise we will shift all intake to the manual queue and provide a revised estimate within 20 minutes.`
- Actions required: `Approve temporary overtime coverage for the claims operations team if manual backlog exceeds 250 cases by 16:00 UTC.`

## Anti-Patterns To Avoid

- Do not lead with internal system names or acronyms.
- Do not say "no impact" if impact is still being assessed; say what is known and unknown.
- Do not give a point estimate unless the recovery step is already complete.

## Acceptance Criteria

- Total length: 1 page or fewer (approximately 400 words maximum)
- Headline is one sentence with all three elements (what, status, impact)
- Recovery timeline is a range (not a point estimate)
- Business impact is quantified or explicitly acknowledged as unquantified
- Actions required from the audience is specific — not "stay informed"
- No technical acronyms or system names in the main body (use plain language equivalents)
