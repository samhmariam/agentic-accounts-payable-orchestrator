# Day 12 - Private Networking, Egress Control, and Security Dependency Management

Primary learner entrypoint: `modules/day_12_private_networking/README.md`.

## Why This Matters to an FDE

Private networking is a hard customer boundary, not an optimization. Financial customers will fail your deployment instantly if you cannot prove traffic never falls back to the public internet.

## Customer Context

The customer CISO escalated a DNS drift concern. You must prove that the VNet, private endpoints, and DNS links keep the agent invisible to the public internet.

## Cost of Failure

If public access returns, regulated data escapes the private boundary and security approval is revoked immediately.

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

## Incident Entry

```bash
uv run aegisap-lab incident start --day 12
```

## Mastery Gate

- `uv run python -m pytest tests/day12/test_network_posture.py tests/day12/test_bicep_policy_checker.py -q && uv run aegisap-lab artifact rebuild --day 12`
- `uv run aegisap-lab audit-production --day 12 --strict`

## Native Tooling Gate

- Policy source: `docs/curriculum/NATIVE_TOOLING_POLICY.md`
- Save native proof to `build/day12/native_operator_evidence.json`
- Allowed: Azure Portal, `az`, `az rest`, raw KQL, `git`, `curl`, `nslookup` or `Resolve-DnsName`
- Tools banned during this gate: `aegisap-lab`, helper verification wrappers, and canned answer keys
- Until both raw evidence files are complete, wrappers stay banned. After that, wrappers are allowed only for artifact rebuild, mastery, or reset flows.
- Day 12 evidence must include at least two literal native commands plus one raw KQL query.
- Day 12 does not pass until the facilitator makes the learner rerun one saved proof live

## KQL Evidence

Save `build/day12/kql_evidence.json` before you patch production code. Capture at least one literal Log Analytics query with workspace, expected signal, observed excerpt, and operator interpretation. The facilitator or CAB reviewer may replay one saved query live.

## Verification Commands

```bash
uv run python -m pytest tests/day12/test_network_posture.py tests/day12/test_bicep_policy_checker.py -q
uv run aegisap-lab artifact rebuild --day 12
```

## Key Files

- `modules/day_12_private_networking/README.md`
- `notebooks/day_12_private_networking_constraints.py`
- `notebooks/bridges/day12_private_networking.md`
- `src/aegisap/network/bicep_policy_checker.py`
- `src/aegisap/network/private_endpoint_probe.py`
- `scripts/check_private_network_static.py`
- `scripts/verify_private_network_posture.py`
- `build/day12/native_operator_evidence.json`
- `scenarios/day12`

## CAPSTONE_B

This day still feeds the transfer track and must preserve the inherited customer constraints while the second domain comes online.

## Automated Drill

- `uv run aegisap-lab drill list --day 12`
- `uv run aegisap-lab drill inject --day 12`
- `uv run aegisap-lab drill reset --day 12`
- `uv run aegisap-lab mastery --day 12` writes `build/day12/constraint_lineage.json` so later reviews can see the inherited rules this day still carries.
