# CAPABILITY ALLOCATION MEMO

## Purpose

Document the rationale for routing each system capability to a specific model
tier, with cost and quality trade-off reasoning that can survive a finance review.

## Required Headings

1. Capability inventory — every system capability, its model tier assignment, and the primary routing signal
2. Cost vs quality trade-off per capability — why this tier was chosen and what the quality downside is
3. Zero-tolerance protected capabilities — capabilities that must not be downgraded under cost pressure
4. Optimisation lever priority — ordered list of levers to pull given a cost-reduction target
5. Finance-facing summary — one-paragraph explanation of the model cost structure for a non-technical audience

## Guiding Questions

- Which capability has the most uncertain quality/cost trade-off?
- If forced to cut cost by 25%, which capability routing change gives the most saving with the least compliance risk?
- How do you explain to a CFO why a zero-tolerance capability cannot be moved to a cheaper model?
- What observability signal tells you a routing change degraded quality before a user complaint arrives?

## Acceptance Criteria

- Minimum 5 capabilities in the inventory
- Zero-tolerance protected list is explicit (not "important capabilities")
- Optimisation lever list is numbered (most safe to least safe ordering)
- Finance-facing summary avoids model names and uses business-outcome language
- Each trade-off entry names the specific quality downside (not "some degradation")
