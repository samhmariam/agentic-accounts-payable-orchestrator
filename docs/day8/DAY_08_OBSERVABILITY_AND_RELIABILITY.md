# Day 8 - Observability and Reliability Engineering

Day 8 turns AegisAP into an inspectable workflow rather than a black box. Every
hosted workflow run now carries a distinct `workflow_run_id`, one canonical
trace, correlated audit metadata, and a repeatable regression dataset for
behavioral drift.

## What Changes

- OpenTelemetry becomes the single in-app instrumentation layer.
- Azure Monitor/Application Insights receives platform and dependency telemetry.
- LangSmith becomes an optional run-level trace sink with shared correlation IDs.
- Day 4, Day 6, and Day 5 runtime boundaries emit task spans, dependency spans,
  typed reliability events, and business metrics.
- The Day 3/6 evaluation sheet becomes a Day 8 regression dataset under
  `data/day8/eval/`.

## New Runtime Contract

- `workflow_run_id` is distinct from `case_id`.
- `thread_id` remains the resumable business thread identifier.
- `trace_id`, `traceparent`, and LangSmith IDs persist inside durable state.
- API responses expose a `correlation` object so operators can pivot from
  business case to trace to audit row.

## Exit Checks

1. `uv run pytest tests/day8 -q`
2. `uv run python -m compileall src`
3. `az bicep build --file infra/monitoring/alerts/alerts.bicep`
4. `az bicep build --file infra/full.bicep`

Day 8 is complete when:

- every workflow run emits a root span plus task and dependency child spans
- pause/resume preserves `workflow_run_id` and trace context
- the regression dataset is executable in CI
- monitoring assets exist for workbook dashboards and silent-failure alerts
- no raw case or thread identifiers leak into telemetry attributes
