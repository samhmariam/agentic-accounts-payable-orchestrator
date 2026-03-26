from aegisap.day4.recommendation.recommendation_gate import evaluate_recommendation_gate
from aegisap.day4.state.workflow_state import create_initial_workflow_state
from tests.day4.helpers import build_safe_plan, load_case_facts


def test_fails_closed_when_combined_risk_requires_manual_escalation() -> None:
    case_facts = load_case_facts("high_value_missing_po_bank_change")
    state = create_initial_workflow_state(case_facts)
    plan = build_safe_plan(case_facts, plan_id="plan_combined_risk")

    result = evaluate_recommendation_gate(state, plan)

    assert result.eligible is False
    joined = " | ".join(result.reasons)
    assert "manual escalation package present in plan" in joined
    assert "combined_risk_requires_manual_review" in joined
    assert "po condition unsatisfied" in joined
    assert "bank change not authoritatively verified" in joined
