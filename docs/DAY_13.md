# Day 13 - Integration Boundaries, Async Reliability, and Contract Management

Primary learner entrypoint: `modules/day_13_integration_boundary/README.md`.

## Why This Matters to an FDE

Integration boundaries fail at the seams between teams. Elite FDEs have to preserve contracts, drain DLQs, and expose compensating actions before a partner outage becomes your outage.

## Customer Context

A line-of-business integration is dropping events at the boundary. The customer expects the MCP surface and DLQ path to recover without breaking inherited identity or network controls.

## Cost of Failure

If the integration contract drifts, partner systems fail unpredictably and compensating-action load spikes across the boundary.

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

## Incident Entry

```bash
uv run aegisap-lab incident start --day 13
```

## Mastery Gate

- `uv run python -m pytest tests/day13/test_dlq_consumer.py tests/day13/test_mcp_server.py tests/day13/test_payment_hold.py -q && uv run aegisap-lab artifact rebuild --day 13`
- `uv run aegisap-lab audit-production --day 13 --strict`

## KQL Evidence

Save `build/day13/kql_evidence.json` before you patch production code. Capture at least one literal Log Analytics query with workspace, expected signal, observed excerpt, and operator interpretation. The facilitator or CAB reviewer may replay one saved query live.

## Verification Commands

```bash
uv run python -m pytest tests/day13/test_dlq_consumer.py tests/day13/test_mcp_server.py tests/day13/test_payment_hold.py -q
uv run aegisap-lab artifact rebuild --day 13
```

## Key Files

- `modules/day_13_integration_boundary/README.md`
- `notebooks/day_13_integration_boundary_and_mcp.py`
- `notebooks/bridges/day13_integration_boundary.md`
- `src/aegisap/mcp/server.py`
- `src/aegisap/mcp/schemas.py`
- `src/aegisap/integration/dlq_consumer.py`
- `src/aegisap/integration/compensating_action.py`
- `scenarios/day13`

## CAPSTONE_B

This day still feeds the transfer track and must preserve the inherited customer constraints while the second domain comes online.

## Automated Drill

- `uv run aegisap-lab drill list --day 13`
- `uv run aegisap-lab drill inject --day 13`
- `uv run aegisap-lab drill reset --day 13`
- `uv run aegisap-lab mastery --day 13` writes `build/day13/constraint_lineage.json` so later reviews can see the inherited rules this day still carries.
