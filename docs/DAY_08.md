# Day 8 - IaC, Identity Planes, and Secure Release Ownership

Primary learner entrypoint: `modules/day_08_iac_identity/README.md`.

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

## Incident Entry

```bash
uv run aegisap-lab incident start --day 08
```

## Mastery Gate

- `uv run python -m pytest tests/day7/security/test_search_token_auth_only.py tests/day8/test_security_and_context.py tests/day8/test_observability_contract.py -q && uv run aegisap-lab artifact rebuild --day 08`
- `uv run aegisap-lab audit-production --day 08 --strict`

## Native Tooling Gate

- Policy source: `docs/curriculum/NATIVE_TOOLING_POLICY.md`
- Save raw proof to `build/day8/native_operator_evidence.json` before you patch production code.
- Allowed: Azure Portal, `az`, `az rest`, raw KQL, `git`, `curl`, `nslookup` or `Resolve-DnsName`
- Tools banned during this gate: `aegisap-lab`, helper verification wrappers, and canned answer keys
- Until both raw evidence files are complete, wrappers stay banned. After that, wrappers are allowed only for artifact rebuild, mastery, or reset flows.

## KQL Evidence

Save `build/day8/kql_evidence.json` before you patch production code. Capture at least one literal Log Analytics query with workspace, expected signal, observed excerpt, and operator interpretation. The facilitator or CAB reviewer may replay one saved query live.

## Verification Commands

```bash
uv run python -m pytest tests/day7/security/test_search_token_auth_only.py tests/day8/test_security_and_context.py tests/day8/test_observability_contract.py -q
uv run aegisap-lab artifact rebuild --day 08
```

## Key Files

- `modules/day_08_iac_identity/README.md`
- `notebooks/day_8_cicd_iac_deployment.py`
- `notebooks/bridges/day08_identity_iac.md`
- `infra/modules/role_assignments.bicep`
- `infra/foundations/search_service.bicep`
- `infra/modules/container_app.bicep`
- `scenarios/day08`

## Automated Drill

- `uv run aegisap-lab drill list --day 08`
- `uv run aegisap-lab drill inject --day 08`
- `uv run aegisap-lab drill reset --day 08`
- `uv run aegisap-lab mastery --day 08` writes `build/day8/constraint_lineage.json` so later reviews can see the inherited rules this day still carries.
