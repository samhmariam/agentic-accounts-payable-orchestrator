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

## Learning Contract

Every day should end with:

- one command to run
- one artifact to inspect
- one exit condition to prove
- one Azure concept that becomes more concrete than the day before

That is the standard for all future curriculum expansion.
