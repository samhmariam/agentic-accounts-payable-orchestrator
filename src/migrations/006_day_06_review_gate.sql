BEGIN;

CREATE TABLE IF NOT EXISTS review_tasks (
    review_task_id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL REFERENCES workflow_threads(thread_id) ON DELETE CASCADE,
    checkpoint_id TEXT NOT NULL REFERENCES workflow_checkpoints(checkpoint_id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    assigned_to TEXT,
    decision_payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_review_tasks_thread_id
    ON review_tasks (thread_id);

CREATE INDEX IF NOT EXISTS idx_review_tasks_status
    ON review_tasks (status);

COMMIT;
