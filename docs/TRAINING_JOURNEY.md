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

## Capstone B — Transfer Domain (Days 12–14)

Capstone B introduces a second domain to test whether the trainee can apply
AegisAP patterns without AegisAP's familiar fixtures.

**Primary transfer domain:** Claims intake for a medical supplier.
**Secondary:** Customer onboarding (product extension scenario).

The trainee is given claims intake fixtures in `fixtures/capstone_b/claims_intake/`
and must implement the same safety guarantees, governance process, and release
evidence pack they built for invoices — but for an unfamiliar document schema
with different compliance constraints.

A hidden assessor case (`fixtures/capstone_b/_assessor_only/`) is used to test
whether the trainee's implementation handles an adversarial input they have never
seen. The trainee is informed this case exists but has not seen its contents.

Capstone B scoring follows the same 100-point rubric. Days 12, 13, and 14 each
require the CAPSTONE_B marker in their primary doc and in the oral defense session.

## Eight Mental Models

The programme develops eight permanent mental models. These are introduced across
the first four days and are examinable from the moment they appear.

See `docs/curriculum/MENTAL_MODELS.md` for full definitions and the day-presence
matrix showing first appearance and reinforcement days.

| Model | First appears |
|---|---|
| Build an agent or not | Day 1 |
| Zero-tolerance vs tunable NFRs | Day 2 |
| Authority and source-of-truth hierarchy | Day 2 |
| Control plane vs data plane | Day 4 |
| Reversible vs irreversible actions | Day 4 |
| Blast radius minimisation | Day 1 |
| Release evidence over intuition | Day 8 |
| "Who must approve this" before "how to code this" | Day 2 |

## Grading and Graduation

Each day is scored on a 100-point scale (35/20/15/15/15 across five dimensions).
The daily pass bar is **80**. The elite bar is **90**.

Three graduation tiers:

| Tier | Score threshold | Key differentiator |
|---|---|---|
| Graduate | ≥ 80 average, all days pass | Passed all gates |
| Strong FDE | ≥ 85 average | Hostile review passed, reusable artifacts |
| Top Talent | ≥ 90 average | Transfer capstone passed, multi-audience communication |

Full tier definitions in `docs/curriculum/GRADUATION_RUBRIC.md`.

That is the standard for all future curriculum expansion.
