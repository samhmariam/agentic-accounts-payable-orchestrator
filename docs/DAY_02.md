# Day 2 - Resilience Under Load, NFR Enforcement, and Ownership

Primary learner entrypoint: `modules/day_02_resilience_ownership/README.md`.

## Why This Matters to an FDE

Enterprise FDE work starts with constraints, not code. If you cannot make reliability and ownership legible, the customer experiences every retry storm as your fault.

## Customer Context

The customer architecture board is pressing for throughput gains during an invoice spike, but the service owner refuses any change that weakens queue safety or approval lines.

## Persistent Constraints

- `regulated_invoice_auditability`: Every financial decision path must leave auditable evidence that survives hostile review.
- `latency_budget_guardrails`: Queue, retry, and latency controls must be explicit enough to defend under customer SLA pressure.

## Incident Entry

```bash
uv run aegisap-lab incident start --day 02
```

## Mastery Gate

- `uv run python -m pytest tests/day2/test_resilience_controls.py tests/day8/test_retry_policy.py -q && uv run aegisap-lab artifact rebuild --day 02`

## Verification Commands

```bash
uv run python -m pytest tests/day2/test_resilience_controls.py tests/day8/test_retry_policy.py -q
uv run aegisap-lab artifact rebuild --day 02
```

## Key Files

- `modules/day_02_resilience_ownership/README.md`
- `notebooks/day_2_requirements_architecture.py`
- `notebooks/bridges/day02_resilience_controls.md`
- `src/aegisap/observability/retry_policy.py`
- `src/aegisap/resilience/backpressure.py`
- `scenarios/day02`
