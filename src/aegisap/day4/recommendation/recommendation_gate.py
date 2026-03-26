from __future__ import annotations

from aegisap.day4.planning.plan_types import ExecutionPlan, RecommendationGateResult
from aegisap.day4.state.workflow_state import WorkflowState


def evaluate_recommendation_gate(state: WorkflowState, plan: ExecutionPlan) -> RecommendationGateResult:
    reasons: list[str] = []

    completed_task_types = {entry.task_type for entry in state.task_ledger if entry.status == "completed"}
    mandatory_task_types = {task.task_type for task in plan.tasks}

    for task_type in mandatory_task_types:
        if task_type not in completed_task_types:
            reasons.append(f"mandatory task not completed: {task_type}")

    if state.eligibility.missing_evidence:
        reasons.extend(f"missing evidence: {name}" for name in state.eligibility.missing_evidence)

    for task in plan.tasks:
        entry = next((item for item in state.task_ledger if item.task_id == task.task_id), None)
        if entry and entry.confidence is not None and entry.confidence < task.min_confidence:
            reasons.append(f"confidence below threshold: {task.task_type}")

    po_satisfied = _po_condition_satisfied(state)
    if "po_verified_or_waived" in plan.global_preconditions and not po_satisfied:
        reasons.append("po condition unsatisfied")

    bank_satisfied = _bank_condition_satisfied(state)
    if "bank_change_authoritatively_verified" in plan.global_preconditions and not bank_satisfied:
        reasons.append("bank change not authoritatively verified")

    approval_satisfied = _approval_path_satisfied(state)
    if "approval_route_defined_for_threshold_case" in plan.global_preconditions and not approval_satisfied:
        reasons.append("approval path not defined")

    if plan.required_approvals and not state.eligibility.required_approvals:
        reasons.append("required approvals not identified")

    if state.eligibility.unmet_preconditions:
        reasons.extend(f"unmet precondition: {name}" for name in state.eligibility.unmet_preconditions)

    if state.eligibility.blocking_conditions:
        reasons.extend(state.eligibility.blocking_conditions)

    forced_manual_review_conditions = {
        "missing_po_and_bank_change_require_manual_review",
        "combined_risk_requires_manual_review",
    }
    for condition in plan.global_stop_conditions:
        if condition in forced_manual_review_conditions:
            reasons.append(condition)
        elif condition == "missing_required_po_evidence" and not po_satisfied:
            reasons.append(condition)
        elif condition == "unverified_bank_change" and not bank_satisfied:
            reasons.append(condition)
        elif condition == "approval_not_obtained_for_high_value_case" and not approval_satisfied:
            reasons.append(condition)

    if "manual_escalation_package" in mandatory_task_types:
        manual_task = next((entry for entry in state.task_ledger if entry.task_type == "manual_escalation_package"), None)
        if manual_task is None or manual_task.status != "completed":
            reasons.append("mandatory escalation not completed")
        reasons.append("manual escalation package present in plan")

    if state.planning.escalation_status == "triggered":
        reasons.append("escalation triggered")

    unique_reasons = list(dict.fromkeys(reasons))
    eligible = not unique_reasons

    state.eligibility.recommendation_allowed = eligible
    state.eligibility.irreversible_actions_allowed = False
    state.recommendation_gate_result = RecommendationGateResult(eligible=eligible, reasons=unique_reasons)

    return state.recommendation_gate_result


def _po_condition_satisfied(state: WorkflowState) -> bool:
    po_entry = next((item for item in state.task_ledger if item.task_type == "po_match_verification"), None)
    waiver_entry = next((item for item in state.task_ledger if item.task_type == "po_waiver_check"), None)
    po_passed = bool(po_entry and po_entry.outputs and po_entry.outputs.get("po_match_status") == "pass")
    waiver_present = bool(waiver_entry and waiver_entry.outputs and waiver_entry.outputs.get("waiver_present") is True)
    return po_passed or waiver_present


def _bank_condition_satisfied(state: WorkflowState) -> bool:
    if not state.case_facts.bank_details_changed:
        return True
    bank_entry = next((item for item in state.task_ledger if item.task_type == "vendor_bank_verification"), None)
    return bool(bank_entry and bank_entry.outputs and bank_entry.outputs.get("bank_change_verified") is True)


def _approval_path_satisfied(state: WorkflowState) -> bool:
    approval_entry = next((item for item in state.task_ledger if item.task_type == "threshold_approval_check"), None)
    if approval_entry is None:
        return not state.eligibility.required_approvals
    return bool(approval_entry.outputs and approval_entry.outputs.get("approval_path_defined") is True)
