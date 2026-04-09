# Day 14 Module Wormhole

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

## FDE Implementation Cycle

- Customer Reality: inspect the live incident and portal surface before you theorize.
- Diagnostic Bridge: prove the state in Marimo and name the API or SDK call that matches the portal behavior.
- Production Engineering: patch the durable code in the repo, not inside the notebook.
- Chaos Gate: recover under the time box and defend the trade-off in review language.

## Mastery Gate

- `uv run python -m pytest tests/day14/test_breaking_changes.py -q && uv run python scripts/run_chaos_capstone.py && uv run aegisap-lab artifact rebuild --day 14`
- `uv run aegisap-lab audit-production --day 14 --strict`

## Native Tooling Gate

- Policy source: `docs/curriculum/NATIVE_TOOLING_POLICY.md`
- Save native proof to `build/day14/native_operator_evidence.json`
- Allowed: Azure Portal, `az`, `az rest`, raw KQL, `git`, `curl`, `nslookup` or `Resolve-DnsName`
- Tools banned during this gate: `aegisap-lab`, helper verification wrappers, and canned answer keys
- Until both raw evidence files are complete, wrappers stay banned. After that, wrappers are allowed only for artifact rebuild, mastery, or reset flows.
- Day 14 evidence must include at least two literal native commands plus one raw KQL query.
- The capstone CAB chair may randomly select one saved proof and require a live rerun
- Peer checklist file: `docs/curriculum/checklists/day14_peer_red_team.md`
- Revert Proof: `docs/curriculum/artifacts/day14/REVERT_PROOF.md`

- Save `build/day14/diagnostic_timeline.md` while you investigate so the scoring panel can verify the first symptom, first telemetry proof, subsystem narrowed, durable repair, and post-fix confirmation.

## KQL Evidence

Save `build/day14/kql_evidence.json` before you patch production code. Capture at least one literal Log Analytics query before the repo patch with capture order, `captured_before_patch=true`, workspace, `first_signal_or_followup`, correlation or trace reference when available, observed excerpt, and operator interpretation. The facilitator or CAB reviewer may replay one saved query live.

## Chaos Gate

- Failure signal: A breaking change brings down the orchestration path and the team must restore service without losing correlation or rollback readiness.
- Starting signal: Customers report that nothing is processing; clear the network fault first, then the identity fault, then the canary and correlation fault.
- Expected recovery artifact: `build/day14/cto_trace_report.json`
- Time box: 35 minutes

## Day X File Manifest

Do not edit code in this module folder.

- Diagnostic Notebook: `notebooks/day_14_breaking_changes_elite_ops.py`
- Primary Day Doc: `docs/DAY_14.md`
- Rosetta Stone Bridge: `notebooks/bridges/day14_elite_operations.md`
- Repair Domain: `Gates V2`
- Repair Domain: `Correlation`
- Repair Domain: `Verify Trace Correlation`
- Repair Domain: `Run Chaos Capstone`
- Incident Asset Ref: `incident.day14`
- Verification Command: `uv run python -m pytest tests/day14/test_breaking_changes.py -q`
- Verification Command: `uv run python scripts/run_chaos_capstone.py`
- Verification Command: `uv run aegisap-lab artifact rebuild --day 14`
- Native Evidence Artifact: `build/day14/native_operator_evidence.json`
- KQL Evidence Artifact: `build/day14/kql_evidence.json`
- Diagnostic Timeline: `build/day14/diagnostic_timeline.md`

## Automated Drill

- List drills: `uv run aegisap-lab drill list --day 14`
- Inject default drill: `uv run aegisap-lab drill inject --day 14`
- Reset active drill: `uv run aegisap-lab drill reset --day 14`
- Constraint lineage artifact after mastery: `build/day14/constraint_lineage.json`
