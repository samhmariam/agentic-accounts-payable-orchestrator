# Day 9: Cost, Speed, Routing, Caching, and Optimisation

Day 9 makes capability allocation explicit. AegisAP no longer treats model
choice as a single global deployment setting. Instead, the runtime routes by
task class and case risk, persists that choice into workflow state, and records
the cost impact at the workflow level.

## Target State

- Day 1 extraction and Day 4 planning share one model gateway.
- Every live model call emits a routing decision, selected deployment, and a
  workflow cost ledger entry.
- Semantic cache reuse is conservative, explainable, and disabled for risky
  paths.
- Back-pressure never silently downgrades compliance-sensitive work.
- Day 9 routing experiments are judged by slice, not aggregate average.

## Runtime Additions

- `src/aegisap/routing/` holds task classes, routing policy, and the shared
  gateway.
- `src/aegisap/cost/` holds the workflow cost ledger model and rollups.
- `src/aegisap/cache/` holds cache policy plus the local in-memory semantic
  cache stub.
- `src/aegisap/resilience/` holds the Day 9 back-pressure policy.
- `src/aegisap/prompts/compiled/` holds versioned compiled-prompt artifacts.

## Acceptance Check

Day 9 is complete when:

- model routing is visible in traces and persisted state
- every live model call contributes to `cost_ledger`
- a low-risk task class can use the light deployment without material slice
  regression
- cached answers are bypassed automatically on high-risk or stale-evidence paths
- nightly regression can catch the “aggregate got better, VAT slice got worse”
  failure mode

---

## FDE Rubric — Day 9 (100 points)

| Dimension | Points |
|---|---|
| Routing correctness | 25 |
| Cost reasoning | 25 |
| Observability as control | 20 |
| Finance communication quality | 15 |
| Oral defense | 15 |

**Pass bar: 80.  Elite bar: 90.**

## Oral Defense Prompts

1. Which capability did you route to the mini model and what is the quality degradation risk if that routing decision is wrong?
2. Finance demands a 30% cost cut. Walk through which lever you would pull first and what zero-tolerance controls you would not touch.
3. Who approves a PTU commitment in your enterprise, and what observability evidence would they require before signing a two-year reservation?

## Artifact Scaffolds

- `docs/curriculum/artifacts/day09/CAPABILITY_ALLOCATION_MEMO.md`
- `docs/curriculum/artifacts/day09/COST_GOVERNANCE_POLICY.md`
- `docs/curriculum/artifacts/day09/PTU_PAYG_DECISION_NOTE.md`
