# Day 11 - Delegated Identity, OBO, and Authority Confusion Defense

Primary learner entrypoint: `modules/day_11_delegated_identity/README.md`.

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

## Incident Entry

```bash
uv run aegisap-lab incident start --day 11
```

## Mastery Gate

- `uv run python -m pytest tests/day11/test_actor_verification.py tests/day11/test_obo_flow.py tests/day11/test_obo_simulation.py -q && uv run aegisap-lab artifact rebuild --day 11`
- `uv run aegisap-lab audit-production --day 11 --strict`

## KQL Evidence

Save `build/day11/kql_evidence.json` before you patch production code. Capture at least one literal Log Analytics query with workspace, expected signal, observed excerpt, and operator interpretation. The facilitator or CAB reviewer may replay one saved query live.

## Verification Commands

```bash
uv run python -m pytest tests/day11/test_actor_verification.py tests/day11/test_obo_flow.py tests/day11/test_obo_simulation.py -q
uv run aegisap-lab artifact rebuild --day 11
```

## Key Files

- `modules/day_11_delegated_identity/README.md`
- `notebooks/day_11_delegated_identity_obo.py`
- `notebooks/bridges/day11_delegated_identity.md`
- `src/aegisap/identity/actor_verifier.py`
- `src/aegisap/identity/obo.py`
- `scripts/verify_delegated_identity_contract.py`
- `scenarios/day11`

## Automated Drill

- `uv run aegisap-lab drill list --day 11`
- `uv run aegisap-lab drill inject --day 11`
- `uv run aegisap-lab drill reset --day 11`
- `uv run aegisap-lab mastery --day 11` writes `build/day11/constraint_lineage.json` so later reviews can see the inherited rules this day still carries.
