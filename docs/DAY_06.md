# Day 6 - Data Authority, Review Boundaries, and Conflict Refusal

Primary learner entrypoint: `modules/day_06_data_authority/README.md`.

## Why This Matters to an FDE

Enterprise data integration is mostly refusal discipline. An elite FDE must know when conflicting sources or injected instructions mean the system should stop and escalate.

## Customer Context

A reviewer found a conflict between ERP data and the extracted invoice narrative. The customer expects the system to refuse unsafe blending and document who owns the discrepancy.

## Persistent Constraints

- `regulated_invoice_auditability`: Every financial decision path must leave auditable evidence that survives hostile review.
- `latency_budget_guardrails`: Queue, retry, and latency controls must be explicit enough to defend under customer SLA pressure.
- `authoritative_retrieval_sources`: Retrieval must prefer authoritative source systems over stale or ambiguous evidence.
- `no_public_endpoints`: Production-bound AI and data services must not expose public network access.
- `fail_closed_decisions`: Risky automation paths must fail closed and require explicit human review.
- `durable_resume_idempotency`: Durable state recovery must resume safely without duplicating side effects.
- `conflicting_authority_refusal`: Conflicting records or review evidence must trigger refusal rather than silent blending.

## Incident Entry

```bash
uv run aegisap-lab incident start --day 06
```

## Mastery Gate

- `uv run python -m pytest tests/day6/test_review_gate.py tests/day6/test_training_runtime_integration.py -q && uv run aegisap-lab artifact rebuild --day 06`
- `uv run aegisap-lab audit-production --day 06 --strict`

## Verification Commands

```bash
uv run python -m pytest tests/day6/test_review_gate.py tests/day6/test_training_runtime_integration.py -q
uv run aegisap-lab artifact rebuild --day 06
```

## Key Files

- `modules/day_06_data_authority/README.md`
- `notebooks/day_6_data_ml_integration.py`
- `notebooks/bridges/day06_review_boundary.md`
- `src/aegisap/day6/review/prompt_injection.py`
- `src/aegisap/day6/review/authority_boundary.py`
- `scenarios/day06`
