from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from aegisap.day_01.models import ExtractedInvoiceCandidate, InvoicePackageInput
from aegisap.day4.planning.plan_types import CaseFacts


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
