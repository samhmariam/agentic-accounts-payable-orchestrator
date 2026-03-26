from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

PLAN_TASK_TYPES = (
    "policy_retrieval",
    "po_match_verification",
    "po_waiver_check",
    "vendor_history_check",
    "vendor_bank_verification",
    "threshold_approval_check",
    "manual_escalation_package",
    "payment_recommendation_draft",
)

PlanTaskType = Literal[
    "policy_retrieval",
    "po_match_verification",
    "po_waiver_check",
    "vendor_history_check",
    "vendor_bank_verification",
    "threshold_approval_check",
    "manual_escalation_package",
    "payment_recommendation_draft",
]

TASK_STATUSES = (
    "pending",
    "ready",
    "running",
    "completed",
    "blocked",
    "failed",
    "skipped",
    "escalated",
)

TaskStatus = Literal[
    "pending",
    "ready",
    "running",
    "completed",
    "blocked",
    "failed",
    "skipped",
    "escalated",
]

ACTION_CLASSES = ("reversible", "irreversible")
ActionClass = Literal["reversible", "irreversible"]

FAILURE_BEHAVIORS = ("block", "escalate", "skip")
FailureBehavior = Literal["block", "escalate", "skip"]

RiskFlag = Literal[
    "clean_path",
    "missing_po",
    "bank_details_changed",
    "high_value",
    "combined_risk",
    "existing_supplier",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EvidenceRef(StrictModel):
    source_id: str
    source_type: Literal["structured", "document", "email", "policy", "derived"]
    pointer: str | None = None


class CaseFacts(StrictModel):
    case_id: str
    invoice_id: str
    supplier_id: str
    supplier_name: str
    supplier_exists: bool
    invoice_amount_gbp: float
    invoice_currency: str
    po_present: bool
    po_number: str | None = None
    bank_details_changed: bool
    bank_change_verified: bool | None = None
    amount_approval_threshold_gbp: float | None = None
    controller_approval_threshold_gbp: float | None = None
    retrieved_evidence_ids: list[str] | None = None


class EscalationRoute(StrictModel):
    queue: str
    owners: list[str]


class PlanTask(StrictModel):
    task_id: str
    task_type: PlanTaskType
    owner_agent: str
    depends_on: list[str]
    inputs: dict[str, Any] = Field(default_factory=dict)
    required_evidence: list[str]
    expected_outputs: list[str]
    preconditions: list[str]
    stop_if_missing: bool
    min_confidence: float
    on_failure: FailureBehavior
    action_class: ActionClass


class RecommendationGate(StrictModel):
    all_mandatory_tasks_completed: bool
    required_evidence_present: bool
    no_unresolved_blockers: bool
    confidence_thresholds_met: bool
    required_approvals_identified: bool
    mandatory_escalations_resolved_or_triggered: bool
    po_condition_satisfied: bool
    bank_change_verification_satisfied: bool
    approval_path_satisfied: bool


class ActionClassification(StrictModel):
    current_stage: ActionClass
    irreversible_actions_allowed: bool


class ExecutionPlan(StrictModel):
    plan_id: str
    case_id: str
    goal: str
    case_risk_flags: list[RiskFlag]
    planning_rationale: str
    tasks: list[PlanTask]
    global_preconditions: list[str]
    global_stop_conditions: list[str]
    escalation_triggers: list[str]
    escalation_route: EscalationRoute
    escalation_reason_template: str
    required_approvals: list[str]
    recommendation_gate: RecommendationGate
    action_classification: ActionClassification


class DerivedPolicyOverlay(StrictModel):
    risk_flags: list[RiskFlag]
    mandatory_task_types: list[PlanTaskType]
    global_preconditions: list[str]
    global_stop_conditions: list[str]
    escalation_triggers: list[str]
    required_approvals: list[str]
    recommendation_blocks: list[str]
    escalation_route: EscalationRoute
    escalation_reason_template: str


class TaskResult(StrictModel):
    task_id: str
    status: Literal["completed", "blocked", "failed", "escalated"]
    confidence: float
    outputs: dict[str, Any]
    blocking_reason: str | None = None
    evidence_refs: list[EvidenceRef] | None = None


class TaskLedgerEntry(StrictModel):
    task_id: str
    task_type: PlanTaskType
    owner_agent: str
    status: TaskStatus
    depends_on: list[str]
    started_at: str | None = None
    completed_at: str | None = None
    result_ref: str | None = None
    confidence: float | None = None
    blocking_reason: str | None = None
    outputs: dict[str, Any] | None = None


class RecommendationGateResult(StrictModel):
    eligible: bool
    reasons: list[str]
