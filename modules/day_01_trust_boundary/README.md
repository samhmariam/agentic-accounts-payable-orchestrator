# Day 1 Module Wormhole

## Why This Matters to an FDE

Trust-boundary failures are customer-facing finance incidents. An FDE has to prove whether the system is lying, parsing badly, or violating the review contract before anyone retries money movement.

## Customer Context

A finance operations lead is blocking go-live after a valid European supplier invoice was rejected. They want proof that the deterministic trust boundary can be repaired without widening the blast radius.

## Cost of Failure

Every hour this locale parsing failure survives, valid supplier invoices remain unpaid and finance risks breach-of-contract escalation.

## Persistent Constraints

- `regulated_invoice_auditability`: Every financial decision path must leave auditable evidence that survives hostile review.

## FDE Implementation Cycle

- Customer Reality: inspect the live incident and portal surface before you theorize.
- Diagnostic Bridge: prove the state in Marimo and name the API or SDK call that matches the portal behavior.
- Production Engineering: patch the durable code in the repo, not inside the notebook.
- Chaos Gate: recover under the time box and defend the trade-off in review language.

## Mastery Gate

- `uv run python -m pytest tests/test_day_01_money.py tests/test_day_01_fixtures.py -q && uv run aegisap-lab artifact rebuild --day 01`

## Chaos Gate

- Failure signal: A locale-formatted invoice amount is rejected even though the extraction payload and endpoint health are clean.
- Diagnostic surface: Foundry extraction payload, notebook fixture replay, and trust-boundary parser behavior.
- Expected recovery artifact: `build/day1/golden_thread_day1.json`
- Time box: 20 minutes

## Day X File Manifest

Do not edit code in this module folder.

- Diagnostic Notebook: `notebooks/day_1_agentic_fundamentals.py`
- Primary Day Doc: `docs/DAY_01.md`
- Rosetta Stone Bridge: `notebooks/bridges/day01_trust_boundary.md`
- Production Target: `src/aegisap/day_01/normalizers.py`
- Production Target: `src/aegisap/day_01/service.py`
- Scenario Pack: `scenarios/day01`
- Verification Command: `uv run python -m pytest tests/test_day_01_money.py tests/test_day_01_fixtures.py -q`
- Verification Command: `uv run aegisap-lab artifact rebuild --day 01`

## Automated Drill

- List drills: `uv run aegisap-lab drill list --day 01`
- Inject default drill: `uv run aegisap-lab drill inject --day 01`
- Reset active drill: `uv run aegisap-lab drill reset --day 01`
- Constraint lineage artifact after mastery: `build/day1/constraint_lineage.json`
