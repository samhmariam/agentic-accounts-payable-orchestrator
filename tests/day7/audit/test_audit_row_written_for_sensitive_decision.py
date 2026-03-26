from __future__ import annotations

from aegisap.audit.events import build_audit_event
from aegisap.audit.writer import AuditWriter


class FakeStore:
    def __init__(self) -> None:
        self.events = []

    def insert_audit_event(self, *, event, conn=None) -> None:
        self.events.append(event.model_dump(mode="json"))


def test_audit_writer_persists_redacted_sensitive_decision() -> None:
    store = FakeStore()
    event = build_audit_event(
        workflow_run_id="case-1",
        thread_id="thread-1",
        state_version=7,
        actor_type="managed_identity",
        actor_id="runtime-api",
        action_type="refusal",
        decision_outcome="not_authorised_to_continue",
        evidence_summary=(
            "Blocked because finance@example.com requested approval via phone +44 20 7946 0958 "
            "for VAT GB123456789 and account 12345678."
        ),
        evidence_refs=["email_017", "POL-AUTH-004"],
        error_code="UNVERIFIED_APPROVAL_CLAIM",
        trace_id="trace-123",
    )

    AuditWriter(store=store).write(event)  # type: ignore[arg-type]

    assert len(store.events) == 1
    stored = store.events[0]
    assert stored["trace_id"] == "trace-123"
    assert stored["error_code"] == "UNVERIFIED_APPROVAL_CLAIM"
    assert stored["pii_redaction_applied"] is True
    assert "finance@example.com" not in stored["evidence_summary_redacted"]
    assert "0958" not in stored["evidence_summary_redacted"]
    assert stored["evidence_refs"] == ["email_017", "POL-AUTH-004"]
