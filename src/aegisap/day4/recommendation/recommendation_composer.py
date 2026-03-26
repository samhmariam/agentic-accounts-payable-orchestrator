from __future__ import annotations

from aegisap.day4.planning.plan_types import ExecutionPlan
from aegisap.day4.state.workflow_state import WorkflowState


def compose_recommendation(state: WorkflowState, plan: ExecutionPlan) -> dict:
    if not state.recommendation_gate_result or not state.recommendation_gate_result.eligible:
        raise ValueError("recommendation_cannot_be_composed_before_gate_passes")

    draft_entry = next((entry for entry in state.task_ledger if entry.task_type == "payment_recommendation_draft"), None)
    draft_payload = draft_entry.outputs.get("recommendation_draft") if draft_entry and draft_entry.outputs else None

    return {
        "case_id": plan.case_id,
        "plan_id": plan.plan_id,
        "status": "recommendation_ready",
        "message": "All mandatory Day 4 planning and verification conditions have passed.",
        "completed_tasks": [entry.task_id for entry in state.task_ledger if entry.status == "completed"],
        "required_approvals": plan.required_approvals,
        "irreversible_actions_allowed": False,
        "draft": draft_payload,
    }
