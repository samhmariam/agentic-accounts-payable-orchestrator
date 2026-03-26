from __future__ import annotations

from dataclasses import dataclass

from aegisap.security.config import load_security_config


@dataclass(slots=True)
class BackpressureDecision:
    allow_execution: bool
    queue_required: bool
    queue_delay_ms: int
    reason: str
    deployment_tier: str


def evaluate_backpressure(
    *,
    task_class: str,
    deployment_tier: str,
    active_inflight: int,
) -> BackpressureDecision:
    config = load_security_config()
    if not config.backpressure_enabled:
        return BackpressureDecision(True, False, 0, "backpressure_disabled", deployment_tier)

    limit = (
        config.strong_model_max_concurrency
        if deployment_tier == "strong"
        else config.cheap_model_max_concurrency
    )
    if active_inflight < limit:
        return BackpressureDecision(True, False, 0, "within_capacity", deployment_tier)

    protected = {"plan", "compliance_review", "reflection"}
    if task_class in protected:
        return BackpressureDecision(False, True, 250, "protected_path_queued", deployment_tier)
    return BackpressureDecision(False, True, 125, "capacity_pressure_queued", deployment_tier)
