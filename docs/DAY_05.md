# Day 5 - Multi-Agent Orchestration, Durable State, and Resume Safety

Primary learner entrypoint: `modules/day_05_durable_state/README.md`.

## Why This Matters to an FDE

Durable state work is the difference between a demo and a recoverable production system. FDEs need to resume safely, explain checkpoints, and keep side effects idempotent under pressure.

## Customer Context

An approver reopened a paused invoice after a partial outage. The customer wants the workflow resumed without duplicate approvals, duplicate recommendations, or policy drift.

## Persistent Constraints

- `regulated_invoice_auditability`: Every financial decision path must leave auditable evidence that survives hostile review.
- `latency_budget_guardrails`: Queue, retry, and latency controls must be explicit enough to defend under customer SLA pressure.
- `authoritative_retrieval_sources`: Retrieval must prefer authoritative source systems over stale or ambiguous evidence.
- `no_public_endpoints`: Production-bound AI and data services must not expose public network access.
- `fail_closed_decisions`: Risky automation paths must fail closed and require explicit human review.
- `durable_resume_idempotency`: Durable state recovery must resume safely without duplicating side effects.

## Incident Entry

```bash
uv run aegisap-lab incident start --day 05
```

## Mastery Gate

- `uv run python -m pytest tests/day5/integration/test_resume_service.py tests/day5/integration/test_idempotent_recommendation_resume.py -q && uv run aegisap-lab artifact rebuild --day 05`
- `uv run aegisap-lab audit-production --day 05 --strict`

## Verification Commands

```bash
uv run python -m pytest tests/day5/integration/test_resume_service.py tests/day5/integration/test_idempotent_recommendation_resume.py -q
uv run aegisap-lab artifact rebuild --day 05
```

## Key Files

- `modules/day_05_durable_state/README.md`
- `notebooks/day_5_multi_agent_orchestration.py`
- `notebooks/bridges/day05_durable_state.md`
- `src/aegisap/day5/workflow/resume_service.py`
- `src/aegisap/day5/workflow/checkpoint_manager.py`
- `scenarios/day05`

## Automated Drill

- `uv run aegisap-lab drill list --day 05`
- `uv run aegisap-lab drill inject --day 05`
- `uv run aegisap-lab drill reset --day 05`
- `uv run aegisap-lab mastery --day 05` writes `build/day5/constraint_lineage.json` so later reviews can see the inherited rules this day still carries.
