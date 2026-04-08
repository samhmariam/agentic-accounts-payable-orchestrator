# Day 10 Module Wormhole

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

## FDE Implementation Cycle

- Customer Reality: inspect the live incident and portal surface before you theorize.
- Diagnostic Bridge: prove the state in Marimo and name the API or SDK call that matches the portal behavior.
- Production Engineering: patch the durable code in the repo, not inside the notebook.
- Chaos Gate: recover under the time box and defend the trade-off in review language.

## Mastery Gate

- `uv run python -m pytest tests/day10/test_deployment_contract.py tests/day10/test_release_security.py tests/day10/test_release_envelope.py tests/training/test_checkpoints.py tests/api/test_app.py -q && uv run aegisap-lab artifact rebuild --day 10`
- `uv run aegisap-lab audit-production --day 10 --strict`

## KQL Evidence

Save `build/day10/kql_evidence.json` before you patch production code. Capture at least one literal Log Analytics query with workspace, expected signal, observed excerpt, and operator interpretation. The facilitator or CAB reviewer may replay one saved query live.

## Chaos Gate

- Failure signal: A release gate or evidence packet is incomplete, leaving production acceptance without defensible proof.
- Diagnostic surface: Deployment gate outputs, checkpoint artifacts, release envelope evidence, and cloud-truth posture checks.
- Expected recovery artifact: `build/day10/release_envelope.json`
- Time box: 30 minutes

## CAB Review Mode

- Peer checklist file: `docs/curriculum/checklists/day10_peer_red_team.md`
- Reviewers must replay at least one saved KQL query live before approval.
- Revert Proof is mandatory and must name the rollback mechanism, last-known-good target, time-box, and exercised or dry-run evidence.


- Review mode: `cab_board`
- Required review roles: `cab_chair`, `client_ciso_or_infra_lead`
- The board may replay `build/day9/native_operator_evidence.json` live before approving the release packet

## Day X File Manifest

Do not edit code in this module folder.

- Diagnostic Notebook: `notebooks/day_10_production_operations.py`
- Primary Day Doc: `docs/DAY_10.md`
- Rosetta Stone Bridge: `notebooks/bridges/day10_release_evidence.md`
- Production Target: `src/aegisap/deploy/gates.py`
- Production Target: `scripts/check_all_gates.py`
- Production Target: `src/aegisap/training/checkpoints.py`
- Scenario Pack: `scenarios/day10`
- Verification Command: `uv run python -m pytest tests/day10/test_deployment_contract.py tests/day10/test_release_security.py tests/day10/test_release_envelope.py tests/training/test_checkpoints.py tests/api/test_app.py -q`
- Verification Command: `uv run aegisap-lab artifact rebuild --day 10`

## Automated Drill

- List drills: `uv run aegisap-lab drill list --day 10`
- Inject default drill: `uv run aegisap-lab drill inject --day 10`
- Reset active drill: `uv run aegisap-lab drill reset --day 10`
- Constraint lineage artifact after mastery: `build/day10/constraint_lineage.json`
