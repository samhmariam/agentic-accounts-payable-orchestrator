from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


STATE_SCHEMA_VERSION = 7


ThreadStatus = Literal[
    "running",
    "awaiting_approval",
    "resumable",
    "completed",
    "failed",
    "quarantined",
]

ApprovalStatus = Literal[
    "not_requested",
    "pending",
    "approved",
    "rejected",
    "expired",
]

ReviewTaskStatus = Literal[
    "not_requested",
    "pending",
    "completed",
]


class EvidenceSnapshot(BaseModel):
    evidence_id: str
    source_type: Literal["erp", "retrieval", "tool", "human_note", "policy"]
    source_ref: str
    captured_at: datetime
    payload: dict[str, Any]
    payload_hash: str
    freshness_class: Literal["static", "slow_changing", "time_sensitive"] = "slow_changing"
    replay_safe: bool = False


class ToolExecutionRecord(BaseModel):
    tool_name: str
    tool_call_id: str
    executed_at: datetime
    input_hash: str
    output_hash: str
    deterministic: bool = False
    replay_safe: bool = False
    evidence_snapshot_id: str | None = None


class SideEffectRecord(BaseModel):
    effect_key: str
    effect_type: Literal[
        "audit_entry",
        "payment_recommendation",
        "notification",
        "erp_write",
    ]
    status: Literal["pending", "applied", "deduplicated", "failed"]
    created_at: datetime
    result_ref: str | None = None


class ApprovalState(BaseModel):
    status: ApprovalStatus = "not_requested"
    approval_task_id: str | None = None
    assigned_to: str | None = None
    requested_at: datetime | None = None
    resolved_at: datetime | None = None
    decision_payload: dict[str, Any] | None = None


class HistoryMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool", "reviewer"]
    content: str
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class HistoryState(BaseModel):
    raw_messages: list[HistoryMessage] = Field(default_factory=list)
    summary_blocks: list[dict[str, Any]] = Field(default_factory=list)
    retained_window_size: int = 12


class ResumeMetadata(BaseModel):
    resume_token_id: str | None = None
    resumable_from_checkpoint_id: str | None = None
    last_resume_attempt_at: datetime | None = None
    last_resumed_by: str | None = None


class ReviewTaskState(BaseModel):
    status: ReviewTaskStatus = "not_requested"
    review_task_id: str | None = None
    assigned_to: str | None = None
    requested_at: datetime | None = None
    resolved_at: datetime | None = None
    decision_payload: dict[str, Any] | None = None
    missing_requirements: list[str] = Field(default_factory=list)


class DurableWorkflowState(BaseModel):
    workflow_run_id: str
    thread_id: str
    case_id: str
    workflow_name: str = "payment_recommendation_workflow"
    observability: dict[str, Any] = Field(default_factory=dict)
    task_class: str = "plan"
    risk_flags: list[str] = Field(default_factory=list)
    routing_decision: dict[str, Any] = Field(default_factory=dict)
    model_deployment: str | None = None
    cache_hit: bool = False
    workflow_cost_estimate: float = 0.0
    cost_ledger: list[dict[str, Any]] = Field(default_factory=list)
    evidence_conflict_count: int = 0
    retrieval_confidence: float | None = None

    checkpoint_seq: int = 0
    current_node: str = "start"
    thread_status: ThreadStatus = "running"

    state_schema_version: int = STATE_SCHEMA_VERSION
    state_checksum: str | None = None

    plan_version: str = "v1"
    execution_plan: dict[str, Any] = Field(default_factory=dict)

    canonical_invoice: dict[str, Any] = Field(default_factory=dict)
    payment_recommendation: dict[str, Any] | None = None
    escalation_package: dict[str, Any] | None = None
    review_outcome: dict[str, Any] | None = None
    review_summary: str | None = None

    approval_state: ApprovalState = Field(default_factory=ApprovalState)
    review_task_state: ReviewTaskState = Field(default_factory=ReviewTaskState)
    evidence_snapshots: list[EvidenceSnapshot] = Field(default_factory=list)
    tool_execution_records: list[ToolExecutionRecord] = Field(default_factory=list)
    side_effect_records: list[SideEffectRecord] = Field(default_factory=list)

    history_state: HistoryState = Field(default_factory=HistoryState)
    resume_metadata: ResumeMetadata = Field(default_factory=ResumeMetadata)

    last_error: str | None = None
    created_at: datetime
    updated_at: datetime

    def canonical_payload(self) -> dict[str, Any]:
        payload = self.model_dump(mode="json")
        payload["state_checksum"] = None
        return payload
