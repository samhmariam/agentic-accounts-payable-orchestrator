# Day 14 Module Wormhole

## Why This Matters to an FDE

Elite operations is executive engineering under pressure. FDEs must manage breaking changes with rollback proof, telemetry, and customer-safe trade-offs while the incident clock is running.

## Customer Context

A downstream SAP schema change created a severity-1 incident. Leadership needs a rollback-capable repair path that preserves traceability, network posture, and release evidence.

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

## FDE Implementation Cycle

- Customer Reality: inspect the live incident and portal surface before you theorize.
- Diagnostic Bridge: prove the state in Marimo and name the API or SDK call that matches the portal behavior.
- Production Engineering: patch the durable code in the repo, not inside the notebook.
- Chaos Gate: recover under the time box and defend the trade-off in review language.

## Mastery Gate

- `uv run python -m pytest tests/day14/test_breaking_changes.py -q && uv run python scripts/run_chaos_capstone.py && uv run aegisap-lab artifact rebuild --day 14`
- `uv run aegisap-lab audit-production --day 14 --strict`

## Chaos Gate

- Failure signal: A breaking change brings down the orchestration path and the team must restore service without losing correlation or rollback readiness.
- Diagnostic surface: Chaos drill evidence, trace correlation artifacts, rollback gates, and cloud-truth posture checks.
- Expected recovery artifact: `build/day14/cto_trace_report.json`
- Time box: 35 minutes

## Day X File Manifest

Do not edit code in this module folder.

- Diagnostic Notebook: `notebooks/day_14_breaking_changes_elite_ops.py`
- Primary Day Doc: `docs/DAY_14.md`
- Rosetta Stone Bridge: `notebooks/bridges/day14_elite_operations.md`
- Production Target: `src/aegisap/deploy/gates_v2.py`
- Production Target: `src/aegisap/traceability/correlation.py`
- Production Target: `scripts/verify_trace_correlation.py`
- Production Target: `scripts/run_chaos_capstone.py`
- Scenario Pack: `scenarios/day14`
- Verification Command: `uv run python -m pytest tests/day14/test_breaking_changes.py -q`
- Verification Command: `uv run python scripts/run_chaos_capstone.py`
- Verification Command: `uv run aegisap-lab artifact rebuild --day 14`
