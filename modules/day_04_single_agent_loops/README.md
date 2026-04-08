# Day 4 Module Wormhole

## Why This Matters to an FDE

Single-agent loops only become production-safe when policy can override model enthusiasm. FDEs get paid to keep irreversible actions inside a fail-closed boundary.

## Customer Context

The customer CISO banned public exposure for production-bound AI services and wants proof that risky recommendation paths still stop for review instead of acting optimistically.

## Persistent Constraints

- `regulated_invoice_auditability`: Every financial decision path must leave auditable evidence that survives hostile review.
- `latency_budget_guardrails`: Queue, retry, and latency controls must be explicit enough to defend under customer SLA pressure.
- `authoritative_retrieval_sources`: Retrieval must prefer authoritative source systems over stale or ambiguous evidence.
- `no_public_endpoints`: Production-bound AI and data services must not expose public network access.
- `fail_closed_decisions`: Risky automation paths must fail closed and require explicit human review.

## FDE Implementation Cycle

- Customer Reality: inspect the live incident and portal surface before you theorize.
- Diagnostic Bridge: prove the state in Marimo and name the API or SDK call that matches the portal behavior.
- Production Engineering: patch the durable code in the repo, not inside the notebook.
- Chaos Gate: recover under the time box and defend the trade-off in review language.

## Mastery Gate

- `uv run python -m pytest tests/day4/unit/planning/test_policy_overlay.py tests/day4/unit/recommendation/test_recommendation_gate.py -q && uv run aegisap-lab artifact rebuild --day 04`
- `uv run aegisap-lab audit-production --day 04 --strict`

## Chaos Gate

- Failure signal: Execution traces show a risky recommendation escaping the policy overlay while public exposure constraints stay in force.
- Diagnostic surface: Execution traces, policy overlay cells, and live cloud posture for AI and data endpoints.
- Expected recovery artifact: `build/day4/golden_thread_day4.json`
- Time box: 25 minutes

## Day X File Manifest

Do not edit code in this module folder.

- Diagnostic Notebook: `notebooks/day_4_single_agent_loops.py`
- Primary Day Doc: `docs/DAY_04.md`
- Rosetta Stone Bridge: `notebooks/bridges/day04_fail_closed_planning.md`
- Production Target: `src/aegisap/day4/planning/policy_overlay.py`
- Production Target: `src/aegisap/day4/recommendation/recommendation_gate.py`
- Scenario Pack: `scenarios/day04`
- Verification Command: `uv run python -m pytest tests/day4/unit/planning/test_policy_overlay.py tests/day4/unit/recommendation/test_recommendation_gate.py -q`
- Verification Command: `uv run aegisap-lab artifact rebuild --day 04`
