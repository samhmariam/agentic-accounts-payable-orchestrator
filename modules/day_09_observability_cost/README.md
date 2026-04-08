# Day 9 Module Wormhole

## Why This Matters to an FDE

Production economics are part of the design, not a dashboard afterthought. FDEs have to trace runaway cost back to routing and stop it before the customer stops the project.

## Customer Context

A finance sponsor is alarmed by rising token spend and wants a defensible routing and cache policy that respects the same infrastructure and identity constraints already in force.

## Cost of Failure

If routing and cost telemetry drift silently, runaway spend and untraceable failures can continue until finance or operations halts rollout.

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

## Native Tooling Gate

- Policy source: `docs/curriculum/NATIVE_TOOLING_POLICY.md`
- Save native proof to `build/day9/native_operator_evidence.json`
- Allowed: Azure Portal, `az`, `az rest`, raw KQL, `git`, `curl`, `nslookup` or `Resolve-DnsName`
- Tools banned during this gate: `aegisap-lab`, helper verification wrappers, and canned step-by-step answer keys
- Day 9 native evidence is blocking and must include at least two literal native commands plus one raw KQL query
- Until both raw evidence files are complete, wrappers stay banned. After that, wrappers are allowed only for artifact rebuild, mastery, or reset flows.
- The Day 10 CAB board may replay one saved Day 9 proof live

## KQL Evidence

Save `build/day9/kql_evidence.json` before you patch production code. Capture at least one literal Log Analytics query with workspace, expected signal, observed excerpt, and operator interpretation. The facilitator or CAB reviewer may replay one saved query live.

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
- Native Evidence Artifact: `build/day9/native_operator_evidence.json`

## Automated Drill

- List drills: `uv run aegisap-lab drill list --day 09`
- Inject default drill: `uv run aegisap-lab drill inject --day 09`
- Reset active drill: `uv run aegisap-lab drill reset --day 09`
- Constraint lineage artifact after mastery: `build/day9/constraint_lineage.json`
