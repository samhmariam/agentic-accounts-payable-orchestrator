# Day 5 Module Wormhole

## Why This Matters to an FDE

Durable state work is the difference between a demo and a recoverable production system. FDEs need to resume safely, explain checkpoints, and keep side effects idempotent under pressure.

## Customer Context

An approver reopened a paused invoice after a partial outage. The customer wants the workflow resumed without duplicate approvals, duplicate recommendations, or policy drift.

## Cost of Failure

If stale resume tokens are accepted, duplicate or misrouted side effects can hit downstream finance systems and create expensive manual cleanup.

## Persistent Constraints

- `regulated_invoice_auditability`: Every financial decision path must leave auditable evidence that survives hostile review.
- `latency_budget_guardrails`: Queue, retry, and latency controls must be explicit enough to defend under customer SLA pressure.
- `authoritative_retrieval_sources`: Retrieval must prefer authoritative source systems over stale or ambiguous evidence.
- `no_public_endpoints`: Production-bound AI and data services must not expose public network access.
- `fail_closed_decisions`: Risky automation paths must fail closed and require explicit human review.
- `durable_resume_idempotency`: Durable state recovery must resume safely without duplicating side effects.

## FDE Implementation Cycle

- Customer Reality: inspect the live incident and portal surface before you theorize.
- Diagnostic Bridge: prove the state in Marimo and name the API or SDK call that matches the portal behavior.
- Production Engineering: patch the durable code in the repo, not inside the notebook.
- Chaos Gate: recover under the time box and defend the trade-off in review language.

## Mastery Gate

- `uv run python -m pytest tests/day5/integration/test_resume_service.py tests/day5/integration/test_idempotent_recommendation_resume.py -q && uv run aegisap-lab artifact rebuild --day 05`
- `uv run aegisap-lab audit-production --day 05 --strict`

## Chaos Gate

- Failure signal: The durable workflow stalls or resumes unsafely after interruption, risking duplicate state transitions.
- Diagnostic surface: Cosmos-style thread state, notebook resume prototype, and the resume/checkpoint services.
- Expected recovery artifact: `build/day5/golden_thread_day5_resumed.json`
- Time box: 25 minutes

## Day X File Manifest

Do not edit code in this module folder.

- Diagnostic Notebook: `notebooks/day_5_multi_agent_orchestration.py`
- Primary Day Doc: `docs/DAY_05.md`
- Rosetta Stone Bridge: `notebooks/bridges/day05_durable_state.md`
- Production Target: `src/aegisap/day5/workflow/resume_service.py`
- Production Target: `src/aegisap/day5/workflow/checkpoint_manager.py`
- Scenario Pack: `scenarios/day05`
- Verification Command: `uv run python -m pytest tests/day5/integration/test_resume_service.py tests/day5/integration/test_idempotent_recommendation_resume.py -q`
- Verification Command: `uv run aegisap-lab artifact rebuild --day 05`

## Automated Drill

- List drills: `uv run aegisap-lab drill list --day 05`
- Inject default drill: `uv run aegisap-lab drill inject --day 05`
- Reset active drill: `uv run aegisap-lab drill reset --day 05`
- Constraint lineage artifact after mastery: `build/day5/constraint_lineage.json`
