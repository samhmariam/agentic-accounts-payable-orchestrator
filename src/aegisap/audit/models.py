from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


ActorType = Literal["managed_identity", "human_approver", "system_job"]
ActionType = Literal[
    "vendor_check",
    "po_match_check",
    "bank_detail_evaluation",
    "high_value_escalation",
    "payment_recommendation",
    "human_approval",
    "refusal",
    "resume",
    "secret_read",
]
DecisionOutcome = Literal[
    "approved_to_proceed",
    "needs_human_review",
    "not_authorised_to_continue",
    "approved",
    "rejected",
    "completed",
]


class AuditEvent(BaseModel):
    audit_id: str
    timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    workflow_run_id: str
    thread_id: str
    state_version: int
    actor_type: ActorType
    actor_id: str
    action_type: ActionType
    decision_outcome: DecisionOutcome
    approval_status: str | None = None
    evidence_summary_redacted: str
    evidence_refs: list[str] = Field(default_factory=list)
    pii_redaction_applied: bool = False
    policy_version: str | None = None
    planner_version: str | None = None
    error_code: str | None = None
    trace_id: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)

