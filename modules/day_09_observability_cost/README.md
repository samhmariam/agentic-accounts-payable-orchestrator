# Day 9 Module Wormhole

## Why This Matters to an FDE

Production economics are part of the design, not a dashboard afterthought. FDEs have to trace runaway cost back to routing and stop it before the customer stops the project.

## Customer Context

A finance sponsor is alarmed by rising token spend and wants a defensible routing and cache policy that respects the same infrastructure and identity constraints already in force.

## Persistent Constraints

- `regulated_invoice_auditability`: Every financial decision path must leave auditable evidence that survives hostile review.
- `latency_budget_guardrails`: Queue, retry, and latency controls must be explicit enough to defend under customer SLA pressure.
- `authoritative_retrieval_sources`: Retrieval must prefer authoritative source systems over stale or ambiguous evidence.
- `no_public_endpoints`: Production-bound AI and data services must not expose public network access.
- `fail_closed_decisions`: Risky automation paths must fail closed and require explicit human review.
- `durable_resume_idempotency`: Durable state recovery must resume safely without duplicating side effects.
- `conflicting_authority_refusal`: Conflicting records or review evidence must trigger refusal rather than silent blending.
- `pii_redaction_before_audit`: Sensitive content must be redacted before logging, audit writes, or downstream release evidence.
- `search_token_auth_only`: Search runtime access must rely on token auth and disable local keys.
- `keyless_runtime_identity`: Runtime identity should prefer managed identity or delegated flows over embedded credentials.
- `cost_ceiling_enforced`: Economic controls must prevent runaway routing, caching, or model-selection cost drift.

## FDE Implementation Cycle

- Customer Reality: inspect the live incident and portal surface before you theorize.
- Diagnostic Bridge: prove the state in Marimo and name the API or SDK call that matches the portal behavior.
- Production Engineering: patch the durable code in the repo, not inside the notebook.
- Chaos Gate: recover under the time box and defend the trade-off in review language.

## Mastery Gate

- `uv run python -m pytest tests/day9/test_routing_policy.py tests/day9/test_cache_and_cost.py tests/day9/test_runtime_day9_contract.py -q && uv run aegisap-lab artifact rebuild --day 09`
- `uv run aegisap-lab audit-production --day 09 --strict`

## Chaos Gate

- Failure signal: Routing or caching pushes the workload outside the cost ceiling while inherited infrastructure posture still has to hold.
- Diagnostic surface: Azure Monitor or KQL evidence, routing notebook analysis, budget gates, and cloud-truth posture checks.
- Expected recovery artifact: `build/day9/routing_report.json`
- Time box: 25 minutes

## Day X File Manifest

Do not edit code in this module folder.

- Diagnostic Notebook: `notebooks/day_9_scaling_monitoring_cost.py`
- Primary Day Doc: `docs/DAY_09.md`
- Rosetta Stone Bridge: `notebooks/bridges/day09_routing_cost.md`
- Production Target: `src/aegisap/routing/routing_policy.py`
- Production Target: `src/aegisap/cache/cache_policy.py`
- Production Target: `src/aegisap/cost/budget_gate.py`
- Scenario Pack: `scenarios/day09`
- Verification Command: `uv run python -m pytest tests/day9/test_routing_policy.py tests/day9/test_cache_and_cost.py tests/day9/test_runtime_day9_contract.py -q`
- Verification Command: `uv run aegisap-lab artifact rebuild --day 09`

## Automated Drill

- List drills: `uv run aegisap-lab drill list --day 09`
- Inject default drill: `uv run aegisap-lab drill inject --day 09`
- Reset active drill: `uv run aegisap-lab drill reset --day 09`
- Constraint lineage artifact after mastery: `build/day9/constraint_lineage.json`
