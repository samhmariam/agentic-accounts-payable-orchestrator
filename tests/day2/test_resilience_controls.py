from __future__ import annotations

from aegisap.observability.retry_policy import RetryPolicy, execute_with_retry
from aegisap.resilience.backpressure import evaluate_backpressure


def test_retry_policy_retries_quota_throttle_for_idempotent_extract() -> None:
    attempts = {"count": 0}

    def flaky_extract() -> str:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("429 quota throttle from azure openai")
        return "ok"

    result = execute_with_retry(
        flaky_extract,
        policy=RetryPolicy(max_attempts=3, initial_backoff_ms=0, max_backoff_ms=0, deadline_ms=1_000),
        node_name="invoice_extraction",
        dependency_name="azure_openai",
        idempotent=True,
        sleep_fn=lambda _seconds: None,
        random_fn=lambda: 0.5,
    )

    assert result == "ok"
    assert attempts["count"] == 3


def test_backpressure_queues_protected_paths_when_strong_tier_is_saturated(monkeypatch) -> None:
    monkeypatch.setenv("AEGISAP_BACKPRESSURE_ENABLED", "true")
    monkeypatch.setenv("AEGISAP_STRONG_MODEL_MAX_CONCURRENCY", "1")

    decision = evaluate_backpressure(
        task_class="plan",
        deployment_tier="strong",
        active_inflight=1,
    )

    assert decision.allow_execution is False
    assert decision.queue_required is True
    assert decision.queue_delay_ms == 250
    assert decision.reason == "protected_path_queued"


def test_backpressure_allows_low_risk_tasks_when_capacity_exists(monkeypatch) -> None:
    monkeypatch.setenv("AEGISAP_BACKPRESSURE_ENABLED", "true")
    monkeypatch.setenv("AEGISAP_CHEAP_MODEL_MAX_CONCURRENCY", "3")

    decision = evaluate_backpressure(
        task_class="extract",
        deployment_tier="light",
        active_inflight=1,
    )

    assert decision.allow_execution is True
    assert decision.queue_required is False
    assert decision.reason == "within_capacity"
