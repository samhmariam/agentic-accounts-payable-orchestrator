from __future__ import annotations

import json
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Iterator

import psycopg

from aegisap.audit.models import AuditEvent
from aegisap.day5.state.durable_models import DurableWorkflowState


@dataclass
class StoredCheckpoint:
    checkpoint_id: str
    checkpoint_seq: int
    node_name: str
    state_json: dict[str, Any]
    state_checksum: str
    is_interrupt_checkpoint: bool


@dataclass
class StoredApprovalTask:
    approval_task_id: str
    thread_id: str
    checkpoint_id: str
    status: str
    assigned_to: str | None
    decision_payload: dict[str, Any] | None


@dataclass
class StoredReviewTask:
    review_task_id: str
    thread_id: str
    checkpoint_id: str
    status: str
    assigned_to: str | None
    decision_payload: dict[str, Any] | None


@dataclass
class StoredSideEffect:
    effect_key: str
    effect_type: str
    effect_result_json: dict[str, Any]
    status: str


@dataclass
class StoredAuditEvent:
    audit_id: str
    thread_id: str
    action_type: str
    decision_outcome: str
    trace_id: str | None
    payload_json: dict[str, Any]


class DurableStateStore:
    def __init__(
        self,
        dsn: str | None = None,
        *,
        connect_factory: Callable[[], psycopg.Connection] | None = None,
    ) -> None:
        if dsn is None and connect_factory is None:
            raise ValueError("Either dsn or connect_factory must be provided.")
        self.dsn = dsn
        self.connect_factory = connect_factory

    @contextmanager
    def connection(self) -> Iterator[psycopg.Connection]:
        if self.connect_factory is not None:
            with self.connect_factory() as conn:
                yield conn
            return

        assert self.dsn is not None
        with psycopg.connect(self.dsn) as conn:
            yield conn

    def create_thread(
        self,
        *,
        thread_id: str,
        case_id: str,
        workflow_name: str,
        status: str,
        state_schema_version: int,
        conn: psycopg.Connection | None = None,
    ) -> None:
        with self._cursor(conn) as (active_conn, cur):
            cur.execute(
                """
                INSERT INTO workflow_threads (
                    thread_id, case_id, workflow_name, status, state_schema_version
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (thread_id) DO NOTHING
                """,
                (thread_id, case_id, workflow_name, status, state_schema_version),
            )
            self._commit_if_owned(conn, active_conn)

    def insert_checkpoint(
        self,
        *,
        thread_id: str,
        node_name: str,
        checkpoint_seq: int,
        state: DurableWorkflowState,
        state_checksum: str,
        history_summary_json: dict[str, Any] | None = None,
        is_interrupt_checkpoint: bool = False,
        checkpoint_id: str | None = None,
        conn: psycopg.Connection | None = None,
    ) -> str:
        checkpoint_id = checkpoint_id or str(uuid.uuid4())
        state_json = state.model_dump(mode="json")

        with self._cursor(conn) as (active_conn, cur):
            cur.execute(
                """
                INSERT INTO workflow_checkpoints (
                    checkpoint_id, thread_id, checkpoint_seq, node_name,
                    state_schema_version, state_json, state_checksum,
                    history_summary_json, is_interrupt_checkpoint
                )
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s::jsonb, %s)
                """,
                (
                    checkpoint_id,
                    thread_id,
                    checkpoint_seq,
                    node_name,
                    state.state_schema_version,
                    json.dumps(state_json),
                    state_checksum,
                    json.dumps(history_summary_json) if history_summary_json else None,
                    is_interrupt_checkpoint,
                ),
            )
            self._advance_thread_pointer(
                thread_id=thread_id,
                checkpoint_id=checkpoint_id,
                checkpoint_seq=checkpoint_seq,
                status=state.thread_status,
                state_schema_version=state.state_schema_version,
                conn=active_conn,
            )
            self._commit_if_owned(conn, active_conn)

        return checkpoint_id

    def get_latest_checkpoint(
        self,
        thread_id: str,
        *,
        conn: psycopg.Connection | None = None,
    ) -> StoredCheckpoint | None:
        with self._cursor(conn) as (_active_conn, cur):
            cur.execute(
                """
                SELECT checkpoint_id, checkpoint_seq, node_name, state_json, state_checksum, is_interrupt_checkpoint
                FROM workflow_checkpoints
                WHERE thread_id = %s
                ORDER BY checkpoint_seq DESC
                LIMIT 1
                """,
                (thread_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return StoredCheckpoint(
                checkpoint_id=row[0],
                checkpoint_seq=row[1],
                node_name=row[2],
                state_json=row[3],
                state_checksum=row[4],
                is_interrupt_checkpoint=row[5],
            )

    def create_approval_task(
        self,
        *,
        thread_id: str,
        checkpoint_id: str,
        assigned_to: str | None,
        due_at: str | None = None,
        approval_task_id: str | None = None,
        conn: psycopg.Connection | None = None,
    ) -> str:
        approval_task_id = approval_task_id or str(uuid.uuid4())
        with self._cursor(conn) as (active_conn, cur):
            cur.execute(
                """
                INSERT INTO approval_tasks (
                    approval_task_id, thread_id, checkpoint_id, status, assigned_to, due_at
                )
                VALUES (%s, %s, %s, 'pending', %s, %s)
                """,
                (approval_task_id, thread_id, checkpoint_id, assigned_to, due_at),
            )
            self._commit_if_owned(conn, active_conn)
        return approval_task_id

    def get_approval_task(
        self,
        approval_task_id: str,
        *,
        conn: psycopg.Connection | None = None,
    ) -> StoredApprovalTask | None:
        with self._cursor(conn) as (_active_conn, cur):
            cur.execute(
                """
                SELECT approval_task_id, thread_id, checkpoint_id, status, assigned_to, decision_payload
                FROM approval_tasks
                WHERE approval_task_id = %s
                """,
                (approval_task_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return StoredApprovalTask(
                approval_task_id=row[0],
                thread_id=row[1],
                checkpoint_id=row[2],
                status=row[3],
                assigned_to=row[4],
                decision_payload=row[5],
            )

    def create_review_task(
        self,
        *,
        thread_id: str,
        checkpoint_id: str,
        assigned_to: str | None,
        review_task_id: str | None = None,
        conn: psycopg.Connection | None = None,
    ) -> str:
        review_task_id = review_task_id or str(uuid.uuid4())
        with self._cursor(conn) as (active_conn, cur):
            cur.execute(
                """
                INSERT INTO review_tasks (
                    review_task_id, thread_id, checkpoint_id, status, assigned_to
                )
                VALUES (%s, %s, %s, 'pending', %s)
                """,
                (review_task_id, thread_id, checkpoint_id, assigned_to),
            )
            self._commit_if_owned(conn, active_conn)
        return review_task_id

    def get_review_task(
        self,
        review_task_id: str,
        *,
        conn: psycopg.Connection | None = None,
    ) -> StoredReviewTask | None:
        with self._cursor(conn) as (_active_conn, cur):
            cur.execute(
                """
                SELECT review_task_id, thread_id, checkpoint_id, status, assigned_to, decision_payload
                FROM review_tasks
                WHERE review_task_id = %s
                """,
                (review_task_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return StoredReviewTask(
                review_task_id=row[0],
                thread_id=row[1],
                checkpoint_id=row[2],
                status=row[3],
                assigned_to=row[4],
                decision_payload=row[5],
            )

    def resolve_approval_task(
        self,
        *,
        approval_task_id: str,
        status: str,
        decision_payload: dict[str, Any],
        conn: psycopg.Connection | None = None,
    ) -> None:
        with self._cursor(conn) as (active_conn, cur):
            cur.execute(
                """
                UPDATE approval_tasks
                SET status = %s, decision_payload = %s::jsonb, resolved_at = NOW()
                WHERE approval_task_id = %s
                """,
                (status, json.dumps(decision_payload), approval_task_id),
            )
            self._commit_if_owned(conn, active_conn)

    def get_side_effect(
        self,
        effect_key: str,
        *,
        conn: psycopg.Connection | None = None,
    ) -> StoredSideEffect | None:
        with self._cursor(conn) as (_active_conn, cur):
            cur.execute(
                """
                SELECT effect_key, effect_type, effect_result_json, status
                FROM side_effect_ledger
                WHERE effect_key = %s
                """,
                (effect_key,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return StoredSideEffect(
                effect_key=row[0],
                effect_type=row[1],
                effect_result_json=row[2],
                status=row[3],
            )

    def try_start_side_effect(
        self,
        *,
        effect_key: str,
        thread_id: str,
        checkpoint_id: str,
        effect_type: str,
        effect_payload_hash: str,
        conn: psycopg.Connection | None = None,
    ) -> bool:
        with self._cursor(conn) as (active_conn, cur):
            cur.execute(
                """
                INSERT INTO side_effect_ledger (
                    effect_key, thread_id, checkpoint_id, effect_type,
                    effect_payload_hash, effect_result_json, status
                )
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, 'pending')
                ON CONFLICT (effect_key) DO NOTHING
                RETURNING effect_key
                """,
                (
                    effect_key,
                    thread_id,
                    checkpoint_id,
                    effect_type,
                    effect_payload_hash,
                    json.dumps({}),
                ),
            )
            started = cur.fetchone() is not None
            self._commit_if_owned(conn, active_conn)
            return started

    def complete_side_effect(
        self,
        *,
        effect_key: str,
        effect_result_json: dict[str, Any],
        conn: psycopg.Connection | None = None,
    ) -> None:
        with self._cursor(conn) as (active_conn, cur):
            cur.execute(
                """
                UPDATE side_effect_ledger
                SET effect_result_json = %s::jsonb, status = 'applied'
                WHERE effect_key = %s
                """,
                (json.dumps(effect_result_json), effect_key),
            )
            self._commit_if_owned(conn, active_conn)

    def fail_side_effect(
        self,
        *,
        effect_key: str,
        conn: psycopg.Connection | None = None,
    ) -> None:
        with self._cursor(conn) as (active_conn, cur):
            cur.execute(
                """
                UPDATE side_effect_ledger
                SET status = 'failed'
                WHERE effect_key = %s
                """,
                (effect_key,),
            )
            self._commit_if_owned(conn, active_conn)

    def insert_audit_event(
        self,
        *,
        event: AuditEvent,
        conn: psycopg.Connection | None = None,
    ) -> None:
        payload = event.model_dump(mode="json")
        with self._cursor(conn) as (active_conn, cur):
            cur.execute(
                """
                INSERT INTO workflow_audit_events (
                    audit_id,
                    timestamp_utc,
                    workflow_run_id,
                    thread_id,
                    state_version,
                    actor_type,
                    actor_id,
                    action_type,
                    decision_outcome,
                    approval_status,
                    evidence_summary_redacted,
                    evidence_refs,
                    pii_redaction_applied,
                    policy_version,
                    planner_version,
                    error_code,
                    trace_id,
                    payload_json
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s::jsonb
                )
                ON CONFLICT (audit_id) DO NOTHING
                """,
                (
                    event.audit_id,
                    event.timestamp_utc,
                    event.workflow_run_id,
                    event.thread_id,
                    event.state_version,
                    event.actor_type,
                    event.actor_id,
                    event.action_type,
                    event.decision_outcome,
                    event.approval_status,
                    event.evidence_summary_redacted,
                    json.dumps(event.evidence_refs),
                    event.pii_redaction_applied,
                    event.policy_version,
                    event.planner_version,
                    event.error_code,
                    event.trace_id,
                    json.dumps(payload),
                ),
            )
            self._commit_if_owned(conn, active_conn)

    def list_audit_events(
        self,
        *,
        thread_id: str,
        limit: int = 25,
        conn: psycopg.Connection | None = None,
    ) -> list[StoredAuditEvent]:
        with self._cursor(conn) as (_active_conn, cur):
            cur.execute(
                """
                SELECT audit_id, thread_id, action_type, decision_outcome, trace_id, payload_json
                FROM workflow_audit_events
                WHERE thread_id = %s
                ORDER BY timestamp_utc DESC
                LIMIT %s
                """,
                (thread_id, limit),
            )
            rows = cur.fetchall() or []
            return [
                StoredAuditEvent(
                    audit_id=row[0],
                    thread_id=row[1],
                    action_type=row[2],
                    decision_outcome=row[3],
                    trace_id=row[4],
                    payload_json=row[5],
                )
                for row in rows
            ]

    def mark_thread_quarantined(
        self,
        thread_id: str,
        reason: str,
        *,
        conn: psycopg.Connection | None = None,
    ) -> None:
        with self._cursor(conn) as (active_conn, cur):
            cur.execute(
                """
                UPDATE workflow_threads
                SET status = 'quarantined', updated_at = NOW()
                WHERE thread_id = %s
                """,
                (thread_id,),
            )
            cur.execute(
                """
                INSERT INTO history_compactions (
                    compaction_id, thread_id, up_to_checkpoint_seq, summary_json, source_message_range
                )
                VALUES (%s, %s, 0, %s::jsonb, %s::jsonb)
                """,
                (
                    str(uuid.uuid4()),
                    thread_id,
                    json.dumps({"quarantine_reason": reason}),
                    json.dumps({"start": 0, "end": 0}),
                ),
            )
            self._commit_if_owned(conn, active_conn)

    def _advance_thread_pointer(
        self,
        *,
        thread_id: str,
        checkpoint_id: str,
        checkpoint_seq: int,
        status: str,
        state_schema_version: int,
        conn: psycopg.Connection,
    ) -> None:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE workflow_threads
                SET
                    current_checkpoint_id = %s,
                    current_checkpoint_seq = %s,
                    status = %s,
                    state_schema_version = %s,
                    updated_at = NOW()
                WHERE thread_id = %s
                """,
                (
                    checkpoint_id,
                    checkpoint_seq,
                    status,
                    state_schema_version,
                    thread_id,
                ),
            )

    @contextmanager
    def _cursor(
        self,
        conn: psycopg.Connection | None,
    ) -> Iterator[tuple[psycopg.Connection, psycopg.Cursor]]:
        if conn is not None:
            with conn.cursor() as cur:
                yield conn, cur
            return

        with self.connection() as owned_conn, owned_conn.cursor() as cur:
            yield owned_conn, cur

    def _commit_if_owned(
        self,
        provided_conn: psycopg.Connection | None,
        active_conn: psycopg.Connection,
    ) -> None:
        if provided_conn is None:
            active_conn.commit()
