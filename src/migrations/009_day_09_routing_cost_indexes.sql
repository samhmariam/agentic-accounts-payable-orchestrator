BEGIN;

CREATE INDEX IF NOT EXISTS idx_workflow_threads_status_updated_at
    ON workflow_threads (status, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_workflow_checkpoints_thread_node
    ON workflow_checkpoints (thread_id, node_name, checkpoint_seq DESC);

COMMIT;
