from __future__ import annotations

from datetime import datetime, timezone

from aegisap.day4.planning.plan_types import PlanTask
from aegisap.day4.state.workflow_state import WorkflowState as Day4WorkflowState
from aegisap.day5.state.checksum import compute_payload_checksum
from aegisap.day5.state.durable_models import (
    ApprovalState,
    DurableWorkflowState,
    EvidenceSnapshot,
    HistoryMessage,
    ToolExecutionRecord,
)


def bootstrap_durable_state_from_day4(
    day4_state: Day4WorkflowState,
    *,
    thread_id: str,
    workflow_name: str = "payment_recommendation_workflow",
    now: datetime | None = None,
) -> DurableWorkflowState:
    handoff_time = now or datetime.now(timezone.utc)
    current_node, thread_status, approval_state = _derive_handoff_status(day4_state, handoff_time)
    evidence_snapshots, tool_execution_records = _build_execution_snapshots(day4_state, handoff_time)
    required_approvals = _required_approvals(day4_state)

    return DurableWorkflowState(
        thread_id=thread_id,
        case_id=day4_state.case_facts.case_id,
        workflow_name=workflow_name,
        current_node=current_node,
        thread_status=thread_status,
        plan_version=day4_state.planning.plan_version or "day4",
        execution_plan=day4_state.plan.model_dump(mode="json") if day4_state.plan is not None else {},
        canonical_invoice=day4_state.case_facts.model_dump(mode="json"),
        payment_recommendation=day4_state.recommendation,
        escalation_package=day4_state.escalation_package,
        approval_state=approval_state,
        evidence_snapshots=evidence_snapshots,
        tool_execution_records=tool_execution_records,
        history_state={
            "raw_messages": [
                HistoryMessage(
                    role="system",
                    content="State handed off from Day 4 explicit planning workflow.",
                    created_at=handoff_time,
                    metadata={
                        "source": "day4",
                        "plan_id": day4_state.plan.plan_id if day4_state.plan is not None else None,
                        "required_approvals": required_approvals,
                    },
                )
            ],
            "summary_blocks": [],
            "retained_window_size": 12,
        },
        created_at=handoff_time,
        updated_at=handoff_time,
    )


def _derive_handoff_status(
    day4_state: Day4WorkflowState,
    handoff_time: datetime,
) -> tuple[str, str, ApprovalState]:
    required_approvals = _required_approvals(day4_state)

    if day4_state.recommendation is not None and required_approvals:
        return (
            "await_controller_approval",
            "awaiting_approval",
            ApprovalState(
                status="pending",
                requested_at=handoff_time,
            ),
        )

    if day4_state.escalation_package is not None:
        return (
            "manual_review_required",
            "resumable",
            ApprovalState(status="not_requested"),
        )

    if day4_state.recommendation is not None:
        return (
            "day4_completed",
            "completed",
            ApprovalState(status="not_requested"),
        )

    return (
        "day4_handoff",
        "running",
        ApprovalState(status="not_requested"),
    )


def _build_execution_snapshots(
    day4_state: Day4WorkflowState,
    handoff_time: datetime,
) -> tuple[list[EvidenceSnapshot], list[ToolExecutionRecord]]:
    evidence_snapshots: list[EvidenceSnapshot] = []
    tool_execution_records: list[ToolExecutionRecord] = []
    tasks_by_id = {
        task.task_id: task
        for task in (day4_state.plan.tasks if day4_state.plan is not None else [])
    }

    for entry in day4_state.task_ledger:
        task = tasks_by_id.get(entry.task_id)
        artifact = day4_state.artifacts.get(entry.task_id, {})
        if entry.status in {"pending", "skipped"} and not artifact:
            continue

        executed_at = _parse_timestamp(entry.completed_at or entry.started_at, handoff_time)
        outputs = entry.outputs or {}
        artifact_payload = {
            "task_type": entry.task_type,
            "status": entry.status,
            "outputs": outputs,
            "artifact": artifact,
        }
        snapshot_id = f"day4:{entry.task_id}"

        evidence_snapshots.append(
            EvidenceSnapshot(
                evidence_id=snapshot_id,
                source_type="tool",
                source_ref=entry.task_id,
                captured_at=executed_at,
                payload=artifact_payload,
                payload_hash=compute_payload_checksum(artifact_payload),
                replay_safe=False,
            )
        )

        tool_execution_records.append(
            ToolExecutionRecord(
                tool_name=entry.task_type,
                tool_call_id=entry.task_id,
                executed_at=executed_at,
                input_hash=compute_payload_checksum(_task_input_payload(task)),
                output_hash=compute_payload_checksum(outputs),
                deterministic=False,
                replay_safe=False,
                evidence_snapshot_id=snapshot_id,
            )
        )

    return evidence_snapshots, tool_execution_records


def _task_input_payload(task: PlanTask | None) -> dict:
    if task is None:
        return {}
    return {
        "depends_on": task.depends_on,
        "inputs": task.inputs,
        "required_evidence": task.required_evidence,
        "expected_outputs": task.expected_outputs,
        "preconditions": task.preconditions,
    }


def _required_approvals(day4_state: Day4WorkflowState) -> list[str]:
    approvals = day4_state.eligibility.required_approvals[:]
    if day4_state.plan is not None:
        approvals.extend(day4_state.plan.required_approvals)
    return list(dict.fromkeys(approvals))


def _parse_timestamp(timestamp: str | None, fallback: datetime) -> datetime:
    if not timestamp:
        return fallback
    return datetime.fromisoformat(timestamp)
