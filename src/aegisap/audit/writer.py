from __future__ import annotations

import logging

from aegisap.audit.models import AuditEvent
from aegisap.day5.persistence.durable_state_store import DurableStateStore
from aegisap.observability.logging import log_structured


class AuditWriter:
    def __init__(self, *, store: DurableStateStore, logger: logging.Logger | None = None) -> None:
        self.store = store
        self.logger = logger or logging.getLogger("aegisap.audit")

    def write(self, event: AuditEvent) -> None:
        self.store.insert_audit_event(event=event)
        log_structured(
            self.logger,
            "audit_event_recorded",
            audit_id=event.audit_id,
            workflow_run_id=event.workflow_run_id,
            thread_id=event.thread_id,
            action_type=event.action_type,
            decision_outcome=event.decision_outcome,
            trace_id=event.trace_id,
            evidence_summary=event.evidence_summary_redacted,
            pii_redaction_applied=event.pii_redaction_applied,
        )

    def write_many(self, events: list[AuditEvent]) -> None:
        for event in events:
            self.write(event)
