# Day 2 Module Wormhole

## Why This Matters to an FDE

Enterprise FDE work starts with constraints, not code. If you cannot make reliability and ownership legible, the customer experiences every retry storm as your fault.

## Customer Context

The customer architecture board is pressing for throughput gains during an invoice spike, but the service owner refuses any change that weakens queue safety or approval lines.

## Cost of Failure

If queue and retry controls drift under load, invoice SLAs slip and the customer loses confidence in the team's operational ownership.

## Persistent Constraints

- `regulated_invoice_auditability`: Every financial decision path must leave auditable evidence that survives hostile review.
- `latency_budget_guardrails`: Queue, retry, and latency controls must be explicit enough to defend under customer SLA pressure.

## FDE Implementation Cycle

- Customer Reality: inspect the live incident and portal surface before you theorize.
- Diagnostic Bridge: prove the state in Marimo and name the API or SDK call that matches the portal behavior.
- Production Engineering: patch the durable code in the repo, not inside the notebook.
- Chaos Gate: recover under the time box and defend the trade-off in review language.

## Mastery Gate

- `uv run python -m pytest tests/day2/test_resilience_controls.py tests/day8/test_retry_policy.py -q && uv run aegisap-lab artifact rebuild --day 02`

## Chaos Gate

- Failure signal: Retry policy and backpressure assumptions no longer match observed queue pressure and latency targets.
- Diagnostic surface: Azure OpenAI metrics, queue pressure notes, and the resilience policy code paths.
- Expected recovery artifact: `build/day2/golden_thread_day2.json`
- Time box: 20 minutes

## Day X File Manifest

Do not edit code in this module folder.

- Diagnostic Notebook: `notebooks/day_2_requirements_architecture.py`
- Primary Day Doc: `docs/DAY_02.md`
- Rosetta Stone Bridge: `notebooks/bridges/day02_resilience_controls.md`
- Production Target: `src/aegisap/observability/retry_policy.py`
- Production Target: `src/aegisap/resilience/backpressure.py`
- Scenario Pack: `scenarios/day02`
- Verification Command: `uv run python -m pytest tests/day2/test_resilience_controls.py tests/day8/test_retry_policy.py -q`
- Verification Command: `uv run aegisap-lab artifact rebuild --day 02`

## Automated Drill

- List drills: `uv run aegisap-lab drill list --day 02`
- Inject default drill: `uv run aegisap-lab drill inject --day 02`
- Reset active drill: `uv run aegisap-lab drill reset --day 02`
- Constraint lineage artifact after mastery: `build/day2/constraint_lineage.json`
