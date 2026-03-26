from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

from aegisap.cache.cache_policy import build_cache_key, evaluate_cache_policy
from aegisap.cache.semantic_cache import InMemorySemanticCache
from aegisap.common.hashing import stable_sha256
from aegisap.cost.cost_ledger import CostLedgerEntry
from aegisap.observability.context import get_observability_context, update_observability_context
from aegisap.observability.metrics import (
    record_cache_event,
    record_estimated_cost,
    record_queue_delay,
    record_routing_decision,
    record_tokens,
)
from aegisap.observability.retry_policy import RetryPolicy, execute_with_retry
from aegisap.observability.tracing import add_span_event, node_span_attributes, set_span_attributes, start_observability_span
from aegisap.resilience.backpressure import evaluate_backpressure
from aegisap.routing.routing_policy import ModelRouteDecision, TaskClass, route_task
from aegisap.security.credentials import get_openai_client


@dataclass(slots=True)
class ModelInvocationRequest:
    task_class: TaskClass
    node_name: str
    system_instruction: str
    user_prompt: str
    prompt_revision: str
    policy_version: str | None = None
    risk_flags: list[str] = field(default_factory=list)
    retrieval_confidence: float | None = None
    evidence_conflict_count: int = 0
    final_render_sensitive: bool = False
    temperature: float = 0.0
    source_snapshot_hash: str = "stable"
    citation_hash: str = "none"
    metadata: dict[str, Any] = field(default_factory=dict)


@lru_cache(maxsize=1)
def _client():
    return get_openai_client()


@lru_cache(maxsize=1)
def _semantic_cache() -> InMemorySemanticCache:
    return InMemorySemanticCache()


class ModelGateway:
    _inflight_by_tier: dict[str, int] = {"light": 0, "strong": 0}

    def invoke_text(self, request: ModelInvocationRequest) -> tuple[str, ModelRouteDecision, CostLedgerEntry]:
        decision = route_task(
            task_class=request.task_class,
            risk_flags=request.risk_flags,
            retrieval_confidence=request.retrieval_confidence,
            evidence_conflict_count=request.evidence_conflict_count,
            final_render_sensitive=request.final_render_sensitive,
        )
        record_routing_decision(
            task_class=request.task_class,
            deployment_name=decision.deployment_name,
            deployment_tier=decision.deployment_tier,
            routing_decision=decision.reason,
        )
        update_observability_context(**decision.to_metadata())
        set_span_attributes(
            {
                "aegis.task_class": request.task_class,
                "aegis.routing_decision": decision.reason,
                "aegis.model_deployment": decision.deployment_name,
            }
        )
        add_span_event(
            "routing_decided",
            {
                "error_class": "none",
                "attempt_number": 1,
                "backoff_ms": 0,
                "remaining_budget_ms": decision.timeout_budget_ms,
                "dependency_name": "model_router",
                "decision_reason_code": decision.reason,
            },
        )
        if decision.escalated:
            add_span_event(
                "routing_escalated",
                {
                    "error_class": "risk_escalator",
                    "attempt_number": 1,
                    "backoff_ms": 0,
                    "remaining_budget_ms": decision.timeout_budget_ms,
                    "dependency_name": "model_router",
                    "decision_reason_code": decision.reason,
                },
            )

        pressure = evaluate_backpressure(
            task_class=request.task_class,
            deployment_tier=decision.deployment_tier,
            active_inflight=self._inflight_by_tier[decision.deployment_tier],
        )
        if pressure.queue_required:
            record_queue_delay(
                pressure.queue_delay_ms,
                task_class=request.task_class,
                deployment_tier=decision.deployment_tier,
            )
            add_span_event(
                "backpressure_deferred",
                {
                    "error_class": "capacity_pressure",
                    "attempt_number": 1,
                    "backoff_ms": pressure.queue_delay_ms,
                    "remaining_budget_ms": decision.timeout_budget_ms,
                    "dependency_name": "model_gateway",
                    "decision_reason_code": pressure.reason,
                },
            )
            if request.task_class in {"plan", "compliance_review", "reflection"}:
                add_span_event(
                    "capacity_downgrade_blocked",
                    {
                        "error_class": "capacity_pressure",
                        "attempt_number": 1,
                        "backoff_ms": pressure.queue_delay_ms,
                        "remaining_budget_ms": decision.timeout_budget_ms,
                        "dependency_name": "model_gateway",
                        "decision_reason_code": "protected_path_not_downgraded",
                    },
                )

        cache_decision = evaluate_cache_policy(
            task_class=request.task_class,
            risk_flags=request.risk_flags,
            retrieval_confidence=request.retrieval_confidence,
            evidence_conflict_count=request.evidence_conflict_count,
            evidence_fresh=request.metadata.get("evidence_fresh", True),
        )
        prompt = request.user_prompt
        cache_key = build_cache_key(
            tenant=request.metadata.get("tenant", "aegisap"),
            task_class=request.task_class,
            policy_version=request.policy_version,
            source_snapshot_hash=request.source_snapshot_hash,
            prompt_text=prompt,
        )
        if decision.cache_allowed and cache_decision.allowed:
            cached = _semantic_cache().get(cache_key)
            if cached is not None and cached.citation_hash == request.citation_hash:
                record_cache_event(
                    "hit",
                    task_class=request.task_class,
                    node_name=request.node_name,
                    deployment_name=decision.deployment_name,
                )
                add_span_event(
                    "cache_reused",
                    {
                        "error_class": "none",
                        "attempt_number": 1,
                        "backoff_ms": 0,
                        "remaining_budget_ms": decision.timeout_budget_ms,
                        "dependency_name": "semantic_cache",
                        "decision_reason_code": "cache_hit",
                    },
                )
                ledger_entry = self._ledger_entry(
                    request=request,
                    decision=decision,
                    prompt_tokens=0,
                    completion_tokens=0,
                    latency_ms=0,
                    retry_count=0,
                    estimated_cost=0.0,
                    cached_hit=True,
                    input_hash=stable_sha256(prompt),
                )
                update_observability_context(cache_hit=True)
                return cached.response_text, decision, ledger_entry
            record_cache_event(
                "miss",
                task_class=request.task_class,
                node_name=request.node_name,
                deployment_name=decision.deployment_name,
            )
        else:
            record_cache_event(
                "bypass",
                task_class=request.task_class,
                node_name=request.node_name,
                bypass_reason=cache_decision.bypass_reason,
            )
            add_span_event(
                "cache_bypassed",
                {
                    "error_class": cache_decision.bypass_reason or "cache_bypassed",
                    "attempt_number": 1,
                    "backoff_ms": 0,
                    "remaining_budget_ms": decision.timeout_budget_ms,
                    "dependency_name": "semantic_cache",
                    "decision_reason_code": cache_decision.bypass_reason or "cache_not_allowed",
                },
            )

        start = time.perf_counter()
        self._inflight_by_tier[decision.deployment_tier] += 1
        try:
            with start_observability_span(
                "dep.llm.call",
                attributes=node_span_attributes(
                    node_name=request.node_name,
                    idempotent=True,
                    prompt_revision=request.prompt_revision,
                    model_name=decision.deployment_name,
                ),
            ):
                response = execute_with_retry(
                    _client().chat.completions.create,
                    policy=RetryPolicy(
                        max_attempts=decision.max_retries,
                        initial_backoff_ms=250,
                        max_backoff_ms=1_000,
                        deadline_ms=decision.timeout_budget_ms,
                    ),
                    node_name=request.node_name,
                    dependency_name="azure_openai",
                    idempotent=True,
                    decision_reason_code=decision.reason,
                    kwargs={
                        "model": decision.deployment_name,
                        "messages": [
                            {"role": "system", "content": request.system_instruction},
                            {"role": "user", "content": request.user_prompt},
                        ],
                        "temperature": request.temperature,
                    },
                )
        finally:
            self._inflight_by_tier[decision.deployment_tier] = max(
                0,
                self._inflight_by_tier[decision.deployment_tier] - 1,
            )

        response_text = _extract_message_text(response)
        usage = getattr(response, "usage", None)
        prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0) if usage is not None else 0
        completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0) if usage is not None else 0
        total_tokens = prompt_tokens + completion_tokens
        estimated_cost = self._estimate_cost(
            deployment_tier=decision.deployment_tier,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
        latency_ms = int((time.perf_counter() - start) * 1000)
        record_tokens(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            node_name=request.node_name,
            model_name=decision.deployment_name,
            task_class=request.task_class,
        )
        record_estimated_cost(
            cost_usd=estimated_cost,
            node_name=request.node_name,
            model_name=decision.deployment_name,
            task_class=request.task_class,
        )
        ledger_entry = self._ledger_entry(
            request=request,
            decision=decision,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
            retry_count=max(decision.max_retries - 1, 0),
            estimated_cost=estimated_cost,
            cached_hit=False,
            input_hash=stable_sha256(prompt),
        )
        if decision.cache_allowed and cache_decision.allowed:
            _semantic_cache().put(
                key=cache_key,
                response_text=response_text,
                ttl_seconds=cache_decision.ttl_seconds,
                citation_hash=request.citation_hash,
            )
        update_observability_context(cache_hit=False)
        return response_text, decision, ledger_entry

    def _ledger_entry(
        self,
        *,
        request: ModelInvocationRequest,
        decision: ModelRouteDecision,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: int,
        retry_count: int,
        estimated_cost: float,
        cached_hit: bool,
        input_hash: str,
    ) -> CostLedgerEntry:
        context = get_observability_context()
        workflow_run_id = context.workflow_run_id if context is not None else "standalone"
        total_tokens = prompt_tokens + completion_tokens
        return CostLedgerEntry(
            task_class=request.task_class,
            node_name=request.node_name,
            deployment_name=decision.deployment_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cached_hit=cached_hit,
            latency_ms=latency_ms,
            retry_count=retry_count,
            estimated_cost=estimated_cost,
            input_hash=input_hash,
            policy_version=request.policy_version,
            workflow_run_id=workflow_run_id,
        )

    def _estimate_cost(
        self,
        *,
        deployment_tier: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        if deployment_tier == "strong":
            return round((prompt_tokens * 0.000005) + (completion_tokens * 0.000015), 6)
        return round((prompt_tokens * 0.0000015) + (completion_tokens * 0.000006), 6)


def _extract_message_text(response: Any) -> str:
    content = response.choices[0].message.content
    if isinstance(content, str):
        return content
    parts: list[str] = []
    for item in content or []:
        text = getattr(item, "text", None)
        if text:
            parts.append(text)
    return "".join(parts)
