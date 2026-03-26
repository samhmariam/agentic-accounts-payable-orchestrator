from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from aegisap.day4.planning.plan_types import (
    CaseFacts,
    ExecutionPlan,
    RecommendationGateResult,
    TaskLedgerEntry,
)


class PlanningState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    requires_explicit_plan: bool
    plan_status: str
    plan_id: str | None
    plan_version: str | None
    planner_input_snapshot: dict[str, Any]
    validated: bool
    validation_errors: list[str]
    active_task_ids: list[str]
    completed_task_ids: list[str]
    blocked_task_ids: list[str]
    escalation_status: str


class EligibilityState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    recommendation_allowed: bool
    unmet_preconditions: list[str]
    missing_evidence: list[str]
    required_approvals: list[str]
    blocking_conditions: list[str]
    irreversible_actions_allowed: bool


class WorkflowState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    case_facts: CaseFacts
    retrieved_evidence: list[str]
    planning: PlanningState
    eligibility: EligibilityState
    task_ledger: list[TaskLedgerEntry]
    plan: ExecutionPlan | None = None
    recommendation_gate_result: RecommendationGateResult | None = None
    recommendation: dict[str, Any] | None = None
    escalation_package: dict[str, Any] | None = None
    artifacts: dict[str, dict[str, Any]] = Field(default_factory=dict)


def create_initial_workflow_state(case_facts: CaseFacts) -> WorkflowState:
    return WorkflowState(
        case_facts=case_facts,
        retrieved_evidence=case_facts.retrieved_evidence_ids or [],
        planning=PlanningState(
            requires_explicit_plan=True,
            plan_status="not_started",
            plan_id=None,
            plan_version="day4",
            planner_input_snapshot={},
            validated=False,
            validation_errors=[],
            active_task_ids=[],
            completed_task_ids=[],
            blocked_task_ids=[],
            escalation_status="none",
        ),
        eligibility=EligibilityState(
            recommendation_allowed=False,
            unmet_preconditions=[],
            missing_evidence=[],
            required_approvals=[],
            blocking_conditions=[],
            irreversible_actions_allowed=False,
        ),
        task_ledger=[],
    )
