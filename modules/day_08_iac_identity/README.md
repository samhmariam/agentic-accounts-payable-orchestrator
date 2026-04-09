# Day 8 Module Wormhole

## Why This Matters to an FDE

IaC and identity are where customer trust is won or lost. If you cannot map a portal permission to the exact Bicep resource that fixes it, you are still doing ClickOps.

## Customer Context

A rogue admin changed runtime permissions and the customer now suspects the search tier is over-privileged. You must restore least privilege without violating the no-public-endpoints rule inherited from Day 4.

## Cost of Failure

If runtime identity stays over-privileged, a single deployment drift can become cross-service data access and immediate CAB rejection.

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

## FDE Implementation Cycle

- Customer Reality: inspect the live incident and portal surface before you theorize.
- Diagnostic Bridge: prove the state in Marimo and name the API or SDK call that matches the portal behavior.
- Production Engineering: patch the durable code in the repo, not inside the notebook.
- Chaos Gate: recover under the time box and defend the trade-off in review language.

## Mastery Gate

- `uv run python -m pytest tests/day7/security/test_search_token_auth_only.py tests/day8/test_security_and_context.py tests/day8/test_observability_contract.py -q && uv run aegisap-lab artifact rebuild --day 08`
- `uv run aegisap-lab audit-production --day 08 --strict`

## Native Tooling Gate

- Policy source: `docs/curriculum/NATIVE_TOOLING_POLICY.md`
- Save raw proof to `build/day8/native_operator_evidence.json` before you patch production code.
- Allowed: Azure Portal, `az`, `az rest`, raw KQL, `git`, `curl`, `nslookup` or `Resolve-DnsName`
- Tools banned during this gate: `aegisap-lab`, helper verification wrappers, and canned answer keys
- Until both raw evidence files are complete, wrappers stay banned. After that, wrappers are allowed only for artifact rebuild, mastery, or reset flows.

- Save `build/day8/diagnostic_timeline.md` while you investigate so the scoring panel can verify the first symptom, first telemetry proof, subsystem narrowed, durable repair, and post-fix confirmation.

## KQL Evidence

Save `build/day8/kql_evidence.json` before you patch production code. Capture at least one literal Log Analytics query before the repo patch with capture order, `captured_before_patch=true`, workspace, `first_signal_or_followup`, correlation or trace reference when available, observed excerpt, and operator interpretation. The facilitator or CAB reviewer may replay one saved query live.

## Chaos Gate

- Failure signal: Role assignments or service posture drifted, and the runtime principal can mutate resources it should only read.
- Starting signal: A deployment-state break-glass recovery is blocked and the runtime identity still looks over-privileged.
- Expected recovery artifact: `build/day8/deployment_design.json`
- Time box: 30 minutes

## Day X File Manifest

Do not edit code in this module folder.

- Diagnostic Notebook: `notebooks/day_8_cicd_iac_deployment.py`
- Primary Day Doc: `docs/DAY_08.md`
- Rosetta Stone Bridge: `notebooks/bridges/day08_identity_iac.md`
- Repair Domain: `Role Assignments`
- Repair Domain: `Search Service`
- Repair Domain: `Container App`
- Incident Asset Ref: `incident.day08`
- Verification Command: `uv run python -m pytest tests/day7/security/test_search_token_auth_only.py tests/day8/test_security_and_context.py tests/day8/test_observability_contract.py -q`
- Verification Command: `uv run aegisap-lab artifact rebuild --day 08`
- Native Evidence Artifact: `build/day8/native_operator_evidence.json`
- KQL Evidence Artifact: `build/day8/kql_evidence.json`
- Diagnostic Timeline: `build/day8/diagnostic_timeline.md`

## Automated Drill

- List drills: `uv run aegisap-lab drill list --day 08`
- Inject default drill: `uv run aegisap-lab drill inject --day 08`
- Reset active drill: `uv run aegisap-lab drill reset --day 08`
- Constraint lineage artifact after mastery: `build/day8/constraint_lineage.json`
