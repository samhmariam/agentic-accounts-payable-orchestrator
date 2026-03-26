from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


ReviewStage = Literal["policy_tax_compliance_review"]
ReviewOutcomeValue = Literal[
    "approved_to_proceed",
    "needs_human_review",
    "not_authorised_to_continue",
]
ReasonCode = Literal[
    "INSUFFICIENT_EVIDENCE",
    "MISSING_AUTHORITY",
    "CONTRADICTORY_EVIDENCE",
    "PROMPT_INJECTION_ATTEMPT",
    "POLICY_CONFLICT",
    "OUT_OF_SCOPE_ACTION",
    "UNVERIFIED_APPROVAL_CLAIM",
    "UNTRUSTED_OVERRIDE_REQUEST",
]
Severity = Literal["low", "medium", "high"]
EvidenceSourceType = Literal[
    "email",
    "erp_record",
    "po_record",
    "invoice_ocr",
    "policy_doc",
    "approval_record",
    "tool_artifact",
    "vendor_master",
    "retrieval_note",
    "case_summary",
]
TrustTier = Literal["authoritative", "policy", "derived", "untrusted"]
CheckStatus = Literal["pass", "fail", "not_applicable"]
Sufficiency = Literal["sufficient", "insufficient", "conflicting"]
NextActionOwner = Literal["system", "finance_controller", "tax_reviewer", "operator"]


class EvidenceLedgerItem(BaseModel):
    evidence_id: str
    source_type: EvidenceSourceType
    source_ref: str
    trust_tier: TrustTier
    timestamp: str
    extract: str
    payload_hash: str
    derived_claim_ids: list[str] = Field(default_factory=list)


class ClaimLedgerItem(BaseModel):
    claim_id: str
    claim_type: str
    summary: str
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    conflicting_evidence_ids: list[str] = Field(default_factory=list)
    requires_authority: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class PolicyReference(BaseModel):
    policy_id: str
    title: str
    description: str


class PolicyContext(BaseModel):
    policy_version: str
    accepted_approval_channels: list[str]
    mandatory_checks: list[str]
    policy_references: list[PolicyReference]
    control_plane_rules: list[str] = Field(default_factory=list)


class AuthorityContext(BaseModel):
    required_approvals: list[str] = Field(default_factory=list)
    registered_approval_channels: list[str] = Field(default_factory=list)
    allowed_actions: list[str] = Field(default_factory=list)
    prohibited_actions: list[str] = Field(default_factory=list)


class InjectionSignal(BaseModel):
    evidence_id: str
    signal: str
    severity: Severity


class ReviewReason(BaseModel):
    code: ReasonCode
    severity: Severity
    message: str
    evidence_ids: list[str] = Field(default_factory=list)
    policy_ids: list[str] = Field(default_factory=list)


class EvidenceCitation(BaseModel):
    evidence_id: str
    source_type: str
    excerpt: str


class MandatoryCheckResult(BaseModel):
    check_id: str
    status: CheckStatus
    reason_code: str
    evidence_ids: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    policy_ids: list[str] = Field(default_factory=list)


class AuthorisationCheck(BaseModel):
    required: bool
    present: bool
    approval_channel_valid: bool
    approver_identity_verified: bool
    approved_by: str | None = None
    notes: str


class EvidenceAssessment(BaseModel):
    sufficiency: Sufficiency
    mandatory_checks: list[MandatoryCheckResult] = Field(default_factory=list)


class NextAction(BaseModel):
    action: str
    owner: NextActionOwner
    blocking: bool


class ModelTrace(BaseModel):
    prompt_version: str
    policy_version: str
    reviewer_model: str


class ReflectionReview(BaseModel):
    required_claims: list[str] = Field(default_factory=list)
    unresolved_conflicts: list[str] = Field(default_factory=list)
    override_signals: list[str] = Field(default_factory=list)
    recommended_outcome: ReviewOutcomeValue
    rationale: str


class ReviewOutcome(BaseModel):
    case_id: str
    thread_id: str
    review_stage: ReviewStage = "policy_tax_compliance_review"
    outcome: ReviewOutcomeValue
    decision_summary: str
    reasons: list[ReviewReason]
    citations: list[EvidenceCitation]
    authorisation_check: AuthorisationCheck
    evidence_assessment: EvidenceAssessment
    next_actions: list[NextAction]
    model_trace: ModelTrace
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @model_validator(mode="after")
    def validate_terminal_refusal(self) -> "ReviewOutcome":
        if self.outcome == "not_authorised_to_continue":
            if not any(reason.severity == "high" for reason in self.reasons):
                raise ValueError(
                    "not_authorised_to_continue requires at least one high-severity reason"
                )
            if not self.citations:
                raise ValueError("not_authorised_to_continue requires at least one citation")
        return self


class Day6ReviewInput(BaseModel):
    case_id: str
    thread_id: str
    candidate_recommendation: dict[str, Any] | None = None
    escalation_package: dict[str, Any] | None = None
    evidence_ledger: list[EvidenceLedgerItem]
    claim_ledger: list[ClaimLedgerItem] = Field(default_factory=list)
    policy_context: PolicyContext
    authority_context: AuthorityContext
    injection_flags: list[str] = Field(default_factory=list)
    missing_requirements: list[str] = Field(default_factory=list)
    conflict_flags: list[str] = Field(default_factory=list)
    review_metadata: dict[str, Any] = Field(default_factory=dict)

