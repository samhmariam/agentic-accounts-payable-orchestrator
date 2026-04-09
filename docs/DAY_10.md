# Day 10 - Production Acceptance, Release Evidence, and Change Board Readiness

Primary learner entrypoint: `modules/day_10_production_acceptance/README.md`.

## Why This Matters to an FDE

Release acceptance is where technical fixes become enterprise commitments. An FDE has to defend the packet, the ownership map, and the rollback path together.

## Customer Context

The customer CAB will not approve rollout without a release packet that proves security posture, ownership, rollback readiness, and cost governance survived the repair.

## Cost of Failure

If release evidence goes false-green, the CAB can approve a broken deployment and force an emergency rollback under executive scrutiny.

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

## Incident Entry

```bash
uv run aegisap-lab incident start --day 10
```

## Mastery Gate

- `uv run python -m pytest tests/day10/test_deployment_contract.py tests/day10/test_release_security.py tests/day10/test_release_envelope.py tests/training/test_checkpoints.py tests/api/test_app.py -q && uv run aegisap-lab artifact rebuild --day 10`
- `uv run aegisap-lab audit-production --day 10 --strict`

## Native Tooling Gate

- Policy source: `docs/curriculum/NATIVE_TOOLING_POLICY.md`
- Save raw proof to `build/day10/native_operator_evidence.json` before you patch production code.
- Append `-o json` to Azure CLI diagnostics so the CAB packet stores machine-readable output.
- Allowed: Azure Portal, `az`, `az rest`, raw KQL, `git`, `curl`, `nslookup` or `Resolve-DnsName`
- Tools banned during this gate: `aegisap-lab`, helper verification wrappers, and canned answer keys
- Until both raw evidence files are complete, wrappers stay banned. After that, wrappers are allowed only for artifact rebuild, mastery, or reset flows.
- Day 10 evidence is CAB-facing and must include at least two literal native commands plus one raw KQL query.

## Rollback Rehearsal

- Save exercised rollback proof to `build/day10/rollback_rehearsal.json`.
- The rollback unit is the ACA revision, not a Git commit.
- Shift 100% of live traffic back to the last-known-good revision with `az containerapp ingress traffic set ... -o json` before discussing Git history.
- Verify the routed revision identity with `az containerapp ingress traffic show ... -o json`.
- Wait for replica readiness with retry/backoff before judging `/health/ready` or `/version` probes.
- A Git-only revert does not satisfy rollback proof.

## CAB Review Mode

- Peer checklist file: `docs/curriculum/checklists/day10_peer_red_team.md`
- Reviewers must replay at least one saved KQL query live before approval.
- Revert Proof is mandatory and must name the rollback mechanism, last-known-good target, time-box, and exercised rollback evidence.


- Review mode: `cab_board`
- Required review roles: `cab_chair`, `client_ciso_or_infra_lead`
- The board may replay `build/day9/native_operator_evidence.json` live before approving the release packet
- CAB approval is blocked if Days 05-09 native or KQL evidence is missing, structurally weak, or inconsistent with the release packet

- Save `build/day10/diagnostic_timeline.md` while you investigate so the scoring panel can verify the first symptom, first telemetry proof, subsystem narrowed, durable repair, and post-fix confirmation.

## KQL Evidence

Save `build/day10/kql_evidence.json` before you patch production code. Capture at least one literal Log Analytics query before the repo patch with capture order, `captured_before_patch=true`, workspace, `first_signal_or_followup`, correlation or trace reference when available, observed excerpt, and operator interpretation. The facilitator or CAB reviewer may replay one saved query live. The CAB packet now statically validates the full Days 05-09 native and KQL evidence chain before board readiness is accepted.

## Verification Commands

```bash
uv run python -m pytest tests/day10/test_deployment_contract.py tests/day10/test_release_security.py tests/day10/test_release_envelope.py tests/training/test_checkpoints.py tests/api/test_app.py -q
uv run aegisap-lab artifact rebuild --day 10
```

## Investigation Surfaces

- `notebooks/day_10_production_operations.py`
- `notebooks/bridges/day10_release_evidence.md`
- Incident Asset Ref: `incident.day10`
- Repair Domain: `Gates`
- Repair Domain: `Check All Gates`
- Repair Domain: `Checkpoints`

## Automated Drill

- `uv run aegisap-lab drill list --day 10`
- `uv run aegisap-lab drill inject --day 10`
- `uv run aegisap-lab drill reset --day 10`
- `uv run aegisap-lab mastery --day 10` writes `build/day10/constraint_lineage.json` so later reviews can see the inherited rules this day still carries.
