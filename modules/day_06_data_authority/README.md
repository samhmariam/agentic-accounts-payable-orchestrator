# Day 6 Module Wormhole

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

## FDE Implementation Cycle

- Customer Reality: inspect the live incident and portal surface before you theorize.
- Diagnostic Bridge: prove the state in Marimo and name the API or SDK call that matches the portal behavior.
- Production Engineering: patch the durable code in the repo, not inside the notebook.
- Chaos Gate: recover under the time box and defend the trade-off in review language.

## Mastery Gate

- `uv run python -m pytest tests/day6/test_review_gate.py tests/day6/test_training_runtime_integration.py -q && uv run aegisap-lab artifact rebuild --day 06`
- `uv run aegisap-lab audit-production --day 06 --strict`

## Chaos Gate

- Failure signal: The review path accepts conflicting authority instead of refusing and escalating the dispute.
- Diagnostic surface: Review notebook evidence, authority-boundary code, and refusal instrumentation.
- Expected recovery artifact: `build/day6/golden_thread_day6.json`
- Time box: 25 minutes

## Day X File Manifest

Do not edit code in this module folder.

- Diagnostic Notebook: `notebooks/day_6_data_ml_integration.py`
- Primary Day Doc: `docs/DAY_06.md`
- Rosetta Stone Bridge: `notebooks/bridges/day06_review_boundary.md`
- Production Target: `src/aegisap/day6/review/prompt_injection.py`
- Production Target: `src/aegisap/day6/review/authority_boundary.py`
- Scenario Pack: `scenarios/day06`
- Verification Command: `uv run python -m pytest tests/day6/test_review_gate.py tests/day6/test_training_runtime_integration.py -q`
- Verification Command: `uv run aegisap-lab artifact rebuild --day 06`
