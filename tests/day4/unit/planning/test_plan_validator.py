import pytest
from pydantic import ValidationError

from aegisap.day4.planning.plan_schema import parse_execution_plan
from aegisap.day4.planning.plan_types import ActionClassification, ExecutionPlan, PlanTask, RecommendationGate
from aegisap.day4.planning.plan_validator import validate_execution_plan
from aegisap.day4.planning.policy_overlay import derive_policy_overlay
from tests.day4.helpers import build_safe_plan, load_case_facts


def test_rejects_silent_failure_plan_that_omits_bank_verification_and_escalation_logic() -> None:
    case_facts = load_case_facts("high_value_missing_po_bank_change")
    overlay = derive_policy_overlay(case_facts)

    unsafe_plan = ExecutionPlan(
        plan_id="plan_unsafe",
        case_id=case_facts.case_id,
        goal="Determine payment recommendation eligibility",
        case_risk_flags=["existing_supplier", "high_value"],
        planning_rationale="Existing supplier appears low risk.",
        tasks=[
            PlanTask(
                task_id="policy_retrieval",
                task_type="policy_retrieval",
                owner_agent="policy_retriever",
                depends_on=[],
                inputs={},
                required_evidence=["policy:controls"],
                expected_outputs=["policy_requirements", "citation_refs", "confidence"],
                preconditions=[],
                stop_if_missing=True,
                min_confidence=0.8,
                on_failure="block",
                action_class="reversible",
            ),
            PlanTask(
                task_id="payment_recommendation_draft",
                task_type="payment_recommendation_draft",
                owner_agent="payment_recommendation_agent",
                depends_on=["policy_retrieval"],
                inputs={},
                required_evidence=[],
                expected_outputs=["recommendation_draft", "confidence"],
                preconditions=[],
                stop_if_missing=False,
                min_confidence=0.8,
                on_failure="block",
                action_class="reversible",
            ),
        ],
        global_preconditions=[],
        global_stop_conditions=[],
        escalation_triggers=[],
        escalation_route=overlay.escalation_route,
        escalation_reason_template=overlay.escalation_reason_template,
        required_approvals=[],
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

    result = validate_execution_plan(unsafe_plan, overlay)

    assert result.valid is False
    joined = " | ".join(result.errors)
    assert "missing mandatory task type: vendor_bank_verification" in joined
    assert "missing mandatory task type: threshold_approval_check" in joined
    assert "missing mandatory task type: manual_escalation_package" in joined
    assert "missing global precondition: bank_change_authoritatively_verified" in joined
    assert "missing escalation trigger: combined_risk_flags_present" in joined


def test_plan_schema_is_strictly_snake_case() -> None:
    with pytest.raises(ValidationError):
        parse_execution_plan({"planId": "legacy"})


def test_valid_plan_passes_validation() -> None:
    case_facts = load_case_facts("clean_path")
    overlay = derive_policy_overlay(case_facts)
    plan = build_safe_plan(case_facts, plan_id="plan_clean")

    result = validate_execution_plan(plan, overlay)

    assert result.valid is True
    assert result.errors == []
