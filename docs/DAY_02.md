# Day 02

## Purpose

Day 02 adds explicit workflow state after Day 01 has already produced a trusted
`CanonicalInvoice`.

Instead of sending that invoice directly into downstream automation, Day 02
wraps it in a `WorkflowState` object and routes it through deterministic review
steps. The goal is to make control flow, evidence, and telemetry explicit.

If Day 01 rejects the invoice, Day 02 does not run.

## Pipeline

```text
InvoicePackageInput + ExtractedInvoiceCandidate
    ->
canonicalize_with_candidate(...) or run_day_01_intake(...)
    ->
CanonicalInvoice
    ->
make_initial_state(...)
    ->
LangGraph workflow
    ->
WorkflowState
```

The runnable entrypoint is `python -m aegisap.day2.run_workflow ...` in
`src/aegisap/day2/run_workflow.py`.

## Boundary with Day 01

Day 01 remains the strict intake boundary.

That means:

- invoices without a PO are rejected before Day 02
- `CanonicalInvoice` is the only invoice object Day 02 consumes
- Day 02 does not define a parallel invoice schema

Day 02 combines the Day 01 canonical invoice with the Day 01 `message_id` to
derive workflow identity:

- `invoice_id = invoice.invoice_number`
- `package_id = message_id`
- `thread_id = thread_{message_id}_{invoice_number}`

For now, vendor identity is based on `supplier_name` until an upstream master
vendor ID exists.

## Core models

### `WorkflowState`

Represents one invoice workflow thread.

It contains:

- workflow identity and timestamps
- the Day 01 `CanonicalInvoice`
- vendor context and verification state
- current route, status, and completed nodes
- evidence and recommendations
- metrics, totals, and idempotency guards

### `VendorContext`

Represents thread-local vendor review state.

This is where Day 02 stores vendor verification results so they cannot leak
across workflow threads through process-global memory.

### `WorkflowPolicy`

Represents deterministic routing configuration:

- `high_value_threshold`
- `route_precedence`

## Routes

Day 02 currently has three reachable paths:

- `high_value`
- `new_vendor`
- `clean_path`

The predicates are deterministic:

- `is_high_value`: `invoice.gross_amount >= HIGH_VALUE_THRESHOLD`
- `is_new_vendor`: supplier name not found in `KNOWN_VENDORS`

Precedence is:

1. `high_value`
2. `new_vendor`
3. `clean_path`

If more than one predicate is true, the first matching route wins and the
suppressed conditions are still recorded as evidence.

## Nodes

### `init_workflow`

Records that the workflow started from a Day 01 canonical invoice.

### `route_invoice`

Evaluates routing predicates and writes:

- `route`
- `route_reason`
- routing evidence
- suppressed-rule evidence when precedence hides another true condition

### `high_value_review`

Records that the invoice gross amount crossed the configured threshold and
emits the recommendation `manager_approval_required`.

### `new_vendor_review`

Records that the supplier is not present in the approved-vendor registry and
emits the recommendation `run_vendor_verification`.

### `clean_path_finalize`

Records that no deterministic control exception fired and marks the invoice as
completed.

### `finalize_workflow`

Appends final evidence and preserves aggregate latency/cost totals.

## Demo fixtures

The Day 02 demo fixtures live under `fixtures/day2/`.

Each fixture directory contains:

- `package.json`
- `candidate.json`

These are Day 01-shaped inputs. The demo first canonicalizes them into a real
`CanonicalInvoice`, then passes that invoice into the Day 02 workflow. This
keeps the demo aligned with the real application boundary.

Available fixture cases:

- `clean_path`
- `high_value`
- `new_vendor`

## Running the demo

If the project dependencies are installed through `pyproject.toml`, the Day 02
module can be run directly:

```bash
uv run python -m aegisap.day2.run_workflow clean_path --known-vendor
uv run python -m aegisap.day2.run_workflow high_value --known-vendor
uv run python -m aegisap.day2.run_workflow new_vendor
```

The `--known-vendor` flag overrides registry lookup for the fixture run. If it
is omitted, known-vendor status is inferred from `KNOWN_VENDORS`.

## Tests

Day 02 tests cover:

- workflow state initialization from real Day 01 output
- route selection and precedence
- graph behavior for clean path, high value, and new vendor
- idempotent recommendations
- thread-local vendor verification state
- tracing and aggregate metrics
- rejection of missing-PO inputs before Day 02 starts

Run them with:

```bash
pytest -q tests/day2
```

To run Day 01 and Day 02 boundary coverage together:

```bash
pytest -q tests/day2 tests/test_day_01_fixtures.py tests/test_day_01_money.py
```

## File map

- `src/aegisap/day2/state.py`: workflow state and initialization
- `src/aegisap/day2/predicates.py`: deterministic routing predicates
- `src/aegisap/day2/router.py`: route decision and evidence writing
- `src/aegisap/day2/nodes.py`: workflow node implementations
- `src/aegisap/day2/graph.py`: LangGraph assembly
- `src/aegisap/day2/run_workflow.py`: CLI/demo entrypoint
- `tests/day2/`: Day 02 coverage
- `docs/DAY_02_STATE_FLOW.md`: deeper state-flow walkthrough
