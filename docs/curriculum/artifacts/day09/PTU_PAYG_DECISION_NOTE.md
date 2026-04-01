# PTU vs PAYG DECISION NOTE

## Purpose

Document the commercial decision about provisioned throughput units (PTU) vs
pay-as-you-go (PAYG) with the financial and operational trade-off reasoning.

## Required Headings

1. Consumption profile — current and projected token consumption by tier
2. PTU break-even analysis — at what utilisation rate PTU becomes cost-effective vs PAYG
3. Operational risks of PTU — over-provisioning risk, under-utilisation cost, commitment duration
4. Decision and rationale
5. Review trigger — the observable condition that should prompt re-evaluation

## Guiding Questions

- At what monthly token volume does PTU pay off in this workload?
- What is the blast radius of committing to a PTU reservation that turns out to be over-provisioned?
- Who approves a two-year PTU commitment and what financial evidence do they require?
- What happens to in-flight requests if PTU capacity is exhausted?

## Structural Example — Break-Even Table

| Scenario | Monthly tokens | PAYG cost (USD) | PTU cost (USD) | Delta |
|---|---|---|---|---|
| Conservative | `<number>` | `<calculated>` | `<calculated>` | `<delta>` |
| Expected | `<number>` | `<calculated>` | `<calculated>` | `<delta>` |
| Peak | `<number>` | `<calculated>` | `<calculated>` | `<delta>` |

## Acceptance Criteria

- Break-even table has at least three scenarios with numbers (not "depends on usage")
- Operational risks are specific (not "it might cost more")
- Decision is explicit — one of: PAYG, PTU, hybrid with routing rules
- Review trigger is an observable signal (not "annually")
- Approver role is named in the decision section
