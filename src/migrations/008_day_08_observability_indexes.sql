BEGIN;

CREATE INDEX IF NOT EXISTS idx_workflow_audit_events_workflow_run_id
    ON workflow_audit_events (workflow_run_id, timestamp_utc DESC);

COMMIT;
