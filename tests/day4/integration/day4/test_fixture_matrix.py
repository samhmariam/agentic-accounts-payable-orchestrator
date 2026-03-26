from __future__ import annotations

import asyncio
import json

import pytest

from aegisap.day4.execution.task_registry import create_default_task_registry
from aegisap.day4.graph.day4_explicit_planning_graph import run_day4_explicit_planning_case
from aegisap.day4.planning.policy_overlay import derive_policy_overlay
from tests.day4.helpers import build_safe_plan, load_case_facts, load_day4_fixture


class StubModel:
    def __init__(self, payload: str) -> None:
        self._payload = payload

    async def invoke(self, prompt: str) -> str:
        return self._payload


@pytest.mark.parametrize(
    ("fixture_name", "expects_recommendation"),
    [
        ("clean_path", True),
        ("missing_po", False),
        ("bank_change", False),
        ("high_value_missing_po", False),
        ("high_value_missing_po_bank_change", False),
    ],
)
def test_day4_fixture_matrix(fixture_name: str, expects_recommendation: bool) -> None:
    fixture = load_day4_fixture(fixture_name)
    case_facts = load_case_facts(fixture_name)
    overlay = derive_policy_overlay(case_facts)
    plan = build_safe_plan(case_facts, plan_id=f"plan_{fixture_name}")

    state = asyncio.run(
        run_day4_explicit_planning_case(
            case_facts=case_facts,
            model=StubModel(json.dumps(plan.model_dump())),
            registry=create_default_task_registry(),
        )
    )

    expected = fixture["expected"]
    assert set(expected.get("must_include_risk_flags", [])) <= set(overlay.risk_flags)
    assert set(expected.get("must_include_task_types", [])) <= {task.task_type for task in plan.tasks}
    assert set(expected.get("must_require_approvals", [])) <= set(plan.required_approvals)

    if expects_recommendation:
        assert state.recommendation is not None
        assert state.escalation_package is None
    else:
        assert state.recommendation is None
        assert state.escalation_package is not None

    if expected.get("must_escalate"):
        assert state.planning.escalation_status == "triggered"
    if expected.get("must_not_escalate"):
        assert state.planning.escalation_status == "none"
