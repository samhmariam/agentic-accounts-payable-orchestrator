from __future__ import annotations

from pydantic import BaseModel, Field


class NodeMetric(BaseModel):
    node_name: str
    started_at: str
    finished_at: str
    latency_ms: int = Field(ge=0)
    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    estimated_cost_usd: float = Field(default=0.0, ge=0.0)
    outcome: str
