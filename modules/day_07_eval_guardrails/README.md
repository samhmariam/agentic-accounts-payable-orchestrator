# Day 7 Module Wormhole

## Why This Matters to an FDE

Guardrails are not decorations. FDEs have to prove that sensitive content stays redacted, auditable, and governable even when prompts or test slices get adversarial.

## Customer Context

The customer risk team wants evidence that prompt injection and PII leakage are rejected before anything lands in logs or audit evidence.

## Cost of Failure

If sensitive content leaks into audit material, the customer faces privacy escalation, frozen releases, and possible regulator notification.

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
- `uv run python evals/run_eval_suite.py --suite all --synthetic-cases build/day7/synthetic_cases_drift.jsonl --malicious-cases build/day7/malicious_cases_drift.jsonl --thresholds evals/score_thresholds.yaml --output build/day7/prompt_drift_report.json --enforce-thresholds`
- `uv run aegisap-lab audit-production --day 07 --strict`

## Native Tooling Gate

- Policy source: `docs/curriculum/NATIVE_TOOLING_POLICY.md`
- Save raw proof to `build/day7/native_operator_evidence.json` before you patch production code.
- Append `-o json` to Azure CLI diagnostics so the signal-family matcher can replay machine-readable output.
- Allowed: Azure Portal, `az`, `az rest`, raw KQL, `git`, `curl`, `nslookup` or `Resolve-DnsName`
- Tools banned during this gate: `aegisap-lab`, helper verification wrappers, and canned answer keys
- Until both raw evidence files are complete, wrappers stay banned. After that, wrappers are allowed only for artifact rebuild, mastery, or reset flows.

## KQL Evidence

Save `build/day7/kql_evidence.json` before you patch production code. Capture at least one literal Log Analytics query with workspace, expected signal, observed excerpt, and operator interpretation. Shadow-drift drills must still be diagnosed from current-day telemetry and evidence only.

## Early Transfer Proof

- Hostile fixtures: `fixtures/capstone_b/claims_intake/`
- Adapter boundary: `src/aegisap/transfer/claims_adapter.py`
- Transfer artifact: `build/day7/claims_transfer_report.json`

## Chaos Gate

- Failure signal: A probabilistic authority drift keeps the app running while eval evidence shows the authority boundary is eroding.
- Diagnostic surface: Content-safety notebook evidence, evaluation traces, `build/day7/` drift cases, and Day 3 authority-policy code.
- Expected recovery artifact: `build/day7/prompt_drift_report.json`
- Time box: 25 minutes

## Day X File Manifest

Do not edit code in this module folder.

- Diagnostic Notebook: `notebooks/day_7_testing_eval_guardrails.py`
- Primary Day Doc: `docs/DAY_07.md`
- Rosetta Stone Bridge: `notebooks/bridges/day07_guardrail_redaction.md`
- Production Target: `src/aegisap/security/redaction.py`
- Production Target: `src/aegisap/audit/events.py`
- Production Target: `src/aegisap/audit/writer.py`
- Drift Repair Target: `src/aegisap/day3/policies/source_authority_rules.yaml`
- Drift Repair Target: `src/aegisap/day3/retrieval/authority_policy.py`
- Transfer Adapter Target: `src/aegisap/transfer/claims_adapter.py`
- Transfer Artifact: `build/day7/claims_transfer_report.json`
- Scenario Pack: `scenarios/day07`
- Verification Command: `uv run python -m pytest tests/day7/security/test_redaction.py tests/day7/audit/test_audit_row_written_for_sensitive_decision.py -q`
- Verification Command: `uv run aegisap-lab artifact rebuild --day 07`
- Verification Command: `uv run python evals/run_eval_suite.py --suite all --synthetic-cases build/day7/synthetic_cases_drift.jsonl --malicious-cases build/day7/malicious_cases_drift.jsonl --thresholds evals/score_thresholds.yaml --output build/day7/prompt_drift_report.json --enforce-thresholds`
- Native Evidence Artifact: `build/day7/native_operator_evidence.json`
- KQL Evidence Artifact: `build/day7/kql_evidence.json`

## Automated Drill

- List drills: `uv run aegisap-lab drill list --day 07`
- Inject default drill: `uv run aegisap-lab drill inject --day 07`
- Reset active drill: `uv run aegisap-lab drill reset --day 07`
- Constraint lineage artifact after mastery: `build/day7/constraint_lineage.json`
