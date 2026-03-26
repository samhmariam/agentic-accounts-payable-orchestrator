from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aegisap.observability.metrics import record_workflow_cost


@dataclass(slots=True)
class CostLedgerEntry:
    task_class: str
    node_name: str
    deployment_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cached_hit: bool
    latency_ms: int
    retry_count: int
    estimated_cost: float
    input_hash: str
    policy_version: str | None
    workflow_run_id: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "task_class": self.task_class,
            "node_name": self.node_name,
            "deployment_name": self.deployment_name,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "cached_hit": self.cached_hit,
            "latency_ms": self.latency_ms,
            "retry_count": self.retry_count,
            "estimated_cost": self.estimated_cost,
            "input_hash": self.input_hash,
            "policy_version": self.policy_version,
            "workflow_run_id": self.workflow_run_id,
        }


def append_cost_ledger_entry(
    ledger: list[dict[str, Any]],
    *,
    entry: CostLedgerEntry,
) -> tuple[list[dict[str, Any]], float]:
    updated = [*ledger, entry.as_dict()]
    total_cost = round(sum(float(item.get("estimated_cost", 0.0) or 0.0) for item in updated), 6)
    record_workflow_cost(
        cost_usd=entry.estimated_cost,
        workflow_run_id=entry.workflow_run_id,
        task_class=entry.task_class,
        node_name=entry.node_name,
        deployment_name=entry.deployment_name,
        cached_hit=entry.cached_hit,
    )
    return updated, total_cost


def ledger_rollup(ledger: list[dict[str, Any]]) -> dict[str, Any]:
    total_cost = round(sum(float(item.get("estimated_cost", 0.0) or 0.0) for item in ledger), 6)
    total_tokens = sum(int(item.get("total_tokens", 0) or 0) for item in ledger)
    cache_hits = sum(1 for item in ledger if item.get("cached_hit"))
    return {
        "entry_count": len(ledger),
        "total_cost": total_cost,
        "total_tokens": total_tokens,
        "cache_hits": cache_hits,
    }
