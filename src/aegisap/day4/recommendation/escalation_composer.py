from __future__ import annotations

from aegisap.day4.planning.plan_types import ExecutionPlan
from aegisap.day4.state.workflow_state import WorkflowState


def compose_escalation_package(state: WorkflowState, plan: ExecutionPlan) -> dict:
    reasons = state.recommendation_gate_result.reasons if state.recommendation_gate_result else []
    return {
        "case_id": plan.case_id,
        "plan_id": plan.plan_id,
        "status": "manual_review_required",
        "escalation_triggers": plan.escalation_triggers,
        "escalation_route": plan.escalation_route.model_dump(),
        "escalation_reason_template": plan.escalation_reason_template,
        "blocking_conditions": list(dict.fromkeys(state.eligibility.blocking_conditions)),
        "unmet_preconditions": list(dict.fromkeys(state.eligibility.unmet_preconditions)),
        "missing_evidence": list(dict.fromkeys(state.eligibility.missing_evidence)),
        "required_approvals": plan.required_approvals,
        "gate_reasons": reasons,
        "task_summary": [
            {
                "task_id": entry.task_id,
                "task_type": entry.task_type,
                "status": entry.status,
                "blocking_reason": entry.blocking_reason,
            }
            for entry in state.task_ledger
        ],
    }
