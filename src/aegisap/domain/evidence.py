from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    """Append-only evidence captured during routing and review."""

    kind: str
    source: str
    detail: str
    value: Any = None
    node_name: str | None = None
    recorded_at: str | None = None


class ActionRecommendation(BaseModel):
    """Non-binding operational recommendation for later workflow stages."""

    action: str
    reason: str
    owner: str | None = None
    status: str = Field(default="pending")
