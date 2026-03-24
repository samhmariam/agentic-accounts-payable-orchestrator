from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class VendorRiskFinding:
    status: str
    risk_level: str
    key_findings: list[str]
    evidence_ids: list[str]
    recommended_action: str
    confidence: float
    open_questions: list[str] = field(default_factory=list)


@dataclass(slots=True)
class POMatchFinding:
    status: str
    risk_level: str
    key_findings: list[str]
    evidence_ids: list[str]
    recommended_action: str
    confidence: float
    variance_amount: float = 0.0
    open_questions: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DecisionRecommendation:
    recommendation: str
    rationale: str
    evidence_ids: list[str]
    confidence: float
    next_step: str
    policy_notes: list[str] = field(default_factory=list)
