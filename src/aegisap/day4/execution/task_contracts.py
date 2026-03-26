from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict

from aegisap.day4.planning.plan_types import PlanTaskType, TaskResult
from aegisap.day4.state.workflow_state import WorkflowState


class WorkerTaskInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    task_id: str
    case_id: str
    workflow_state: WorkflowState
    task_inputs: dict[str, Any]
    required_evidence: list[str]
    expected_outputs: list[str]


class WorkerExecutor(Protocol):
    task_type: PlanTaskType

    async def execute(self, input_data: WorkerTaskInput) -> TaskResult:
        ...


class TaskContractDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    task_type: PlanTaskType
    description: str
    expected_output_fields: list[str]
    owner_agent: str


TASK_CONTRACTS = [
    TaskContractDefinition(
        task_type="policy_retrieval",
        description="Retrieve governing policy clauses relevant to the case.",
        expected_output_fields=["policy_requirements", "citation_refs", "confidence"],
        owner_agent="policy_retriever",
    ),
    TaskContractDefinition(
        task_type="po_match_verification",
        description="Verify whether a matching PO exists and is valid.",
        expected_output_fields=[
            "po_match_status",
            "matched_fields",
            "missing_fields",
            "mismatch_flags",
            "confidence",
        ],
        owner_agent="po_match_agent",
    ),
    TaskContractDefinition(
        task_type="po_waiver_check",
        description="Check whether an approved PO waiver exists.",
        expected_output_fields=["waiver_present", "waiver_authority", "confidence"],
        owner_agent="po_waiver_verifier",
    ),
    TaskContractDefinition(
        task_type="vendor_history_check",
        description="Retrieve supplier history and historical risk context.",
        expected_output_fields=["supplier_history_summary", "risk_level", "confidence"],
        owner_agent="vendor_history_verifier",
    ),
    TaskContractDefinition(
        task_type="vendor_bank_verification",
        description="Verify changed bank details using authoritative evidence.",
        expected_output_fields=[
            "bank_change_verified",
            "authoritative_source_checked",
            "risk_level",
            "confidence",
        ],
        owner_agent="vendor_risk_verifier",
    ),
    TaskContractDefinition(
        task_type="threshold_approval_check",
        description="Determine approval route required by amount thresholds.",
        expected_output_fields=["required_approvals", "approval_path_defined", "confidence"],
        owner_agent="approval_policy_agent",
    ),
    TaskContractDefinition(
        task_type="manual_escalation_package",
        description="Prepare a package for manual review with blocking reasons and evidence.",
        expected_output_fields=["escalation_reasons", "evidence_bundle", "confidence"],
        owner_agent="escalation_composer",
    ),
    TaskContractDefinition(
        task_type="payment_recommendation_draft",
        description="Draft the recommendation package without releasing a final decision.",
        expected_output_fields=["recommendation_draft", "confidence"],
        owner_agent="payment_recommendation_agent",
    ),
]

TASK_CONTRACT_BY_TYPE = {contract.task_type: contract for contract in TASK_CONTRACTS}


def get_task_contract(task_type: PlanTaskType) -> TaskContractDefinition:
    return TASK_CONTRACT_BY_TYPE[task_type]


def validate_task_result_against_contract(task_type: PlanTaskType, result: TaskResult) -> list[str]:
    errors: list[str] = []
    contract = get_task_contract(task_type)

    for field_name in contract.expected_output_fields:
        if field_name not in result.outputs:
            errors.append(f"task result missing required output field: {field_name}")

    return errors
