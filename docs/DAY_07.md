# Day 7 - Evaluation, Guardrails, Structured Refusal, and Slice Governance

Primary learner entrypoint: `modules/day_07_eval_guardrails/README.md`.

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

## Incident Entry

```bash
uv run aegisap-lab incident start --day 07
```

## Mastery Gate

- `uv run python -m pytest tests/day7/security/test_redaction.py tests/day7/audit/test_audit_row_written_for_sensitive_decision.py -q && uv run aegisap-lab artifact rebuild --day 07`
- `uv run python evals/run_eval_suite.py --suite all --synthetic-cases build/day7/synthetic_cases_drift.jsonl --malicious-cases build/day7/malicious_cases_drift.jsonl --thresholds evals/score_thresholds.yaml --output build/day7/prompt_drift_report.json --enforce-thresholds`
- `uv run aegisap-lab audit-production --day 07 --strict`

## Verification Commands

```bash
uv run python -m pytest tests/day7/security/test_redaction.py tests/day7/audit/test_audit_row_written_for_sensitive_decision.py -q
uv run aegisap-lab artifact rebuild --day 07
uv run python evals/run_eval_suite.py --suite all --synthetic-cases build/day7/synthetic_cases_drift.jsonl --malicious-cases build/day7/malicious_cases_drift.jsonl --thresholds evals/score_thresholds.yaml --output build/day7/prompt_drift_report.json --enforce-thresholds
```

## Key Files

- `modules/day_07_eval_guardrails/README.md`
- `notebooks/day_7_testing_eval_guardrails.py`
- `notebooks/bridges/day07_guardrail_redaction.md`
- `src/aegisap/security/redaction.py`
- `src/aegisap/audit/events.py`
- `src/aegisap/audit/writer.py`
- `src/aegisap/day3/policies/source_authority_rules.yaml`
- `src/aegisap/day3/retrieval/authority_policy.py`
- `scenarios/day07`

## Automated Drill

- `uv run aegisap-lab drill list --day 07`
- `uv run aegisap-lab drill inject --day 07`
- `uv run aegisap-lab drill reset --day 07`
- `uv run aegisap-lab mastery --day 07` writes `build/day7/constraint_lineage.json` so later reviews can see the inherited rules this day still carries.
