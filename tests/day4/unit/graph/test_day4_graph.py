from __future__ import annotations

import asyncio
import json

from aegisap.day4.execution.task_registry import create_default_task_registry
from aegisap.day4.graph.day4_explicit_planning_graph import run_day4_explicit_planning_case
from tests.day4.helpers import build_safe_plan, load_case_facts


class StubModel:
    def __init__(self, payload: str) -> None:
        self._payload = payload

    async def invoke(self, prompt: str) -> str:
        return self._payload


def test_malformed_planner_output_fails_closed_into_plan_rejection() -> None:
    case_facts = load_case_facts("clean_path")

    state = asyncio.run(
        run_day4_explicit_planning_case(
            case_facts=case_facts,
            model=StubModel("not-json"),
            registry=create_default_task_registry(),
        )
    )

    assert state.planning.plan_status == "rejected"
    assert state.planning.escalation_status == "triggered"
    assert state.escalation_package == {
        "case_id": case_facts.case_id,
        "plan_id": None,
        "status": "plan_rejected",
        "reasons": ["planner_did_not_return_json"],
    }


def test_clean_path_generates_recommendation_without_escalation() -> None:
    case_facts = load_case_facts("clean_path")
    plan = build_safe_plan(case_facts, plan_id="plan_clean_graph")

    state = asyncio.run(
        run_day4_explicit_planning_case(
            case_facts=case_facts,
            model=StubModel(json.dumps(plan.model_dump())),
            registry=create_default_task_registry(),
        )
    )

    assert state.planning.plan_status == "completed"
    assert state.recommendation is not None
    assert state.escalation_package is None
    assert state.eligibility.recommendation_allowed is True
