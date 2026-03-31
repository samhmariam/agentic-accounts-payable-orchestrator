"""
Shared TokenUsage dataclass — records prompt + completion token counts
and a simple cost estimate for any LLM call within AegisAP notebooks.
"""
from __future__ import annotations

from dataclasses import dataclass


# Approximate cost per 1 000 tokens (USD) — update to match your deployment pricing.
_COST_PER_1K: dict[str, dict[str, float]] = {
    "light": {"input": 0.00015, "output": 0.00060},   # gpt-4.1-mini
    "strong": {"input": 0.00200, "output": 0.00800},  # gpt-4.1
}


@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    deployment_tier: str = "light"

    @property
    def estimated_cost_usd(self) -> float:
        rates = _COST_PER_1K.get(self.deployment_tier, _COST_PER_1K["light"])
        return round(
            (self.prompt_tokens / 1000) * rates["input"]
            + (self.completion_tokens / 1000) * rates["output"],
            6,
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "deployment_tier": self.deployment_tier,
            "estimated_cost_usd": self.estimated_cost_usd,
        }
