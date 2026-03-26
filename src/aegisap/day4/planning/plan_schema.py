from __future__ import annotations

from pydantic import TypeAdapter

from .plan_types import CaseFacts, ExecutionPlan

execution_plan_adapter = TypeAdapter(ExecutionPlan)
case_facts_adapter = TypeAdapter(CaseFacts)

ExecutionPlanInput = ExecutionPlan


def parse_execution_plan(data: object) -> ExecutionPlan:
    return execution_plan_adapter.validate_python(data)


def parse_case_facts(data: object) -> CaseFacts:
    return case_facts_adapter.validate_python(data)
