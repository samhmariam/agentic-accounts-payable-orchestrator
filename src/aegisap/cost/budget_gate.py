"""
Budget gate — checks whether the accumulated cost for a session
or time window would breach the configured daily limit.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BudgetStatus:
    total_cost_usd: float
    daily_limit_usd: float
    within_budget: bool
    projected_daily_usd: float
    calls_sampled: int

    @property
    def headroom_usd(self) -> float:
        return round(max(0.0, self.daily_limit_usd - self.total_cost_usd), 6)

    def as_dict(self) -> dict[str, Any]:
        return {
            "total_cost_usd": self.total_cost_usd,
            "daily_limit_usd": self.daily_limit_usd,
            "within_budget": self.within_budget,
            "projected_daily_usd": self.projected_daily_usd,
            "headroom_usd": self.headroom_usd,
            "calls_sampled": self.calls_sampled,
        }


def check_budget(
    ledger: list[dict[str, Any]],
    daily_limit_usd: float,
    *,
    hours_elapsed: float = 1.0,
) -> BudgetStatus:
    """
    Evaluate whether the accumulated cost in ``ledger`` is within budget.

    ``hours_elapsed`` is used to project the daily cost from the sample window.
    """
    total = round(sum(float(row.get("estimated_cost", 0.0) or 0.0)
                  for row in ledger), 6)
    # Simple linear projection to 24 hours
    hours_factor = max(24.0 / max(hours_elapsed, 0.01), 1.0)
    projected = round(total * hours_factor, 4)
    return BudgetStatus(
        total_cost_usd=total,
        daily_limit_usd=daily_limit_usd,
        within_budget=total <= daily_limit_usd,
        projected_daily_usd=projected,
        calls_sampled=len(ledger),
    )
