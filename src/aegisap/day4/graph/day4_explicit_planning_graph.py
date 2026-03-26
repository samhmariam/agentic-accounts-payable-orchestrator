from __future__ import annotations

from pydantic import ValidationError

from aegisap.day4.execution.plan_executor import execute_plan
from aegisap.day4.execution.task_registry import TaskRegistry
from aegisap.day4.planning.plan_schema import parse_execution_plan
from aegisap.day4.planning.plan_types import CaseFacts, ExecutionPlan
from aegisap.day4.planning.plan_validator import validate_execution_plan
from aegisap.day4.planning.planner_agent import ModelClient, request_execution_plan_payload
from aegisap.day4.planning.policy_overlay import derive_policy_overlay
from aegisap.day4.recommendation.escalation_composer import compose_escalation_package
from aegisap.day4.recommendation.recommendation_composer import compose_recommendation
from aegisap.day4.recommendation.recommendation_gate import evaluate_recommendation_gate
from aegisap.day4.state.workflow_state import WorkflowState, create_initial_workflow_state


async def run_day4_explicit_planning_case(
    *,
    case_facts: CaseFacts,
    model: ModelClient,
    registry: TaskRegistry,
) -> WorkflowState:
    state = create_initial_workflow_state(case_facts)
    overlay = derive_policy_overlay(case_facts)
    state.planning.planner_input_snapshot = {
        "case_facts": case_facts.model_dump(),
        "policy_overlay": overlay.model_dump(),
    }

    try:
        raw_plan = await request_execution_plan_payload(
            model=model,
            case_facts=case_facts,
            policy_overlay=overlay,
        )
        plan = parse_execution_plan(raw_plan)
    except (ValueError, ValidationError) as exc:
        _reject_plan(
            state=state,
            case_id=case_facts.case_id,
            plan_id=None,
            reasons=[_stringify_error(exc)],
        )
        return state

    state.plan = plan
    state.planning.plan_id = plan.plan_id
    state.planning.plan_status = "created"
    state.eligibility.required_approvals = plan.required_approvals[:]

    validation = validate_execution_plan(plan, overlay)
    if not validation.valid:
        _reject_plan(
            state=state,
            case_id=plan.case_id,
            plan_id=plan.plan_id,
            reasons=validation.errors,
        )
        return state

    state.planning.plan_status = "validated"
    state.planning.validated = True

    post_execution_state = await execute_plan(state=state, plan=plan, registry=registry)

    gate_result = evaluate_recommendation_gate(post_execution_state, plan)
    if gate_result.eligible:
        post_execution_state.recommendation = compose_recommendation(post_execution_state, plan)
    else:
        post_execution_state.escalation_package = compose_escalation_package(post_execution_state, plan)

    return post_execution_state


def _reject_plan(
    *,
    state: WorkflowState,
    case_id: str,
    plan_id: str | None,
    reasons: list[str],
) -> None:
    unique_reasons = list(dict.fromkeys(reasons))
    state.planning.plan_status = "rejected"
    state.planning.validated = False
    state.planning.validation_errors = unique_reasons
    state.planning.escalation_status = "triggered"
    state.eligibility.blocking_conditions.extend(unique_reasons)
    state.eligibility.recommendation_allowed = False
    state.eligibility.irreversible_actions_allowed = False
    state.escalation_package = {
        "case_id": case_id,
        "plan_id": plan_id,
        "status": "plan_rejected",
        "reasons": unique_reasons,
    }


def _stringify_error(error: ValueError | ValidationError) -> str:
    if isinstance(error, ValidationError):
        return "; ".join(
            f"{'.'.join(str(part) for part in issue['loc']) or '(root)'} -> {issue['msg']}"
            for issue in error.errors()
        )
    return str(error)
