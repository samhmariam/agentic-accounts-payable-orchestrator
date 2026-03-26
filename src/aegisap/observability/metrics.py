from __future__ import annotations

from functools import lru_cache
from typing import Any

from opentelemetry import metrics


@lru_cache(maxsize=1)
def _meter():
    return metrics.get_meter("aegisap.observability")


@lru_cache(maxsize=1)
def workflow_run_counter():
    return _meter().create_counter(
        "aegis.workflow_runs",
        description="AegisAP workflow runs grouped by outcome and environment.",
    )


@lru_cache(maxsize=1)
def business_event_counter():
    return _meter().create_counter(
        "aegis.business_events",
        description="Business outcome and exception counters for AegisAP.",
    )


@lru_cache(maxsize=1)
def retry_counter():
    return _meter().create_counter(
        "aegis.retries",
        description="Retries by dependency, node, and classifier.",
    )


@lru_cache(maxsize=1)
def token_counter():
    return _meter().create_counter(
        "aegis.tokens",
        description="Prompt and completion tokens attributed to workflow nodes.",
    )


@lru_cache(maxsize=1)
def estimated_cost_counter():
    return _meter().create_counter(
        "aegis.estimated_cost_usd",
        unit="USD",
        description="Estimated model cost attributed to workflow nodes.",
    )


@lru_cache(maxsize=1)
def workflow_cost_counter():
    return _meter().create_counter(
        "aegis.workflow_cost_usd",
        unit="USD",
        description="Workflow-level estimated cost rollups for routed model usage.",
    )


@lru_cache(maxsize=1)
def cache_event_counter():
    return _meter().create_counter(
        "aegis.cache_events",
        description="Semantic cache hits, misses, and bypass decisions.",
    )


@lru_cache(maxsize=1)
def routing_decision_counter():
    return _meter().create_counter(
        "aegis.routing_decisions",
        description="Model routing decisions by task class and deployment tier.",
    )


@lru_cache(maxsize=1)
def queue_delay_histogram():
    return _meter().create_histogram(
        "aegis.queue_delay_ms",
        unit="ms",
        description="Queue or backpressure delay grouped by task class and tier.",
    )


@lru_cache(maxsize=1)
def workflow_duration_histogram():
    return _meter().create_histogram(
        "aegis.workflow_duration_ms",
        unit="ms",
        description="End-to-end workflow duration.",
    )


@lru_cache(maxsize=1)
def node_duration_histogram():
    return _meter().create_histogram(
        "aegis.node_duration_ms",
        unit="ms",
        description="Node and dependency duration.",
    )


@lru_cache(maxsize=1)
def resume_delay_histogram():
    return _meter().create_histogram(
        "aegis.resume_delay_ms",
        unit="ms",
        description="Delay between checkpoint pause and resume.",
    )


def record_workflow_run(*, value: int = 1, **attributes: Any) -> None:
    workflow_run_counter().add(value, attributes=_compact(attributes))


def record_business_event(name: str, *, value: int = 1, **attributes: Any) -> None:
    business_event_counter().add(value, attributes=_compact({"event_name": name, **attributes}))


def record_retry(*, value: int = 1, **attributes: Any) -> None:
    retry_counter().add(value, attributes=_compact(attributes))


def record_tokens(*, prompt_tokens: int = 0, completion_tokens: int = 0, **attributes: Any) -> None:
    compact = _compact(attributes)
    if prompt_tokens:
        token_counter().add(prompt_tokens, attributes={**compact, "token_type": "prompt"})
    if completion_tokens:
        token_counter().add(completion_tokens, attributes={**compact, "token_type": "completion"})


def record_estimated_cost(*, cost_usd: float, **attributes: Any) -> None:
    estimated_cost_counter().add(cost_usd, attributes=_compact(attributes))


def record_workflow_cost(*, cost_usd: float, **attributes: Any) -> None:
    workflow_cost_counter().add(cost_usd, attributes=_compact(attributes))


def record_cache_event(name: str, *, value: int = 1, **attributes: Any) -> None:
    cache_event_counter().add(value, attributes=_compact({"cache_event": name, **attributes}))


def record_routing_decision(*, value: int = 1, **attributes: Any) -> None:
    routing_decision_counter().add(value, attributes=_compact(attributes))


def record_workflow_duration(duration_ms: float, **attributes: Any) -> None:
    workflow_duration_histogram().record(duration_ms, attributes=_compact(attributes))


def record_node_duration(duration_ms: float, **attributes: Any) -> None:
    node_duration_histogram().record(duration_ms, attributes=_compact(attributes))


def record_resume_delay(duration_ms: float, **attributes: Any) -> None:
    resume_delay_histogram().record(duration_ms, attributes=_compact(attributes))


def record_queue_delay(duration_ms: float, **attributes: Any) -> None:
    queue_delay_histogram().record(duration_ms, attributes=_compact(attributes))


def _compact(attributes: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in attributes.items() if value is not None}
