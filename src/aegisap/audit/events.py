from __future__ import annotations

import uuid
from typing import Any

from aegisap.audit.models import AuditEvent
from aegisap.security.redaction import summarize_evidence_text


BUFFER_KEY = "_audit_events"


def build_audit_event(
    *,
    workflow_run_id: str,
    thread_id: str,
    state_version: int,
    actor_type: str,
    actor_id: str,
    action_type: str,
    decision_outcome: str,
    evidence_summary: str,
    evidence_refs: list[str] | None = None,
    policy_version: str | None = None,
    planner_version: str | None = None,
    error_code: str | None = None,
    trace_id: str | None = None,
    approval_status: str | None = None,
    metadata: dict[str, object] | None = None,
) -> AuditEvent:
    redacted_summary, pii_redaction_applied = summarize_evidence_text(evidence_summary)
    return AuditEvent(
        audit_id=str(uuid.uuid4()),
        workflow_run_id=workflow_run_id,
        thread_id=thread_id,
        state_version=state_version,
        actor_type=actor_type,  # type: ignore[arg-type]
        actor_id=actor_id,
        action_type=action_type,  # type: ignore[arg-type]
        decision_outcome=decision_outcome,  # type: ignore[arg-type]
        approval_status=approval_status,
        evidence_summary_redacted=redacted_summary,
        evidence_refs=evidence_refs or [],
        pii_redaction_applied=pii_redaction_applied,
        policy_version=policy_version,
        planner_version=planner_version,
        error_code=error_code,
        trace_id=trace_id,
        metadata=metadata or {},
    )


def buffer_audit_event(artifacts: dict[str, dict[str, Any]], event: AuditEvent) -> None:
    artifacts.setdefault(BUFFER_KEY, {"events": []})
    artifacts[BUFFER_KEY].setdefault("events", [])
    artifacts[BUFFER_KEY]["events"].append(event.model_dump(mode="json"))


def buffered_audit_events(artifacts: dict[str, dict[str, Any]]) -> list[AuditEvent]:
    payload = artifacts.get(BUFFER_KEY, {})
    return [AuditEvent.model_validate(item) for item in payload.get("events", [])]

