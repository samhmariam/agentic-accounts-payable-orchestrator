# Day 7 Module Wormhole

## Why This Matters to an FDE

Guardrails are not decorations. FDEs have to prove that sensitive content stays redacted, auditable, and governable even when prompts or test slices get adversarial.

## Customer Context

The customer risk team wants evidence that prompt injection and PII leakage are rejected before anything lands in logs or audit evidence.

## Persistent Constraints

- `regulated_invoice_auditability`: Every financial decision path must leave auditable evidence that survives hostile review.
- `latency_budget_guardrails`: Queue, retry, and latency controls must be explicit enough to defend under customer SLA pressure.
- `authoritative_retrieval_sources`: Retrieval must prefer authoritative source systems over stale or ambiguous evidence.
- `no_public_endpoints`: Production-bound AI and data services must not expose public network access.
- `fail_closed_decisions`: Risky automation paths must fail closed and require explicit human review.
- `durable_resume_idempotency`: Durable state recovery must resume safely without duplicating side effects.
- `conflicting_authority_refusal`: Conflicting records or review evidence must trigger refusal rather than silent blending.
- `pii_redaction_before_audit`: Sensitive content must be redacted before logging, audit writes, or downstream release evidence.

## FDE Implementation Cycle

- Customer Reality: inspect the live incident and portal surface before you theorize.
- Diagnostic Bridge: prove the state in Marimo and name the API or SDK call that matches the portal behavior.
- Production Engineering: patch the durable code in the repo, not inside the notebook.
- Chaos Gate: recover under the time box and defend the trade-off in review language.

## Mastery Gate

- `uv run python -m pytest tests/day7/security/test_redaction.py tests/day7/audit/test_audit_row_written_for_sensitive_decision.py -q && uv run aegisap-lab artifact rebuild --day 07`
- `uv run aegisap-lab audit-production --day 07 --strict`

## Chaos Gate

- Failure signal: A redaction or audit path leaks sensitive text into a Day 7 evaluation artifact.
- Diagnostic surface: Content-safety notebook evidence, redaction code, and audit writer outputs.
- Expected recovery artifact: `build/day7/eval_report.json`
- Time box: 25 minutes

## Day X File Manifest

Do not edit code in this module folder.

- Diagnostic Notebook: `notebooks/day_7_testing_eval_guardrails.py`
- Primary Day Doc: `docs/DAY_07.md`
- Rosetta Stone Bridge: `notebooks/bridges/day07_guardrail_redaction.md`
- Production Target: `src/aegisap/security/redaction.py`
- Production Target: `src/aegisap/audit/events.py`
- Production Target: `src/aegisap/audit/writer.py`
- Scenario Pack: `scenarios/day07`
- Verification Command: `uv run python -m pytest tests/day7/security/test_redaction.py tests/day7/audit/test_audit_row_written_for_sensitive_decision.py -q`
- Verification Command: `uv run aegisap-lab artifact rebuild --day 07`

## Automated Drill

- List drills: `uv run aegisap-lab drill list --day 07`
- Inject default drill: `uv run aegisap-lab drill inject --day 07`
- Reset active drill: `uv run aegisap-lab drill reset --day 07`
- Constraint lineage artifact after mastery: `build/day7/constraint_lineage.json`
