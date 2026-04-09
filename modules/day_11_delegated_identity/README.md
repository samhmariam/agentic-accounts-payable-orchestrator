# Day 11 Module Wormhole

## Why This Matters to an FDE

Delegated identity failures create real authorization and audit gaps. FDEs need to prove who acted, who approved, and how impersonation stayed inside the customer authority model.

## Customer Context

The security team caught an approval path that may be acting as the app instead of the user. You must repair the actor binding without regressing release or network controls.

## Cost of Failure

If actor binding fails, the system can accept the wrong human as an approver and invalidate the authority model for production changes.

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

## FDE Implementation Cycle

- Customer Reality: inspect the live incident and portal surface before you theorize.
- Diagnostic Bridge: prove the state in Marimo and name the API or SDK call that matches the portal behavior.
- Production Engineering: patch the durable code in the repo, not inside the notebook.
- Chaos Gate: recover under the time box and defend the trade-off in review language.

## Mastery Gate

- `uv run python -m pytest tests/day11/test_actor_verification.py tests/day11/test_obo_flow.py tests/day11/test_obo_simulation.py -q && uv run aegisap-lab artifact rebuild --day 11`
- `uv run aegisap-lab audit-production --day 11 --strict`

## Native Tooling Gate

- Policy source: `docs/curriculum/NATIVE_TOOLING_POLICY.md`
- Save raw proof to `build/day11/native_operator_evidence.json` before you patch production code.
- Allowed: Azure Portal, `az`, `az rest`, raw KQL, `git`, `curl`, `nslookup` or `Resolve-DnsName`
- Tools banned during this gate: `aegisap-lab`, helper verification wrappers, and canned answer keys
- Until both raw evidence files are complete, wrappers stay banned. After that, wrappers are allowed only for artifact rebuild, mastery, or reset flows.
- Day 11 evidence must include at least two literal native commands plus one raw KQL query.

- Save `build/day11/diagnostic_timeline.md` while you investigate so the scoring panel can verify the first symptom, first telemetry proof, subsystem narrowed, durable repair, and post-fix confirmation.

## KQL Evidence

Save `build/day11/kql_evidence.json` before you patch production code. Capture at least one literal Log Analytics query before the repo patch with capture order, `captured_before_patch=true`, workspace, `first_signal_or_followup`, correlation or trace reference when available, observed excerpt, and operator interpretation. The facilitator or CAB reviewer may replay one saved query live.

## Chaos Gate

- Failure signal: The OBO path loses actor fidelity, making approvals or downstream actions look like app-only activity.
- Starting signal: Delegated approval begins failing with actor-binding or OBO symptoms once real identity checks run.
- Expected recovery artifact: `build/day11/obo_contract.json`
- Time box: 30 minutes

## Hostile Identity Review

Run the Day 11 triad before the notebook patch work starts. The learner must
defend actor binding, OBO scope or audience, approval authority, and exception
handling against a hostile identity reviewer.

## Day X File Manifest

Do not edit code in this module folder.

- Diagnostic Notebook: `notebooks/day_11_delegated_identity_obo.py`
- Primary Day Doc: `docs/DAY_11.md`
- Rosetta Stone Bridge: `notebooks/bridges/day11_delegated_identity.md`
- Repair Domain: `Actor Verifier`
- Repair Domain: `Obo`
- Repair Domain: `Verify Delegated Identity Contract`
- Incident Asset Ref: `incident.day11`
- Verification Command: `uv run python -m pytest tests/day11/test_actor_verification.py tests/day11/test_obo_flow.py tests/day11/test_obo_simulation.py -q`
- Verification Command: `uv run aegisap-lab artifact rebuild --day 11`
- Native Evidence Artifact: `build/day11/native_operator_evidence.json`
- KQL Evidence Artifact: `build/day11/kql_evidence.json`
- Diagnostic Timeline: `build/day11/diagnostic_timeline.md`

## Automated Drill

- List drills: `uv run aegisap-lab drill list --day 11`
- Inject default drill: `uv run aegisap-lab drill inject --day 11`
- Reset active drill: `uv run aegisap-lab drill reset --day 11`
- Constraint lineage artifact after mastery: `build/day11/constraint_lineage.json`
