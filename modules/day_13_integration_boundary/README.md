# Day 13 Module Wormhole

## Why This Matters to an FDE

Integration boundaries fail at the seams between teams. Elite FDEs have to preserve contracts, drain DLQs, and expose compensating actions before a partner outage becomes your outage.

## Customer Context

A line-of-business integration is dropping events at the boundary. The customer expects the MCP surface and DLQ path to recover without breaking inherited identity or network controls.

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

## FDE Implementation Cycle

- Customer Reality: inspect the live incident and portal surface before you theorize.
- Diagnostic Bridge: prove the state in Marimo and name the API or SDK call that matches the portal behavior.
- Production Engineering: patch the durable code in the repo, not inside the notebook.
- Chaos Gate: recover under the time box and defend the trade-off in review language.

## Mastery Gate

- `uv run python -m pytest tests/day13/test_dlq_consumer.py tests/day13/test_mcp_server.py tests/day13/test_payment_hold.py -q && uv run aegisap-lab artifact rebuild --day 13`
- `uv run aegisap-lab audit-production --day 13 --strict`

## Chaos Gate

- Failure signal: Boundary drift leaves partner traffic in the DLQ or exposes an incomplete MCP contract to the client.
- Diagnostic surface: MCP client notebook flow, DLQ evidence, compensating-action code, and cloud-truth posture checks.
- Expected recovery artifact: `build/day13/mcp_contract_report.json`
- Time box: 30 minutes

## Day X File Manifest

Do not edit code in this module folder.

- Diagnostic Notebook: `notebooks/day_13_integration_boundary_and_mcp.py`
- Primary Day Doc: `docs/DAY_13.md`
- Rosetta Stone Bridge: `notebooks/bridges/day13_integration_boundary.md`
- Production Target: `src/aegisap/mcp/server.py`
- Production Target: `src/aegisap/mcp/schemas.py`
- Production Target: `src/aegisap/integration/dlq_consumer.py`
- Production Target: `src/aegisap/integration/compensating_action.py`
- Scenario Pack: `scenarios/day13`
- Verification Command: `uv run python -m pytest tests/day13/test_dlq_consumer.py tests/day13/test_mcp_server.py tests/day13/test_payment_hold.py -q`
- Verification Command: `uv run aegisap-lab artifact rebuild --day 13`
