from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from aegisap.day_01.models import ExtractedInvoiceCandidate, InvoicePackageInput
from aegisap.day4.planning.plan_types import CaseFacts
from aegisap.day6.state.models import ReasonCode


class Day1IntakeRequest(BaseModel):
    package: InvoicePackageInput
    candidate: ExtractedInvoiceCandidate | None = None


class Day4RunRequest(BaseModel):
    case_facts: CaseFacts
    planner_mode: Literal["fixture", "azure_openai"] = "fixture"
    enable_day6_review: bool = True
    persist_day5_handoff: bool = False
    thread_id: str | None = None
    assigned_to: str | None = None


class Day5ResumeRequest(BaseModel):
    resume_token: str
    decision: dict[str, Any] = Field(default_factory=dict)
    resumed_by: str


class HealthResponse(BaseModel):
    status: Literal["ok", "not_ready"]
    service_name: str
    environment: str
    deployment_revision: str
    git_sha: str
    image_tag: str
    checks: dict[str, str] = Field(default_factory=dict)


class VersionResponse(BaseModel):
    service_name: str
    environment: str
    deployment_revision: str
    git_sha: str
    image_tag: str


class StructuredRefusalResponse(BaseModel):
    decision_class: Literal["structured_refusal"] = "structured_refusal"
    outcome: Literal["not_authorised_to_continue"] = "not_authorised_to_continue"
    primary_reason_code: ReasonCode
    reason_codes: list[ReasonCode]
    review_stage: str
    policy_version: str | None = None
    citations_count: int = 0
    blocking: bool = True


class DecisionEnvelope(BaseModel):
    decision_class: Literal["approved", "manual_review", "structured_refusal", "unknown"]
    outcome: str
    primary_reason_code: ReasonCode | None = None
    reason_codes: list[ReasonCode] = Field(default_factory=list)
    blocking: bool = False
    structured_refusal: StructuredRefusalResponse | None = None
