from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from aegisap.security.config import load_security_config

TaskClass = Literal[
    "extract",
    "classify",
    "retrieve_summarise",
    "plan",
    "compliance_review",
    "reflection",
    "final_render",
]


@dataclass(slots=True)
class RoutingPolicy:
    light_model_deployment: str
    strong_model_deployment: str
    fallback_model_deployment: str
    cache_allowed: bool
    cache_mode: str
    max_retries: int
    timeout_budget_ms: int


@dataclass(slots=True)
class ModelRouteDecision:
    task_class: TaskClass
    deployment_name: str
    deployment_tier: Literal["light", "strong"]
    cache_allowed: bool
    cache_mode: str
    max_retries: int
    timeout_budget_ms: int
    fallback_model_deployment: str
    reason: str
    risk_flags: list[str] = field(default_factory=list)
    escalated: bool = False

    def to_metadata(self) -> dict[str, object]:
        return {
            "task_class": self.task_class,
            "routing_decision": self.reason,
            "model_deployment": self.deployment_name,
            "deployment_tier": self.deployment_tier,
            "cache_allowed": self.cache_allowed,
            "cache_mode": self.cache_mode,
            "risk_flags": self.risk_flags,
            "routing_escalated": self.escalated,
        }


def build_default_routing_policy() -> RoutingPolicy:
    config = load_security_config()
    light = config.light_model_deployment or "gpt-4.1-mini"
    strong = config.strong_model_deployment or "gpt-4.1"
    return RoutingPolicy(
        light_model_deployment=light,
        strong_model_deployment=strong,
        fallback_model_deployment=strong,
        cache_allowed=config.cache_enabled,
        cache_mode="semantic",
        max_retries=3,
        timeout_budget_ms=6_000,
    )


def route_task(
    *,
    task_class: TaskClass,
    risk_flags: list[str] | None = None,
    retrieval_confidence: float | None = None,
    evidence_conflict_count: int = 0,
    policy: RoutingPolicy | None = None,
    final_render_sensitive: bool = False,
) -> ModelRouteDecision:
    active_policy = policy or build_default_routing_policy()
    risk_flags = list(dict.fromkeys(risk_flags or []))
    escalators = {
        "high_value",
        "missing_po",
        "bank_details_changed",
        "new_vendor",
        "cross_border_tax",
        "multi_currency",
        "reflection_triggered",
        "prior_refusal",
        "contradictory_evidence",
        "authoritative_source_missing",
    }
    has_escalator = evidence_conflict_count > 0 or bool(escalators.intersection(risk_flags))
    low_confidence = retrieval_confidence is not None and retrieval_confidence < 0.8

    cache_allowed = active_policy.cache_allowed and task_class in {"extract", "retrieve_summarise", "final_render"}

    if task_class in {"plan", "reflection", "compliance_review"}:
        return ModelRouteDecision(
            task_class=task_class,
            deployment_name=active_policy.strong_model_deployment,
            deployment_tier="strong",
            cache_allowed=False,
            cache_mode="bypass",
            max_retries=active_policy.max_retries,
            timeout_budget_ms=max(active_policy.timeout_budget_ms, 8_000),
            fallback_model_deployment=active_policy.fallback_model_deployment,
            reason=f"{task_class}_defaults_to_strong",
            risk_flags=risk_flags,
            escalated=has_escalator,
        )

    if task_class == "final_render" and final_render_sensitive:
        return ModelRouteDecision(
            task_class=task_class,
            deployment_name=active_policy.strong_model_deployment,
            deployment_tier="strong",
            cache_allowed=False,
            cache_mode="bypass",
            max_retries=active_policy.max_retries,
            timeout_budget_ms=active_policy.timeout_budget_ms,
            fallback_model_deployment=active_policy.fallback_model_deployment,
            reason="sensitive_final_render_requires_strong",
            risk_flags=risk_flags,
            escalated=True,
        )

    if has_escalator or low_confidence:
        return ModelRouteDecision(
            task_class=task_class,
            deployment_name=active_policy.strong_model_deployment,
            deployment_tier="strong",
            cache_allowed=False,
            cache_mode="bypass",
            max_retries=active_policy.max_retries,
            timeout_budget_ms=active_policy.timeout_budget_ms,
            fallback_model_deployment=active_policy.fallback_model_deployment,
            reason="risk_escalator_selected_strong_model",
            risk_flags=risk_flags,
            escalated=True,
        )

    return ModelRouteDecision(
        task_class=task_class,
        deployment_name=active_policy.light_model_deployment,
        deployment_tier="light",
        cache_allowed=cache_allowed,
        cache_mode=active_policy.cache_mode if cache_allowed else "bypass",
        max_retries=active_policy.max_retries,
        timeout_budget_ms=active_policy.timeout_budget_ms,
        fallback_model_deployment=active_policy.fallback_model_deployment,
        reason=f"{task_class}_selected_light_model",
        risk_flags=risk_flags,
        escalated=False,
    )
