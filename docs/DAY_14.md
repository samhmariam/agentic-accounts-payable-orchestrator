# Day 14 - Elite Operations, Breaking Changes, and Executive Incident Leadership

Primary learner entrypoint: `modules/day_14_elite_ops/README.md`.

## Why This Matters to an FDE

Elite operations is executive engineering under pressure. FDEs must manage breaking changes with rollback proof, telemetry, and customer-safe trade-offs while the incident clock is running.

## Customer Context

A downstream SAP schema change created a severity-1 incident. Leadership needs a rollback-capable repair path that preserves traceability, network posture, and release evidence.

## Cost of Failure

If elite-ops gates stay false-green during an incident, executives lose trustworthy go/no-go evidence exactly when recovery decisions matter most.

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
- `release_packet_before_prod`: Production acceptance requires a release packet, explicit ownership, and rollback-ready evidence.
- `actor_bound_approvals`: Approval and impersonation flows must remain bound to the real human actor.
- `private_dns_resolution`: Private endpoints must resolve privately and block public fallback through DNS and routing.
- `integration_contract_compensations`: External contracts require DLQ handling and compensating actions rather than silent drops.
- `rollback_traceability`: Breaking-change response must preserve rollback readiness and end-to-end trace correlation.

## Incident Entry

```bash
uv run aegisap-lab incident start --day 14
```

## Mastery Gate

- `uv run python -m pytest tests/day14/test_breaking_changes.py -q && uv run python scripts/run_chaos_capstone.py && uv run aegisap-lab artifact rebuild --day 14`
- `uv run aegisap-lab audit-production --day 14 --strict`

## Native Tooling Gate

- Save native proof to `build/day14/native_operator_evidence.json`
- Allowed: Azure Portal, `az`, `az rest`, raw KQL, `git`, `curl`, `nslookup` or `Resolve-DnsName`
- Tools banned during this gate: `aegisap-lab`, helper verification wrappers, and canned answer keys
- The capstone CAB chair may randomly select one saved proof and require a live rerun
- Peer checklist file: `docs/curriculum/checklists/day14_peer_red_team.md`
- Revert Proof: `docs/curriculum/artifacts/day14/REVERT_PROOF.md`

## KQL Evidence

Save `build/day14/kql_evidence.json` before you patch production code. Capture at least one literal Log Analytics query with workspace, expected signal, observed excerpt, and operator interpretation. The facilitator or CAB reviewer may replay one saved query live.

## Verification Commands

```bash
uv run python -m pytest tests/day14/test_breaking_changes.py -q
uv run python scripts/run_chaos_capstone.py
uv run aegisap-lab artifact rebuild --day 14
```

## Key Files

- `modules/day_14_elite_ops/README.md`
- `notebooks/day_14_breaking_changes_elite_ops.py`
- `notebooks/bridges/day14_elite_operations.md`
- `src/aegisap/deploy/gates_v2.py`
- `src/aegisap/traceability/correlation.py`
- `scripts/verify_trace_correlation.py`
- `scripts/run_chaos_capstone.py`
- `build/day14/native_operator_evidence.json`
- `scenarios/day14`

## CAPSTONE_B

This day still feeds the transfer track and must preserve the inherited customer constraints while the second domain comes online.

## Automated Drill

- `uv run aegisap-lab drill list --day 14`
- `uv run aegisap-lab drill inject --day 14`
- `uv run aegisap-lab drill reset --day 14`
- `uv run aegisap-lab mastery --day 14` writes `build/day14/constraint_lineage.json` so later reviews can see the inherited rules this day still carries.
