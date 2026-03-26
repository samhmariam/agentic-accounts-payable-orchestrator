from __future__ import annotations

from pydantic import BaseModel, ConfigDict, ValidationError

from aegisap.day4.execution.task_contracts import get_task_contract

from .plan_schema import parse_execution_plan
from .plan_types import DerivedPolicyOverlay, ExecutionPlan, PlanTask

REQUIRED_GATE_KEYS = (
    "all_mandatory_tasks_completed",
    "required_evidence_present",
    "no_unresolved_blockers",
    "confidence_thresholds_met",
    "required_approvals_identified",
    "mandatory_escalations_resolved_or_triggered",
    "po_condition_satisfied",
    "bank_change_verification_satisfied",
    "approval_path_satisfied",
)


class ValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    valid: bool
    errors: list[str]


def validate_execution_plan(plan: ExecutionPlan | dict, overlay: DerivedPolicyOverlay) -> ValidationResult:
    errors: list[str] = []

    try:
        plan = parse_execution_plan(plan)
    except ValidationError as exc:
        for issue in exc.errors():
            loc = ".".join(str(part) for part in issue["loc"]) or "(root)"
            errors.append(f"schema: {loc} -> {issue['msg']}")
        return ValidationResult(valid=False, errors=errors)

    task_ids = [task.task_id for task in plan.tasks]
    duplicate_task_ids = _find_duplicates(task_ids)
    if duplicate_task_ids:
        errors.append(f"duplicate task ids: {', '.join(duplicate_task_ids)}")

    for task in plan.tasks:
        for dep in task.depends_on:
            if dep not in task_ids:
                errors.append(f"task {task.task_id} depends on unknown task {dep}")

    cycle_error = _detect_cycle(plan)
    if cycle_error:
        errors.append(cycle_error)

    task_types = {task.task_type for task in plan.tasks}
    for mandatory_type in overlay.mandatory_task_types:
        if mandatory_type not in task_types:
            errors.append(f"missing mandatory task type: {mandatory_type}")

    for precondition in overlay.global_preconditions:
        if precondition not in plan.global_preconditions:
            errors.append(f"missing global precondition: {precondition}")

    for stop_condition in overlay.global_stop_conditions:
        if stop_condition not in plan.global_stop_conditions:
            errors.append(f"missing global stop condition: {stop_condition}")

    for trigger in overlay.escalation_triggers:
        if trigger not in plan.escalation_triggers:
            errors.append(f"missing escalation trigger: {trigger}")

    for approval in overlay.required_approvals:
        if approval not in plan.required_approvals:
            errors.append(f"missing required approval: {approval}")

    if plan.escalation_route != overlay.escalation_route and overlay.mandatory_task_types.count("manual_escalation_package"):
        errors.append("escalation route must match policy overlay for mandatory escalation cases")

    if not plan.escalation_reason_template.strip():
        errors.append("escalation_reason_template must be populated")

    gate_dict = plan.recommendation_gate.model_dump()
    for gate_key in REQUIRED_GATE_KEYS:
        if gate_key not in gate_dict:
            errors.append(f"recommendation gate missing key: {gate_key}")

    if plan.action_classification.irreversible_actions_allowed:
        errors.append("irreversible_actions_allowed must remain false at planning time")

    for task in plan.tasks:
        errors.extend(_validate_task_contract(task))

    high_risk_task = next((task for task in plan.tasks if task.task_type == "vendor_bank_verification"), None)
    if high_risk_task and high_risk_task.on_failure != "escalate":
        errors.append("vendor_bank_verification must escalate on failure")

    for task in plan.tasks:
        if task.task_type in {"po_match_verification", "po_waiver_check", "vendor_bank_verification"} and not task.stop_if_missing:
            errors.append(f"{task.task_type} must set stop_if_missing=true")

    if "manual_escalation_package" in overlay.mandatory_task_types:
        if "combined_risk_requires_escalation" not in overlay.recommendation_blocks and "manual_review_required" not in overlay.recommendation_blocks:
            errors.append("overlay recommendation blocks must encode manual escalation scenarios")

    return ValidationResult(valid=not errors, errors=errors)


def _validate_task_contract(task: PlanTask) -> list[str]:
    errors: list[str] = []
    contract = get_task_contract(task.task_type)

    if task.owner_agent != contract.owner_agent:
        errors.append(f"task {task.task_id} owner must be {contract.owner_agent}")

    for field_name in contract.expected_output_fields:
        if field_name not in task.expected_outputs:
            errors.append(f"task {task.task_id} missing expected output: {field_name}")

    if task.action_class == "irreversible":
        errors.append(f"task {task.task_id} must remain reversible in day4")

    return errors


def _find_duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def _detect_cycle(plan: ExecutionPlan) -> str | None:
    graph = {task.task_id: task.depends_on for task in plan.tasks}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False

        visiting.add(node)
        for dep in graph.get(node, []):
            if visit(dep):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    for task_id in graph:
        if visit(task_id):
            return f"dependency cycle detected involving task {task_id}"
    return None
