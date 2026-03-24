from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Any


@dataclass(slots=True)
class EvidenceItem:
    """
    Normalized evidence object used across all retrieval lanes.

    authority_tier:
      1 = system of record
      2 = controlled policy / approved workflow artifact
      3 = business communication
      4 = derived note / model summary
    """

    evidence_id: str
    source_name: str
    source_type: str
    backend: str
    authority_tier: int
    event_time: date | None = None
    ingest_time: date | None = None
    retrieval_score: float = 0.0
    authority_adjusted_score: float = 0.0
    citation: str = ""
    raw_ref: str = ""
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    used_by_agents: list[str] = field(default_factory=list)

    def mark_used_by(self, agent_name: str) -> None:
        if agent_name not in self.used_by_agents:
            self.used_by_agents.append(agent_name)

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["event_time"] = self.event_time.isoformat() if self.event_time else None
        payload["ingest_time"] = self.ingest_time.isoformat() if self.ingest_time else None
        return payload
