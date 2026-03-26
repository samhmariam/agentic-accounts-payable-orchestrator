from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from aegisap.day5.persistence.durable_state_store import DurableStateStore
from aegisap.day5.state.durable_models import DurableWorkflowState
from aegisap.day5.workflow.checkpoint_manager import CheckpointManager, CheckpointValidationError


class GraphRunner(Protocol):
    def resume(
        self,
        *,
        state: DurableWorkflowState,
        approval_decision: dict,
    ) -> DurableWorkflowState:
        ...


@dataclass
class ResumeTokenPayload:
    thread_id: str
    checkpoint_id: str
    checkpoint_seq: int
    approval_task_id: str


class ResumeTokenCodec:
    def __init__(self, secret_key: str) -> None:
        self.secret_key = secret_key.encode("utf-8")

    def encode(self, payload: ResumeTokenPayload) -> str:
        raw = json.dumps(payload.__dict__, sort_keys=True).encode("utf-8")
        sig = hmac.new(self.secret_key, raw, hashlib.sha256).hexdigest().encode("utf-8")
        return base64.urlsafe_b64encode(raw + b"." + sig).decode("utf-8")

    def decode(self, token: str) -> ResumeTokenPayload:
        decoded = base64.urlsafe_b64decode(token.encode("utf-8"))
        raw, sig = decoded.rsplit(b".", 1)
        expected_sig = hmac.new(self.secret_key, raw, hashlib.sha256).hexdigest().encode("utf-8")
        if not hmac.compare_digest(sig, expected_sig):
            raise ValueError("Invalid resume token signature.")
        payload = json.loads(raw.decode("utf-8"))
        return ResumeTokenPayload(**payload)


class ResumeService:
    def __init__(
        self,
        *,
        store: DurableStateStore,
        checkpoint_manager: CheckpointManager,
        graph_runner: GraphRunner,
        token_codec: ResumeTokenCodec,
    ) -> None:
        self.store = store
        self.checkpoint_manager = checkpoint_manager
        self.graph_runner = graph_runner
        self.token_codec = token_codec

    def create_resume_token(
        self,
        *,
        thread_id: str,
        checkpoint_id: str,
        checkpoint_seq: int,
        approval_task_id: str,
    ) -> str:
        return self.token_codec.encode(
            ResumeTokenPayload(
                thread_id=thread_id,
                checkpoint_id=checkpoint_id,
                checkpoint_seq=checkpoint_seq,
                approval_task_id=approval_task_id,
            )
        )

    def resume_after_approval(
        self,
        *,
        resume_token: str,
        decision_payload: dict,
        resumed_by: str,
    ) -> DurableWorkflowState:
        token = self.token_codec.decode(resume_token)

        with self.store.connection() as conn:
            try:
                approval_task = self.store.get_approval_task(token.approval_task_id, conn=conn)
                if approval_task is None:
                    raise ValueError("Approval task not found.")
                if approval_task.status != "pending":
                    raise ValueError("Approval task is no longer pending.")
                if approval_task.thread_id != token.thread_id:
                    raise ValueError("Approval task does not belong to thread.")
                if approval_task.checkpoint_id != token.checkpoint_id:
                    raise CheckpointValidationError("Approval task is not bound to the resume checkpoint.")

                loaded = self.checkpoint_manager.load_latest_checkpoint(token.thread_id, conn=conn)
                if loaded.checkpoint_id != token.checkpoint_id:
                    raise CheckpointValidationError("Resume token is stale: checkpoint has moved.")
                if loaded.state.checkpoint_seq != token.checkpoint_seq:
                    raise CheckpointValidationError("Resume token sequence does not match the latest checkpoint.")

                state = loaded.state
                if state.thread_status != "awaiting_approval":
                    raise ValueError("Thread is not awaiting approval.")

                now = datetime.now(timezone.utc)
                state.approval_state.status = decision_payload["status"]
                state.approval_state.decision_payload = decision_payload
                state.approval_state.resolved_at = now
                state.resume_metadata.last_resume_attempt_at = now
                state.resume_metadata.last_resumed_by = resumed_by
                state.thread_status = "running"

                resumed_state = self.graph_runner.resume(
                    state=state,
                    approval_decision=decision_payload,
                )

                self.checkpoint_manager.save_checkpoint(
                    state=resumed_state,
                    node_name=resumed_state.current_node,
                    is_interrupt_checkpoint=False,
                    conn=conn,
                )
                self.store.resolve_approval_task(
                    approval_task_id=token.approval_task_id,
                    status=decision_payload["status"],
                    decision_payload=decision_payload,
                    conn=conn,
                )
                conn.commit()
                return resumed_state
            except Exception:
                conn.rollback()
                raise
