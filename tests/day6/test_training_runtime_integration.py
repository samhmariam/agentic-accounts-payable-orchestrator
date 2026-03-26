from __future__ import annotations

import asyncio
from contextlib import contextmanager

from aegisap.day4.execution.task_registry import create_default_task_registry
from aegisap.day4.graph.day4_explicit_planning_graph import run_day4_explicit_planning_case
from aegisap.day4.planning.plan_types import CaseFacts
from aegisap.training.day4_plans import build_training_plan
from aegisap.training.fixtures import golden_thread_path
from aegisap.training.labs import StaticPlanModel, load_case_facts
from aegisap.training.postgres import apply_migration_path
from aegisap.day5.workflow.training_runtime import create_day5_pause


class FakeConnection:
    def __init__(self) -> None:
        self.on_commit: list = []

    def cursor(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, _statement: str, _params=None) -> None:
        return None

    def fetchone(self):
        return None

    def commit(self) -> None:
        for action in self.on_commit:
            action()
        self.on_commit.clear()


class FakeStore:
    def __init__(self) -> None:
        self.threads: dict[str, dict] = {}
        self.checkpoints: dict[str, dict] = {}
        self.approval_tasks: dict[str, dict] = {}
        self.review_tasks: dict[str, dict] = {}

    @contextmanager
    def connection(self):
        conn = FakeConnection()
        yield conn
        conn.commit()

    def create_thread(self, *, thread_id: str, case_id: str, workflow_name: str, status: str, state_schema_version: int, conn=None) -> None:
        def apply() -> None:
            self.threads[thread_id] = {
                "case_id": case_id,
                "workflow_name": workflow_name,
                "status": status,
                "state_schema_version": state_schema_version,
            }

        if conn is not None:
            conn.on_commit.append(apply)
        else:
            apply()

    def insert_checkpoint(self, *, thread_id: str, node_name: str, checkpoint_seq: int, state, state_checksum: str, history_summary_json=None, is_interrupt_checkpoint: bool = False, checkpoint_id: str | None = None, conn=None) -> str:
        checkpoint_id = checkpoint_id or f"cp-{checkpoint_seq}"

        def apply() -> None:
            self.checkpoints[checkpoint_id] = {
                "thread_id": thread_id,
                "node_name": node_name,
                "checkpoint_seq": checkpoint_seq,
                "state": state.model_dump(mode="json"),
                "state_checksum": state_checksum,
                "is_interrupt_checkpoint": is_interrupt_checkpoint,
            }

        if conn is not None:
            conn.on_commit.append(apply)
        else:
            apply()
        return checkpoint_id

    def create_approval_task(self, *, thread_id: str, checkpoint_id: str, assigned_to: str | None, due_at: str | None = None, approval_task_id: str | None = None, conn=None) -> str:
        approval_task_id = approval_task_id or "approval-task"

        def apply() -> None:
            self.approval_tasks[approval_task_id] = {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
                "assigned_to": assigned_to,
            }

        if conn is not None:
            conn.on_commit.append(apply)
        else:
            apply()
        return approval_task_id

    def create_review_task(self, *, thread_id: str, checkpoint_id: str, assigned_to: str | None, review_task_id: str | None = None, conn=None) -> str:
        review_task_id = review_task_id or "review-task"

        def apply() -> None:
            self.review_tasks[review_task_id] = {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
                "assigned_to": assigned_to,
            }

        if conn is not None:
            conn.on_commit.append(apply)
        else:
            apply()
        return review_task_id


def _run_day4(case_facts: CaseFacts):
    plan = build_training_plan(case_facts, plan_id=f"plan_{case_facts.case_id}")
    return asyncio.run(
        run_day4_explicit_planning_case(
            case_facts=case_facts,
            model=StaticPlanModel(plan),
            registry=create_default_task_registry(),
        )
    )


def test_create_day5_pause_routes_clean_case_into_controller_approval() -> None:
    state = _run_day4(load_case_facts(golden_thread_path("day4_case.json")))
    store = FakeStore()

    pause = create_day5_pause(
        day4_state=state,
        thread_id="thread-day6-clean",
        assigned_to="controller@example.com",
        store=store,  # type: ignore[arg-type]
        token_secret="test-secret",
    )

    assert pause["review_outcome"]["outcome"] == "approved_to_proceed"
    assert pause["approval_task_id"] is not None
    assert pause["review_task_id"] is None
    assert pause["resume_token"] is not None


def test_create_day5_pause_routes_manual_review_case_to_review_task() -> None:
    case_facts = load_case_facts(golden_thread_path("day4_case.json")).model_copy(
        update={
            "po_present": False,
            "po_number": None,
            "retrieved_evidence_ids": ["supplier_master:VEND-001"],
        }
    )
    state = _run_day4(case_facts)
    store = FakeStore()

    pause = create_day5_pause(
        day4_state=state,
        thread_id="thread-day6-manual-review",
        assigned_to="finance-controller@example.com",
        store=store,  # type: ignore[arg-type]
        token_secret="test-secret",
    )

    assert pause["review_outcome"]["outcome"] == "needs_human_review"
    assert pause["approval_task_id"] is None
    assert pause["review_task_id"] is not None
    assert pause["resume_token"] is None


def test_apply_migration_path_runs_all_sql_files(monkeypatch, tmp_path) -> None:
    applied: list[str] = []

    monkeypatch.setattr(
        "aegisap.training.postgres.apply_migration_file",
        lambda path: applied.append(str(path)),
    )
    (tmp_path / "001.sql").write_text("SELECT 1;", encoding="utf-8")
    (tmp_path / "002.sql").write_text("SELECT 2;", encoding="utf-8")

    result = apply_migration_path(tmp_path)

    assert [path.name for path in result] == ["001.sql", "002.sql"]
    assert applied == [str(tmp_path / "001.sql"), str(tmp_path / "002.sql")]
