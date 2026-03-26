# Audit Schema

The canonical Day 7 audit row is stored in PostgreSQL table
`workflow_audit_events`.

## Required Fields

- `audit_id`
- `timestamp_utc`
- `workflow_run_id`
- `thread_id`
- `state_version`
- `actor_type`
- `actor_id`
- `action_type`
- `decision_outcome`
- `evidence_summary_redacted`
- `evidence_refs`
- `pii_redaction_applied`
- `trace_id`

## Typical Action Types

- `vendor_check`
- `po_match_check`
- `bank_detail_evaluation`
- `payment_recommendation`
- `human_approval`
- `refusal`
- `resume`
- `secret_read`

## Audit Design Rules

- Store references and redacted summaries, not raw invoice text.
- Tie audit rows to Day 5 `state_version` and Day 6 outcome semantics.
- Emit rows for approvals, refusals, resumptions, and any sensitive runtime decision.
