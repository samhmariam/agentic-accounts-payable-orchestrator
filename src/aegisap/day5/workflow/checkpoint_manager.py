from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import psycopg

from aegisap.day5.persistence.durable_state_store import DurableStateStore
from aegisap.day5.state.checksum import compute_state_checksum
from aegisap.day5.state.durable_models import DurableWorkflowState, STATE_SCHEMA_VERSION


class CheckpointValidationError(RuntimeError):
    pass


@dataclass
class LoadedCheckpoint:
    checkpoint_id: str
    state: DurableWorkflowState
    is_interrupt_checkpoint: bool


class CheckpointManager:
    def __init__(self, store: DurableStateStore) -> None:
        self.store = store

    def save_checkpoint(
        self,
        *,
        state: DurableWorkflowState,
        node_name: str,
        is_interrupt_checkpoint: bool = False,
        history_summary_json: dict | None = None,
        checkpoint_id: str | None = None,
        conn: psycopg.Connection | None = None,
    ) -> str:
        state.updated_at = datetime.now(timezone.utc)
        state.checkpoint_seq += 1
        state.current_node = node_name
        state.state_checksum = compute_state_checksum(state)

        self.store.create_thread(
            thread_id=state.thread_id,
            case_id=state.case_id,
            workflow_name=state.workflow_name,
            status=state.thread_status,
            state_schema_version=state.state_schema_version,
            conn=conn,
        )
        return self.store.insert_checkpoint(
            thread_id=state.thread_id,
            node_name=node_name,
            checkpoint_seq=state.checkpoint_seq,
            state=state,
            state_checksum=state.state_checksum,
            history_summary_json=history_summary_json,
            is_interrupt_checkpoint=is_interrupt_checkpoint,
            checkpoint_id=checkpoint_id,
            conn=conn,
        )

    def load_latest_checkpoint(
        self,
        thread_id: str,
        *,
        conn: psycopg.Connection | None = None,
    ) -> LoadedCheckpoint:
        stored = self.store.get_latest_checkpoint(thread_id, conn=conn)
        if stored is None:
            raise CheckpointValidationError(f"No checkpoint found for thread_id={thread_id}")

        state = DurableWorkflowState.model_validate(stored.state_json)
        expected_checksum = compute_state_checksum(state)

        if stored.state_checksum != expected_checksum:
            self.store.mark_thread_quarantined(
                thread_id,
                reason=(
                    f"Checksum mismatch at checkpoint {stored.checkpoint_id}: "
                    f"stored={stored.state_checksum}, expected={expected_checksum}"
                ),
                conn=conn,
            )
            raise CheckpointValidationError("Checkpoint checksum mismatch.")

        if state.state_schema_version > STATE_SCHEMA_VERSION:
            raise CheckpointValidationError(
                f"Unsupported forward schema version: {state.state_schema_version} > {STATE_SCHEMA_VERSION}"
            )

        return LoadedCheckpoint(
            checkpoint_id=stored.checkpoint_id,
            state=state,
            is_interrupt_checkpoint=stored.is_interrupt_checkpoint,
        )
