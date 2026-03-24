from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from aegisap.common.clocks import utc_now_iso

from .evidence_models import EvidenceItem


@dataclass(slots=True)
class WorkflowState:
    workflow_id: str
    case_id: str
    invoice: dict[str, Any]
    started_at: str
    last_updated_at: str
    status: str = "initialized"
    current_node: str = "intake_router"
    branch_history: list[str] = field(default_factory=list)
    retrieval_context: dict[str, list[EvidenceItem]] = field(
        default_factory=lambda: {"vendor": [], "po": [], "policy": []}
    )
    evidence_registry: dict[str, EvidenceItem] = field(default_factory=dict)
    agent_findings: dict[str, Any] = field(default_factory=dict)
    eval_scores: dict[str, float | str | list[str]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    validation_errors: list[str] = field(default_factory=list)
    telemetry: dict[str, dict[str, float | int | str]] = field(default_factory=dict)

    def add_evidence(self, bucket: str, items: list[EvidenceItem]) -> None:
        if bucket not in self.retrieval_context:
            self.retrieval_context[bucket] = []
        self.retrieval_context[bucket].extend(items)
        for item in items:
            self.evidence_registry[item.evidence_id] = item

    def get_evidence(self, evidence_ids: list[str]) -> list[EvidenceItem]:
        return [self.evidence_registry[eid] for eid in evidence_ids if eid in self.evidence_registry]

    def bucket(self, *names: str) -> list[EvidenceItem]:
        items: list[EvidenceItem] = []
        for name in names:
            items.extend(self.retrieval_context.get(name, []))
        return items

    def record_agent_finding(self, name: str, finding: Any) -> None:
        self.agent_findings[name] = finding

    def enter_node(self, node_name: str) -> None:
        self.current_node = node_name
        self.last_updated_at = utc_now_iso()
        self.branch_history.append(node_name)

    def record_telemetry(self, node_name: str, **metrics: float | int | str) -> None:
        self.telemetry[node_name] = dict(metrics)


def make_initial_state(invoice: dict[str, Any]) -> WorkflowState:
    now = utc_now_iso()
    case_id = str(invoice["case_id"])
    return WorkflowState(
        workflow_id=f"day3_{uuid4().hex[:12]}",
        case_id=case_id,
        invoice=invoice,
        started_at=now,
        last_updated_at=now,
    )
