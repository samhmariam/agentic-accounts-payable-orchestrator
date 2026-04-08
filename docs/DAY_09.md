# Day 9 - Observability, Routing, Cost, and Economic Control

Primary learner entrypoint: `modules/day_09_observability_cost/README.md`.

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

## Incident Entry

```bash
uv run aegisap-lab incident start --day 09
```

## Mastery Gate

- `uv run python -m pytest tests/day9/test_routing_policy.py tests/day9/test_cache_and_cost.py tests/day9/test_runtime_day9_contract.py -q && uv run aegisap-lab artifact rebuild --day 09`
- `uv run aegisap-lab audit-production --day 09 --strict`

## Native Tooling Gate

- Save native proof to `build/day9/native_operator_evidence.json`
- Allowed: Azure Portal, `az`, `az rest`, raw KQL, `git`, `curl`, `nslookup` or `Resolve-DnsName`
- Tools banned during this gate: `aegisap-lab`, helper verification wrappers, and canned step-by-step answer keys
- Day 9 native evidence is advisory, but it is replayed during the Day 10 CAB review

## Verification Commands

```bash
uv run python -m pytest tests/day9/test_routing_policy.py tests/day9/test_cache_and_cost.py tests/day9/test_runtime_day9_contract.py -q
uv run aegisap-lab artifact rebuild --day 09
```

## Key Files

- `modules/day_09_observability_cost/README.md`
- `notebooks/day_9_scaling_monitoring_cost.py`
- `notebooks/bridges/day09_routing_cost.md`
- `src/aegisap/routing/routing_policy.py`
- `src/aegisap/cache/cache_policy.py`
- `src/aegisap/cost/budget_gate.py`
- `build/day9/native_operator_evidence.json`
- `scenarios/day09`

## Automated Drill

- `uv run aegisap-lab drill list --day 09`
- `uv run aegisap-lab drill inject --day 09`
- `uv run aegisap-lab drill reset --day 09`
- `uv run aegisap-lab mastery --day 09` writes `build/day9/constraint_lineage.json` so later reviews can see the inherited rules this day still carries.
