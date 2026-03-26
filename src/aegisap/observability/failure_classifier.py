from __future__ import annotations

from dataclasses import dataclass
from typing import Any


FailureClass = str


@dataclass(frozen=True, slots=True)
class FailureClassification:
    top_level: FailureClass
    reason: str
    retryable: bool


def classify_failure(error: BaseException | str | None, *, dependency_name: str | None = None) -> FailureClassification:
    if error is None:
        return FailureClassification(top_level="none", reason="no_error", retryable=False)

    text = str(error).lower()
    dependency = (dependency_name or "").lower()
    if "429" in text or "too many requests" in text or "throttle" in text or "quota" in text:
        return FailureClassification(top_level="dependency_failure", reason="quota_throttle", retryable=True)
    if any(token in text for token in ("timeout", "timed out", "connection reset", "temporarily unavailable")):
        return FailureClassification(top_level="dependency_failure", reason="transient_timeout", retryable=True)
    if dependency in {"azure_ai_search", "postgres", "key_vault", "network"}:
        return FailureClassification(top_level="dependency_failure", reason=f"{dependency}_error", retryable=False)
    if any(token in text for token in ("hallucination", "malformed", "schema", "structured output")):
        return FailureClassification(top_level="model_failure", reason="malformed_structured_output", retryable=False)
    if any(token in text for token in ("evidence", "retrieval", "search index", "low confidence")):
        return FailureClassification(top_level="retrieval_failure", reason="evidence_issue", retryable=False)
    if any(token in text for token in ("policy", "authori", "refusal", "insufficient_evidence")):
        return FailureClassification(top_level="policy_failure", reason="policy_boundary", retryable=False)
    if any(token in text for token in ("resume", "checkpoint", "idempotent", "route", "branch")):
        return FailureClassification(top_level="orchestration_failure", reason="workflow_state_error", retryable=False)
    if any(token in text for token in ("ocr", "missing po", "locale", "malformed source")):
        return FailureClassification(top_level="data_quality_failure", reason="source_data_issue", retryable=False)
    if any(token in text for token in ("approval", "sla", "override")):
        return FailureClassification(top_level="human_process_failure", reason="approval_process_issue", retryable=False)
    return FailureClassification(top_level="dependency_failure", reason="unclassified_error", retryable=False)


def failure_attributes(
    error: BaseException | str | None,
    *,
    dependency_name: str | None = None,
) -> dict[str, Any]:
    classification = classify_failure(error, dependency_name=dependency_name)
    return {
        "aegis.failure_class": classification.top_level,
        "error.class": classification.reason,
        "aegis.retryable": classification.retryable,
    }
