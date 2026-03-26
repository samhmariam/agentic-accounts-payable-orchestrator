from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Any, Iterator

from opentelemetry import trace
from opentelemetry.propagate import extract
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio, ALWAYS_OFF
from opentelemetry.trace import Span, Status, StatusCode

from aegisap.observability.context import (
    WorkflowObservabilityContext,
    get_observability_context,
    make_workflow_observability_context,
    update_observability_context,
)
from aegisap.observability.metrics import record_node_duration, record_workflow_duration
from aegisap.security.config import load_security_config

TRACER_NAME = "aegisap.observability"


def _build_provider() -> TracerProvider:
    config = load_security_config()
    sampler = (
        ParentBasedTraceIdRatio(config.trace_sample_ratio)
        if config.tracing_enabled
        else ALWAYS_OFF
    )
    return TracerProvider(sampler=sampler)


def configure_tracing() -> None:
    provider = trace.get_tracer_provider()
    if isinstance(provider, TracerProvider):
        return
    trace.set_tracer_provider(_build_provider())


def get_tracer():
    configure_tracing()
    return trace.get_tracer(TRACER_NAME)


def current_span() -> Span | None:
    span = trace.get_current_span()
    if span is None:
        return None
    span_context = span.get_span_context()
    if span_context is None or not span_context.is_valid:
        return None
    return span


def current_trace_id() -> str | None:
    span = current_span()
    if span is None:
        return None
    return format(span.get_span_context().trace_id, "032x")


def current_traceparent() -> str | None:
    span = current_span()
    if span is None:
        return None
    context = span.get_span_context()
    return f"00-{format(context.trace_id, '032x')}-{format(context.span_id, '016x')}-01"


def otel_parent_context(traceparent: str | None):
    if not traceparent:
        return None
    return extract({"traceparent": traceparent})


def set_span_attributes(attributes: dict[str, Any]) -> None:
    span = current_span()
    if span is None:
        return
    for key, value in attributes.items():
        if value is not None:
            span.set_attribute(key, value)


def add_span_event(name: str, attributes: dict[str, Any] | None = None) -> None:
    span = current_span()
    if span is None:
        return
    span.add_event(name, attributes=attributes or {})


def mark_span_failure(error: BaseException | str, *, failure_class: str | None = None) -> None:
    span = current_span()
    if span is None:
        return
    span.record_exception(error if isinstance(error, BaseException) else RuntimeError(str(error)))
    span.set_status(Status(StatusCode.ERROR, str(error)))
    if failure_class:
        span.set_attribute("aegis.failure_class", failure_class)


def make_trace_context(
    *,
    request_id: str,
    workflow_run_id: str | None = None,
    case_id: str | None = None,
    thread_id: str | None = None,
    checkpoint_id: str | None = None,
    traceparent: str | None = None,
) -> WorkflowObservabilityContext:
    return make_workflow_observability_context(
        request_id=request_id,
        workflow_run_id=workflow_run_id,
        case_id=case_id,
        thread_id=thread_id,
        checkpoint_id=checkpoint_id,
        traceparent=traceparent,
    )


def root_span_attributes(context: WorkflowObservabilityContext) -> dict[str, Any]:
    attributes = {
        "aegis.workflow_run_id": context.workflow_run_id,
        "aegis.thread_id": context.hashed_thread_id,
        "aegis.case_id": context.hashed_case_id,
        "aegis.state_version": context.state_version,
        "aegis.plan_version": context.plan_version,
        "aegis.policy_version": context.policy_version,
        "aegis.environment": context.environment,
        "aegis.deployment_revision": context.deployment_revision,
        "aegis.actor_type": context.actor_type,
        "aegis.outcome_type": context.outcome_type,
        "aegis.approval_status": context.approval_status,
    }
    metadata = context.metadata
    if metadata.get("task_class") is not None:
        attributes["aegis.task_class"] = metadata["task_class"]
    if metadata.get("routing_decision") is not None:
        attributes["aegis.routing_decision"] = metadata["routing_decision"]
    if metadata.get("model_deployment") is not None:
        attributes["aegis.model_deployment"] = metadata["model_deployment"]
    if metadata.get("cache_hit") is not None:
        attributes["aegis.cache_hit"] = metadata["cache_hit"]
    if metadata.get("workflow_cost_estimate") is not None:
        attributes["aegis.workflow_cost_estimate"] = metadata["workflow_cost_estimate"]
    return attributes


def node_span_attributes(
    *,
    node_name: str,
    node_attempt: int = 1,
    retry_count: int = 0,
    idempotent: bool = True,
    failure_class: str | None = None,
    evidence_count: int | None = None,
    checkpoint_loaded: bool | None = None,
    checkpoint_saved: bool | None = None,
    prompt_revision: str | None = None,
    model_name: str | None = None,
    retrieval_index_version: str | None = None,
) -> dict[str, Any]:
    return {
        "aegis.node_name": node_name,
        "aegis.node_attempt": node_attempt,
        "aegis.retry_count": retry_count,
        "aegis.idempotent": idempotent,
        "aegis.failure_class": failure_class,
        "aegis.evidence_count": evidence_count,
        "aegis.checkpoint_loaded": checkpoint_loaded,
        "aegis.checkpoint_saved": checkpoint_saved,
        "aegis.prompt_revision": prompt_revision,
        "aegis.model_name": model_name,
        "aegis.retrieval_index_version": retrieval_index_version,
    }


def business_outcome_attributes(
    *,
    recommendation_value_band: str | None = None,
    vendor_risk_status: str | None = None,
    po_match_status: str | None = None,
    human_review_required: bool | None = None,
    final_decision_type: str | None = None,
) -> dict[str, Any]:
    return {
        "aegis.recommendation_value_band": recommendation_value_band,
        "aegis.vendor_risk_status": vendor_risk_status,
        "aegis.po_match_status": po_match_status,
        "aegis.human_review_required": human_review_required,
        "aegis.final_decision_type": final_decision_type,
    }


@contextmanager
def start_observability_span(
    name: str,
    *,
    attributes: dict[str, Any] | None = None,
    context: WorkflowObservabilityContext | None = None,
    kind: trace.SpanKind = trace.SpanKind.INTERNAL,
) -> Iterator[Span]:
    tracer = get_tracer()
    parent_context = otel_parent_context(context.traceparent) if context else None
    start = time.perf_counter()
    with tracer.start_as_current_span(name, context=parent_context, kind=kind) as span:
        set_span_attributes(attributes or {})
        active = context or get_observability_context()
        if active is not None:
            trace_id = format(span.get_span_context().trace_id, "032x")
            active.trace_id = trace_id
            active.azure_trace_id = trace_id
            active.traceparent = current_traceparent()
            update_observability_context(
                trace_id=trace_id,
                azure_trace_id=trace_id,
                traceparent=active.traceparent,
            )
            set_span_attributes(root_span_attributes(active))
        try:
            yield span
        except Exception:
            mark_span_failure("span_failed")
            raise
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            attrs = attributes or {}
            if name == "aegis.workflow.run":
                record_workflow_duration(duration_ms, workflow_span=name, **attrs)
            else:
                record_node_duration(duration_ms, node_name=name, **attrs)


@contextmanager
def start_workflow_span(
    *,
    request_id: str,
    workflow_run_id: str,
    case_id: str | None = None,
    thread_id: str | None = None,
    checkpoint_id: str | None = None,
    traceparent: str | None = None,
) -> Iterator[WorkflowObservabilityContext]:
    context = make_trace_context(
        request_id=request_id,
        workflow_run_id=workflow_run_id,
        case_id=case_id,
        thread_id=thread_id,
        checkpoint_id=checkpoint_id,
        traceparent=traceparent,
    )
    with start_observability_span("aegis.workflow.run", context=context):
        context.trace_id = current_trace_id()
        context.traceparent = current_traceparent()
        update_observability_context(trace_id=context.trace_id, traceparent=context.traceparent)
        yield context
