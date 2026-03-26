# Training Journey

The AegisAP Golden Thread uses one invoice case from raw intake through durable
approval resumption. The repo is meant to feel like a progressive build, not a
set of disconnected demos.

## Golden Thread Case

- Supplier: `Acme Office Supplies`
- Invoice: `INV-3001`
- PO: `PO-9001`
- Amount: `GBP 12,500.00`
- Vendor ID: `VEND-001`
- Approval route: high-value threshold lowered in Day 4 to force controller
  involvement without changing the domain data set

The fixture sources live in
[fixtures/golden_thread/](/workspaces/agentic-accounts-payable-orchestrator/fixtures/golden_thread).

## Day-by-Day Story

### Day 1

The learner starts with an invoice package and turns it into a trusted
`CanonicalInvoice`. The system either emits a canonical invoice or rejects the
record at the intake boundary.

### Day 2

The canonical invoice becomes explicit workflow state. Routing, review
conditions, telemetry, and recommendations are now inspectable.

### Day 3

The same case is enriched with live retrieval. Azure AI Search supplies
unstructured evidence, while local authority rules decide what counts as truth.

### Day 4

The case moves from implicit sequencing to explicit planning. The system asks a
planner for typed JSON, validates it, executes the plan, and then decides
whether the recommendation is ready or requires manual review.

### Day 5

The case pauses at a controller approval gate. The state is written to durable
storage, the process can die, and the workflow later resumes from the latest
checkpoint without replaying side effects.

### Day 6

The case now faces a hard safety gate. The system no longer optimizes for
completion. It emits one typed outcome:

- `approved_to_proceed`
- `needs_human_review`
- `not_authorised_to_continue`

The refusal path is now a first-class, auditable product outcome rather than an
implicit failure.

### Day 7

The same case now becomes enterprise-reviewable. The runtime identity is
separated from admin identities, residual secrets move behind Key Vault access
contracts, Search key fallback is eliminated, and every sensitive outcome emits
redacted audit evidence tied to thread state and trace context.

### Day 8

The same case now becomes observable and regression-testable. Every workflow run
emits one canonical trace with correlated task and dependency spans, silent
latency or retry regressions become queryable, and the evaluation sheet becomes
an executable regression suite that can run in CI and on a deployed sentinel.

### Day 9

The same case now becomes economically governable. Model choice is no longer an
incidental env var: routing is explicit, cache reuse is bounded by policy,
workflow cost is ledgered per run, and optimisation is allowed only on modules
with slice-level regression evidence strong enough to catch silent compliance
regressions.

### Day 10

The same case now becomes release-governed. A new container revision is not
“good” because it starts; it is good only if health, trace correlation, cost,
synthetic accuracy, refusal behavior, and replay safety all hold after deploy.
The release unit is an immutable ACA revision, and rollback is part of the
design rather than an afterthought.

## Learning Contract

Every day should end with:

- one command to run
- one artifact to inspect
- one exit condition to prove
- one Azure concept that becomes more concrete than the day before

That is the standard for all future curriculum expansion.
