from __future__ import annotations

import asyncio
import json
from pathlib import Path

from aegisap.common.paths import repo_root
from aegisap.day4.execution.plan_executor import execute_plan
from aegisap.day4.execution.task_contracts import get_task_contract
from aegisap.day4.execution.task_registry import create_default_task_registry
from aegisap.day4.planning.plan_types import (
    ActionClassification,
    CaseFacts,
    ExecutionPlan,
    PlanTask,
    RecommendationGate,
)
from aegisap.day4.planning.policy_overlay import derive_policy_overlay
from aegisap.day4.recommendation.escalation_composer import compose_escalation_package
from aegisap.day4.recommendation.recommendation_composer import compose_recommendation
from aegisap.day4.recommendation.recommendation_gate import evaluate_recommendation_gate
from aegisap.day4.state.workflow_state import create_initial_workflow_state
from aegisap.day5.workflow.day4_handoff import bootstrap_durable_state_from_day4


def _fixture_path(name: str) -> Path:
    return repo_root(__file__) / "fixtures" / "day4" / f"{name}.json"


def load_case_facts(name: str) -> CaseFacts:
    payload = json.loads(_fixture_path(name).read_text(encoding="utf-8"))
    return CaseFacts.model_validate(payload["case_facts"])


def build_safe_plan(case_facts: CaseFacts, *, plan_id: str) -> ExecutionPlan:
    overlay = derive_policy_overlay(case_facts)
    tasks: list[PlanTask] = []
    completed_dependencies: list[str] = []

    for task_type in overlay.mandatory_task_types:
        contract = get_task_contract(task_type)
        task_id = task_type

        if task_type == "policy_retrieval":
            depends_on: list[str] = []
        elif task_type == "manual_escalation_package":
            depends_on = []
        elif task_type == "payment_recommendation_draft":
            depends_on = [task.task_id for task in tasks if task.task_type != "manual_escalation_package"]
        else:
            depends_on = ["policy_retrieval"] if "policy_retrieval" in completed_dependencies else []

        tasks.append(
            PlanTask(
                task_id=task_id,
                task_type=task_type,
                owner_agent=contract.owner_agent,
                depends_on=depends_on,
                inputs={"case_id": case_facts.case_id, "invoice_id": case_facts.invoice_id},
                required_evidence=_required_evidence(task_type),
                expected_outputs=contract.expected_output_fields,
                preconditions=[],
                stop_if_missing=task_type in {
                    "po_match_verification",
                    "po_waiver_check",
                    "vendor_bank_verification",
                },
                min_confidence=0.9 if task_type in {"po_match_verification", "vendor_bank_verification"} else 0.8,
                on_failure="escalate" if task_type in {"vendor_bank_verification", "manual_escalation_package"} else "block",
                action_class="reversible",
            )
        )
        completed_dependencies.append(task_id)

    return ExecutionPlan(
        plan_id=plan_id,
        case_id=case_facts.case_id,
        goal="Determine whether payment recommendation is eligible",
        case_risk_flags=overlay.risk_flags,
        planning_rationale="Deterministic test plan aligned to the policy overlay.",
        tasks=tasks,
        global_preconditions=overlay.global_preconditions,
        global_stop_conditions=overlay.global_stop_conditions,
        escalation_triggers=overlay.escalation_triggers,
        escalation_route=overlay.escalation_route,
        escalation_reason_template=overlay.escalation_reason_template,
        required_approvals=overlay.required_approvals,
        recommendation_gate=RecommendationGate(
            all_mandatory_tasks_completed=True,
            required_evidence_present=True,
            no_unresolved_blockers=True,
            confidence_thresholds_met=True,
            required_approvals_identified=True,
            mandatory_escalations_resolved_or_triggered=True,
            po_condition_satisfied=True,
            bank_change_verification_satisfied=True,
            approval_path_satisfied=True,
        ),
        action_classification=ActionClassification(
            current_stage="reversible",
            irreversible_actions_allowed=False,
        ),
    )


def _required_evidence(task_type: str) -> list[str]:
    mapping = {
        "policy_retrieval": ["policy:controls"],
        "po_match_verification": ["po_number"],
        "po_waiver_check": ["po_waiver"],
        "vendor_history_check": ["supplier_master_record"],
        "vendor_bank_verification": ["supplier_master_record", "bank_change_request_evidence"],
        "threshold_approval_check": ["policy:approval-thresholds"],
        "manual_escalation_package": ["case_summary"],
        "payment_recommendation_draft": [],
    }
    return mapping[task_type]


def test_day4_recommendation_handoff_preserves_plan_and_enters_approval_pause() -> None:
    case_facts = load_case_facts("clean_path").model_copy(
        update={
            "invoice_amount_gbp": 45_000.0,
            "amount_approval_threshold_gbp": 25_000.0,
            "controller_approval_threshold_gbp": 40_000.0,
        }
    )
    plan = build_safe_plan(case_facts, plan_id="plan_day4_high_value_clean")
    state = create_initial_workflow_state(case_facts)
    state.plan = plan

    result = asyncio.run(execute_plan(state=state, plan=plan, registry=create_default_task_registry()))
    gate_result = evaluate_recommendation_gate(result, plan)
    assert gate_result.eligible is True
    result.recommendation = compose_recommendation(result, plan)

    durable = bootstrap_durable_state_from_day4(result, thread_id="thread-clean-approval")

    assert durable.thread_id == "thread-clean-approval"
    assert durable.case_id == case_facts.case_id
    assert durable.thread_status == "awaiting_approval"
    assert durable.current_node == "await_controller_approval"
    assert durable.approval_state.status == "pending"
    assert durable.plan_version == "day4"
    assert durable.execution_plan["plan_id"] == "plan_day4_high_value_clean"
    assert set(durable.execution_plan["required_approvals"]) == {"ap_manager", "controller"}
    assert durable.payment_recommendation is not None
    assert durable.payment_recommendation["plan_id"] == "plan_day4_high_value_clean"
    assert durable.escalation_package is None
    assert any(record.tool_name == "threshold_approval_check" for record in durable.tool_execution_records)
    assert any(snapshot.source_ref == "payment_recommendation_draft" for snapshot in durable.evidence_snapshots)


def test_day4_manual_review_handoff_preserves_escalation_package() -> None:
    case_facts = load_case_facts("bank_change")
    plan = build_safe_plan(case_facts, plan_id="plan_day4_bank_change")
    state = create_initial_workflow_state(case_facts)
    state.plan = plan

    result = asyncio.run(execute_plan(state=state, plan=plan, registry=create_default_task_registry()))
    gate_result = evaluate_recommendation_gate(result, plan)
    assert gate_result.eligible is False
    result.escalation_package = compose_escalation_package(result, plan)

    durable = bootstrap_durable_state_from_day4(result, thread_id="thread-bank-review")

    assert durable.thread_id == "thread-bank-review"
    assert durable.thread_status == "resumable"
    assert durable.current_node == "manual_review_required"
    assert durable.payment_recommendation is None
    assert durable.escalation_package is not None
    assert durable.escalation_package["status"] == "manual_review_required"
    assert "unverified_bank_change" in durable.escalation_package["blocking_conditions"]
    assert durable.approval_state.status == "not_requested"
