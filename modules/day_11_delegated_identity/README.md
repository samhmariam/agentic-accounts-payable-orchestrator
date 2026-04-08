# Day 11 Module Wormhole

## Why This Matters to an FDE

Delegated identity failures create real authorization and audit gaps. FDEs need to prove who acted, who approved, and how impersonation stayed inside the customer authority model.

## Customer Context

The security team caught an approval path that may be acting as the app instead of the user. You must repair the actor binding without regressing release or network controls.

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

## Chaos Gate

- Failure signal: The OBO path loses actor fidelity, making approvals or downstream actions look like app-only activity.
- Diagnostic surface: Entra or app registration evidence, OBO notebook proof, actor verifier code, and cloud-truth posture checks.
- Expected recovery artifact: `build/day11/obo_contract.json`
- Time box: 30 minutes

## Day X File Manifest

Do not edit code in this module folder.

- Diagnostic Notebook: `notebooks/day_11_delegated_identity_obo.py`
- Primary Day Doc: `docs/DAY_11.md`
- Rosetta Stone Bridge: `notebooks/bridges/day11_delegated_identity.md`
- Production Target: `src/aegisap/identity/actor_verifier.py`
- Production Target: `src/aegisap/identity/obo.py`
- Production Target: `scripts/verify_delegated_identity_contract.py`
- Scenario Pack: `scenarios/day11`
- Verification Command: `uv run python -m pytest tests/day11/test_actor_verification.py tests/day11/test_obo_flow.py tests/day11/test_obo_simulation.py -q`
- Verification Command: `uv run aegisap-lab artifact rebuild --day 11`
