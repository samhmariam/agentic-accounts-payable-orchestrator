BEGIN;

CREATE TABLE IF NOT EXISTS workflow_threads (
    thread_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    workflow_name TEXT NOT NULL,
    status TEXT NOT NULL,
    current_checkpoint_id TEXT,
    current_checkpoint_seq INTEGER NOT NULL DEFAULT 0,
    state_schema_version INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_workflow_threads_case_id
    ON workflow_threads (case_id);

CREATE INDEX IF NOT EXISTS idx_workflow_threads_status
    ON workflow_threads (status);

CREATE TABLE IF NOT EXISTS workflow_checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL REFERENCES workflow_threads(thread_id) ON DELETE CASCADE,
    checkpoint_seq INTEGER NOT NULL,
    node_name TEXT NOT NULL,
    state_schema_version INTEGER NOT NULL,
    state_json JSONB NOT NULL,
    state_checksum TEXT NOT NULL,
    history_summary_json JSONB,
    is_interrupt_checkpoint BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(thread_id, checkpoint_seq)
);

CREATE INDEX IF NOT EXISTS idx_workflow_checkpoints_thread_id
    ON workflow_checkpoints (thread_id, checkpoint_seq DESC);

CREATE TABLE IF NOT EXISTS approval_tasks (
    approval_task_id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL REFERENCES workflow_threads(thread_id) ON DELETE CASCADE,
    checkpoint_id TEXT NOT NULL REFERENCES workflow_checkpoints(checkpoint_id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    assigned_to TEXT,
    decision_payload JSONB,
    due_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_approval_tasks_thread_id
    ON approval_tasks (thread_id);

CREATE INDEX IF NOT EXISTS idx_approval_tasks_status
    ON approval_tasks (status);

CREATE TABLE IF NOT EXISTS side_effect_ledger (
    effect_key TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL REFERENCES workflow_threads(thread_id) ON DELETE CASCADE,
    checkpoint_id TEXT NOT NULL REFERENCES workflow_checkpoints(checkpoint_id) ON DELETE CASCADE,
    effect_type TEXT NOT NULL,
    effect_payload_hash TEXT NOT NULL,
    effect_result_json JSONB NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_side_effect_ledger_thread_id
    ON side_effect_ledger (thread_id);

CREATE INDEX IF NOT EXISTS idx_side_effect_ledger_effect_type
    ON side_effect_ledger (effect_type);

CREATE TABLE IF NOT EXISTS history_compactions (
    compaction_id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL REFERENCES workflow_threads(thread_id) ON DELETE CASCADE,
    up_to_checkpoint_seq INTEGER NOT NULL,
    summary_json JSONB NOT NULL,
    source_message_range JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_history_compactions_thread_id
    ON history_compactions (thread_id, up_to_checkpoint_seq DESC);

COMMIT;
