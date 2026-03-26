from __future__ import annotations

import asyncio
import json

from aegisap.day4.execution.task_registry import create_default_task_registry
from aegisap.day4.graph.day4_explicit_planning_graph import run_day4_explicit_planning_case
from tests.day4.helpers import build_safe_plan, load_case_facts, load_day4_fixture


class StubModel:
    def __init__(self, payload: str) -> None:
        self._payload = payload

    async def invoke(self, prompt: str) -> str:
        return self._payload


def test_forces_escalation_for_high_value_missing_po_and_bank_change_case() -> None:
    fixture = load_day4_fixture("high_value_missing_po_bank_change")
    case_facts = load_case_facts("high_value_missing_po_bank_change")
    plan = build_safe_plan(case_facts, plan_id="unsafe_controls_blocked")

    state = asyncio.run(
        run_day4_explicit_planning_case(
            case_facts=case_facts,
            model=StubModel(json.dumps(plan.model_dump())),
            registry=create_default_task_registry(),
        )
    )

    assert set(fixture["expected"]["must_include_task_types"]) <= {task.task_type for task in plan.tasks}
    assert state.recommendation is None
    assert state.escalation_package is not None
    assert state.escalation_package["status"] == "manual_review_required"
    assert state.planning.escalation_status == "triggered"
    assert state.eligibility.recommendation_allowed is False
