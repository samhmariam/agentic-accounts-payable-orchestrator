from __future__ import annotations

from collections.abc import Callable
from time import perf_counter
from typing import Any, ParamSpec, TypeVar

from aegisap.common.clocks import utc_now_iso
from aegisap.day2.state import WorkflowState
from aegisap.domain.metrics import NodeMetric

P = ParamSpec("P")
T = TypeVar("T")


def append_metric(
    state: WorkflowState,
    *,
    node_name: str,
    started_at: str,
    finished_at: str,
    latency_ms: int,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    estimated_cost_usd: float = 0.0,
    outcome: str = "ok",
) -> None:
    metric = NodeMetric(
        node_name=node_name,
        started_at=started_at,
        finished_at=finished_at,
        latency_ms=latency_ms,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        estimated_cost_usd=estimated_cost_usd,
        outcome=outcome,
    )
    state.node_metrics.append(metric)
    state.total_tokens_prompt += prompt_tokens
    state.total_tokens_completion += completion_tokens
    state.total_cost_usd += estimated_cost_usd
    state.total_latency_ms += latency_ms
    state.last_updated_at = finished_at


def traced_node(node_name: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(fn: Callable[P, T]) -> Callable[P, T]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            if not args:
                raise ValueError("traced node expected WorkflowState as first argument")

            state = args[0]
            if not isinstance(state, WorkflowState):
                raise TypeError("traced node expected WorkflowState as first argument")

            started_at = utc_now_iso()
            start = perf_counter()
            outcome = "ok"
            try:
                result = fn(*args, **kwargs)
                return result
            except Exception:
                outcome = "error"
                raise
            finally:
                finished_at = utc_now_iso()
                latency_ms = int((perf_counter() - start) * 1000)
                append_metric(
                    state,
                    node_name=node_name,
                    started_at=started_at,
                    finished_at=finished_at,
                    latency_ms=latency_ms,
                    outcome=outcome,
                )
        return wrapper
    return decorator
