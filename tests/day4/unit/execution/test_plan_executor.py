import asyncio

from aegisap.day4.execution.plan_executor import execute_plan
from aegisap.day4.execution.task_registry import create_default_task_registry
from aegisap.day4.state.workflow_state import create_initial_workflow_state
from tests.day4.helpers import build_safe_plan, load_case_facts


def test_clean_path_completes_recommendation_tasks_serially() -> None:
    case_facts = load_case_facts("clean_path")
    plan = build_safe_plan(case_facts, plan_id="plan_clean_serial")
    state = create_initial_workflow_state(case_facts)
    state.plan = plan

    result = asyncio.run(execute_plan(state=state, plan=plan, registry=create_default_task_registry()))

    completed_task_types = [entry.task_type for entry in result.task_ledger if entry.status == "completed"]
    assert completed_task_types == ["policy_retrieval", "vendor_history_check", "payment_recommendation_draft"]
    assert result.planning.escalation_status == "none"


def test_executor_stops_and_skips_remaining_tasks_after_safety_escalation() -> None:
    case_facts = load_case_facts("bank_change")
    plan = build_safe_plan(case_facts, plan_id="plan_bank_change")
    state = create_initial_workflow_state(case_facts)
    state.plan = plan

    result = asyncio.run(execute_plan(state=state, plan=plan, registry=create_default_task_registry()))

    bank_task = next(entry for entry in result.task_ledger if entry.task_type == "vendor_bank_verification")
    draft_task = next(entry for entry in result.task_ledger if entry.task_type == "payment_recommendation_draft")
    assert bank_task.status == "escalated"
    assert draft_task.status == "skipped"
    assert result.planning.escalation_status == "triggered"
    assert "unverified_bank_change" in result.eligibility.blocking_conditions
