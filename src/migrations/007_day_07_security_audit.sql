BEGIN;

CREATE TABLE IF NOT EXISTS workflow_audit_events (
    audit_id TEXT PRIMARY KEY,
    timestamp_utc TIMESTAMPTZ NOT NULL,
    workflow_run_id TEXT NOT NULL,
    thread_id TEXT NOT NULL REFERENCES workflow_threads(thread_id) ON DELETE CASCADE,
    state_version INTEGER NOT NULL,
    actor_type TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    decision_outcome TEXT NOT NULL,
    approval_status TEXT,
    evidence_summary_redacted TEXT NOT NULL,
    evidence_refs JSONB NOT NULL DEFAULT '[]'::jsonb,
    pii_redaction_applied BOOLEAN NOT NULL DEFAULT FALSE,
    policy_version TEXT,
    planner_version TEXT,
    error_code TEXT,
    trace_id TEXT,
    payload_json JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_workflow_audit_events_thread_id
    ON workflow_audit_events (thread_id, timestamp_utc DESC);

CREATE INDEX IF NOT EXISTS idx_workflow_audit_events_action_type
    ON workflow_audit_events (action_type);

CREATE INDEX IF NOT EXISTS idx_workflow_audit_events_trace_id
    ON workflow_audit_events (trace_id);

COMMIT;
