from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone

import pytest

from aegisap.day5.state.durable_models import ApprovalState, DurableWorkflowState
from aegisap.day5.workflow.checkpoint_manager import CheckpointValidationError
from aegisap.day5.workflow.resume_service import ResumeService, ResumeTokenCodec


class FakeConnection:
    def __init__(self) -> None:
        self.on_commit: list = []
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        for action in self.on_commit:
            action()
        self.committed = True
        self.on_commit.clear()

    def rollback(self) -> None:
        self.rolled_back = True
        self.on_commit.clear()


class FakeStore:
    def __init__(self) -> None:
        self.approval_task = {
            "approval_task_id": "task-1",
            "thread_id": "thread-1",
            "checkpoint_id": "cp-1",
            "status": "pending",
            "assigned_to": "controller@shewit.co.uk",
            "decision_payload": None,
        }
        self.resolved = None
        self.last_connection: FakeConnection | None = None

    @contextmanager
    def connection(self):
        conn = FakeConnection()
        self.last_connection = conn
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise

    def get_approval_task(self, approval_task_id: str, *, conn=None):
        if approval_task_id != "task-1":
            return None

        task = self.approval_task

        class Task:
            approval_task_id = task["approval_task_id"]
            thread_id = task["thread_id"]
            checkpoint_id = task["checkpoint_id"]
            status = task["status"]
            assigned_to = task["assigned_to"]
            decision_payload = task["decision_payload"]

        return Task()

    def resolve_approval_task(self, *, approval_task_id: str, status: str, decision_payload: dict, conn=None):
        def apply() -> None:
            self.approval_task["status"] = status
            self.approval_task["decision_payload"] = decision_payload
            self.resolved = {
                "approval_task_id": approval_task_id,
                "status": status,
                "decision_payload": decision_payload,
            }

        if conn is not None:
            conn.on_commit.append(apply)
        else:
            apply()


class FakeCheckpointManager:
    def __init__(self, state: DurableWorkflowState) -> None:
        self.state = state
        self.saved = None
        self.fail_on_save = False

    def load_latest_checkpoint(self, thread_id: str, *, conn=None):
        class Loaded:
            checkpoint_id = "cp-1"
            is_interrupt_checkpoint = True

            def __init__(self, state: DurableWorkflowState):
                self.state = state

        return Loaded(self.state)

    def save_checkpoint(
        self,
        *,
        state: DurableWorkflowState,
        node_name: str,
        is_interrupt_checkpoint: bool = False,
        history_summary_json=None,
        conn=None,
    ):
        if self.fail_on_save:
            raise RuntimeError("checkpoint write failed")

        def apply() -> None:
            self.saved = {
                "state": state,
                "node_name": node_name,
                "is_interrupt_checkpoint": is_interrupt_checkpoint,
            }

        if conn is not None:
            conn.on_commit.append(apply)
        else:
            apply()

        return "cp-2"


class FakeGraphRunner:
    def __init__(self, *, should_fail: bool = False) -> None:
        self.should_fail = should_fail

    def resume(self, *, state: DurableWorkflowState, approval_decision: dict):
        if self.should_fail:
            raise RuntimeError("resume failed")

        state.current_node = "post_approval_router"
        state.payment_recommendation = {
            "status": "approved_to_continue",
            "approval_comment": approval_decision.get("comment"),
        }
        return state


def build_state() -> DurableWorkflowState:
    now = datetime.now(timezone.utc)
    return DurableWorkflowState(
        workflow_run_id="wf-1",
        thread_id="thread-1",
        case_id="case-1",
        observability={"workflow_run_id": "wf-1", "trace_id": "trace-1"},
        checkpoint_seq=1,
        current_node="await_controller_approval",
        thread_status="awaiting_approval",
        approval_state=ApprovalState(
            status="pending",
            approval_task_id="task-1",
            assigned_to="controller@shewit.co.uk",
            requested_at=now,
        ),
        created_at=now,
        updated_at=now,
    )


def build_service(*, graph_runner: FakeGraphRunner | None = None):
    state = build_state()
    store = FakeStore()
    checkpoint_manager = FakeCheckpointManager(state)
    service = ResumeService(
        store=store,  # type: ignore[arg-type]
        checkpoint_manager=checkpoint_manager,  # type: ignore[arg-type]
        graph_runner=graph_runner or FakeGraphRunner(),
        token_codec=ResumeTokenCodec("test-secret"),
    )
    token = service.create_resume_token(
        thread_id="thread-1",
        checkpoint_id="cp-1",
        checkpoint_seq=1,
        approval_task_id="task-1",
    )
    return service, store, checkpoint_manager, token


def test_resume_from_pending_approval_uses_latest_checkpoint_state() -> None:
    service, store, checkpoint_manager, token = build_service()

    resumed = service.resume_after_approval(
        resume_token=token,
        decision_payload={"status": "approved", "comment": "Looks good."},
        resumed_by="controller@shewit.co.uk",
    )

    assert resumed.approval_state.status == "approved"
    assert resumed.current_node == "post_approval_router"
    assert resumed.payment_recommendation is not None
    assert store.resolved["status"] == "approved"
    assert checkpoint_manager.saved["node_name"] == "post_approval_router"
    assert store.last_connection is not None
    assert store.last_connection.committed is True


def test_resume_rolls_back_when_graph_resume_fails() -> None:
    service, store, checkpoint_manager, token = build_service(
        graph_runner=FakeGraphRunner(should_fail=True)
    )

    with pytest.raises(RuntimeError, match="resume failed"):
        service.resume_after_approval(
            resume_token=token,
            decision_payload={"status": "approved", "comment": "Looks good."},
            resumed_by="controller@shewit.co.uk",
        )

    assert store.approval_task["status"] == "pending"
    assert store.resolved is None
    assert checkpoint_manager.saved is None
    assert store.last_connection is not None
    assert store.last_connection.rolled_back is True


def test_resume_rolls_back_when_checkpoint_save_fails() -> None:
    service, store, checkpoint_manager, token = build_service()
    checkpoint_manager.fail_on_save = True

    with pytest.raises(RuntimeError, match="checkpoint write failed"):
        service.resume_after_approval(
            resume_token=token,
            decision_payload={"status": "approved", "comment": "Looks good."},
            resumed_by="controller@shewit.co.uk",
        )

    assert store.approval_task["status"] == "pending"
    assert store.resolved is None
    assert checkpoint_manager.saved is None
    assert store.last_connection is not None
    assert store.last_connection.rolled_back is True


def test_resume_rejects_task_bound_to_different_checkpoint() -> None:
    service, store, _checkpoint_manager, token = build_service()
    store.approval_task["checkpoint_id"] = "cp-2"

    with pytest.raises(CheckpointValidationError, match="not bound"):
        service.resume_after_approval(
            resume_token=token,
            decision_payload={"status": "approved", "comment": "Looks good."},
            resumed_by="controller@shewit.co.uk",
        )

    assert store.approval_task["status"] == "pending"
