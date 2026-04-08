# Day 12 Module Wormhole

## Why This Matters to an FDE

Private networking is a hard customer boundary, not an optimization. Financial customers will fail your deployment instantly if you cannot prove traffic never falls back to the public internet.

## Customer Context

The customer CISO escalated a DNS drift concern. You must prove that the VNet, private endpoints, and DNS links keep the agent invisible to the public internet.

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

## FDE Implementation Cycle

- Customer Reality: inspect the live incident and portal surface before you theorize.
- Diagnostic Bridge: prove the state in Marimo and name the API or SDK call that matches the portal behavior.
- Production Engineering: patch the durable code in the repo, not inside the notebook.
- Chaos Gate: recover under the time box and defend the trade-off in review language.

## Mastery Gate

- `uv run python -m pytest tests/day12/test_network_posture.py tests/day12/test_bicep_policy_checker.py -q && uv run aegisap-lab artifact rebuild --day 12`
- `uv run aegisap-lab audit-production --day 12 --strict`

## Native Tooling Gate

- Save native proof to `build/day12/native_operator_evidence.json`
- Allowed: Azure Portal, `az`, `az rest`, raw KQL, `git`, `curl`, `nslookup` or `Resolve-DnsName`
- Tools banned during this gate: `aegisap-lab`, helper verification wrappers, and canned answer keys
- Day 12 does not pass until the facilitator makes the learner rerun one saved proof live

## Chaos Gate

- Failure signal: Private endpoint DNS or routing drift makes a production-bound service resolve publicly or appear publicly reachable.
- Diagnostic surface: Network Watcher evidence, private endpoint probe cells, and live audit-production DNS posture checks.
- Expected recovery artifact: `build/day12/private_network_posture.json`
- Time box: 30 minutes

## Day X File Manifest

Do not edit code in this module folder.

- Diagnostic Notebook: `notebooks/day_12_private_networking_constraints.py`
- Primary Day Doc: `docs/DAY_12.md`
- Rosetta Stone Bridge: `notebooks/bridges/day12_private_networking.md`
- Production Target: `src/aegisap/network/bicep_policy_checker.py`
- Production Target: `src/aegisap/network/private_endpoint_probe.py`
- Production Target: `scripts/check_private_network_static.py`
- Production Target: `scripts/verify_private_network_posture.py`
- Scenario Pack: `scenarios/day12`
- Verification Command: `uv run python -m pytest tests/day12/test_network_posture.py tests/day12/test_bicep_policy_checker.py -q`
- Verification Command: `uv run aegisap-lab artifact rebuild --day 12`
- Native Evidence Artifact: `build/day12/native_operator_evidence.json`

## Automated Drill

- List drills: `uv run aegisap-lab drill list --day 12`
- Inject default drill: `uv run aegisap-lab drill inject --day 12`
- Reset active drill: `uv run aegisap-lab drill reset --day 12`
- Constraint lineage artifact after mastery: `build/day12/constraint_lineage.json`
