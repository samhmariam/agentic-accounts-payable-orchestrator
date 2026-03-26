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
from aegisap.observability.context import WorkflowObservabilityContext
from aegisap.observability.langsmith_bridge import publish_langsmith_run
from aegisap.observability.tracing import (
    add_span_event,
    business_outcome_attributes,
    node_span_attributes,
    set_span_attributes,
    start_observability_span,
)


async def run_day4_explicit_planning_case(
    *,
    case_facts: CaseFacts,
    model: ModelClient,
    registry: TaskRegistry,
    observability_context: WorkflowObservabilityContext | None = None,
) -> WorkflowState:
    state = create_initial_workflow_state(
        case_facts,
        workflow_run_id=observability_context.workflow_run_id if observability_context else None,
        observability=observability_context.to_state_payload() if observability_context else None,
    )
    overlay = derive_policy_overlay(case_facts)
    state.planning.planner_input_snapshot = {
        "case_facts": case_facts.model_dump(),
        "policy_overlay": overlay.model_dump(),
    }

    try:
        with start_observability_span(
            "aegis.workflow.day4.plan",
            attributes=node_span_attributes(
                node_name="day4_plan",
                prompt_revision="day4",
                checkpoint_loaded=False,
                checkpoint_saved=False,
            ),
        ):
            raw_plan = await request_execution_plan_payload(
                model=model,
                case_facts=case_facts,
                policy_overlay=overlay,
            )
            plan = parse_execution_plan(raw_plan)
    except (ValueError, ValidationError) as exc:
        add_span_event(
            "policy_refusal",
            {
                "error_class": "planner_validation_failure",
                "attempt_number": 1,
                "backoff_ms": 0,
                "remaining_budget_ms": 0,
                "dependency_name": "planner",
                "decision_reason_code": "PLAN_REJECTED",
            },
        )
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

    with start_observability_span(
        "aegis.workflow.day4.execute",
        attributes=node_span_attributes(
            node_name="day4_execute",
            checkpoint_loaded=False,
            checkpoint_saved=False,
        ),
    ):
        post_execution_state = await execute_plan(state=state, plan=plan, registry=registry)

    gate_result = evaluate_recommendation_gate(post_execution_state, plan)
    if gate_result.eligible:
        post_execution_state.recommendation = compose_recommendation(post_execution_state, plan)
    else:
        post_execution_state.escalation_package = compose_escalation_package(post_execution_state, plan)
        add_span_event(
            "human_review_escalated",
            {
                "error_class": "manual_review_required",
                "attempt_number": 1,
                "backoff_ms": 0,
                "remaining_budget_ms": 0,
                "dependency_name": "workflow",
                "decision_reason_code": "NEEDS_HUMAN_REVIEW",
            },
        )

    set_span_attributes(
        business_outcome_attributes(
            recommendation_value_band=_value_band(case_facts.invoice_amount_gbp),
            vendor_risk_status=_task_output(post_execution_state, "vendor_history_check", "risk_level"),
            po_match_status=_task_output(post_execution_state, "po_match_verification", "po_match_status"),
            human_review_required=post_execution_state.escalation_package is not None,
            final_decision_type=(
                "recommendation_ready"
                if post_execution_state.recommendation is not None
                else "manual_review_required"
            ),
        )
    )
    if observability_context is not None:
        publish_langsmith_run(
            context=observability_context,
            name="aegis.workflow.day4",
            run_type="chain",
            inputs={"case_id_hash": observability_context.hashed_case_id},
            outputs={
                "recommendation_ready": post_execution_state.recommendation is not None,
                "plan_id": post_execution_state.planning.plan_id,
                "outcome": "recommendation_ready"
                if post_execution_state.recommendation is not None
                else "manual_review_required",
            },
            tags=["day4", "workflow"],
        )
    post_execution_state.observability = (
        observability_context.to_state_payload() if observability_context else state.observability
    )

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


def _task_output(state: WorkflowState, task_type: str, key: str) -> str | None:
    for entry in state.task_ledger:
        if entry.task_type == task_type and entry.outputs:
            value = entry.outputs.get(key)
            return None if value is None else str(value)
    return None


def _value_band(amount: float) -> str:
    if amount >= 40_000:
        return "very_high"
    if amount >= 25_000:
        return "high"
    if amount >= 10_000:
        return "medium"
    return "standard"
