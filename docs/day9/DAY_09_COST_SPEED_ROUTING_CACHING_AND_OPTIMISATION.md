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
