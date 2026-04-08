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

## KQL Evidence

Save `build/day8/kql_evidence.json` before you patch production code. Capture at least one literal Log Analytics query with workspace, expected signal, observed excerpt, and operator interpretation. The facilitator or CAB reviewer may replay one saved query live.

## Chaos Gate

- Failure signal: Role assignments or service posture drifted, and the runtime principal can mutate resources it should only read.
- Diagnostic surface: Portal role assignments, Marimo Bicep bridge, and live audit-production probes.
- Expected recovery artifact: `build/day8/deployment_design.json`
- Time box: 30 minutes

## Day X File Manifest

Do not edit code in this module folder.

- Diagnostic Notebook: `notebooks/day_8_cicd_iac_deployment.py`
- Primary Day Doc: `docs/DAY_08.md`
- Rosetta Stone Bridge: `notebooks/bridges/day08_identity_iac.md`
- Production Target: `infra/modules/role_assignments.bicep`
- Production Target: `infra/foundations/search_service.bicep`
- Production Target: `infra/modules/container_app.bicep`
- Scenario Pack: `scenarios/day08`
- Verification Command: `uv run python -m pytest tests/day7/security/test_search_token_auth_only.py tests/day8/test_security_and_context.py tests/day8/test_observability_contract.py -q`
- Verification Command: `uv run aegisap-lab artifact rebuild --day 08`

## Automated Drill

- List drills: `uv run aegisap-lab drill list --day 08`
- Inject default drill: `uv run aegisap-lab drill inject --day 08`
- Reset active drill: `uv run aegisap-lab drill reset --day 08`
- Constraint lineage artifact after mastery: `build/day8/constraint_lineage.json`
