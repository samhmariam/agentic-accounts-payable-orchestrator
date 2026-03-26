from __future__ import annotations

import pytest

from aegisap.observability.failure_classifier import classify_failure
from aegisap.observability.retry_policy import RetryPolicy, execute_with_retry, is_retryable_error


def test_failure_classifier_marks_timeouts_retryable() -> None:
    classified = classify_failure("upstream timeout from azure search", dependency_name="azure_ai_search")

    assert classified.top_level == "dependency_failure"
    assert classified.retryable is True


def test_retry_policy_retries_transient_idempotent_calls() -> None:
    attempts = {"count": 0}

    def flaky() -> str:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("429 temporary throttle")
        return "ok"

    result = execute_with_retry(
        flaky,
        policy=RetryPolicy(max_attempts=3, initial_backoff_ms=0, max_backoff_ms=0, deadline_ms=1_000),
        node_name="vendor_history_check",
        dependency_name="azure_ai_search",
        idempotent=True,
        sleep_fn=lambda _seconds: None,
        random_fn=lambda: 0.5,
    )

    assert result == "ok"
    assert attempts["count"] == 3


def test_retry_policy_does_not_retry_non_idempotent_calls() -> None:
    attempts = {"count": 0}

    def not_safe() -> str:
        attempts["count"] += 1
        raise RuntimeError("429 temporary throttle")

    with pytest.raises(RuntimeError):
        execute_with_retry(
            not_safe,
            policy=RetryPolicy(max_attempts=3, initial_backoff_ms=0, max_backoff_ms=0, deadline_ms=1_000),
            node_name="audit_write",
            dependency_name="postgres",
            idempotent=False,
            sleep_fn=lambda _seconds: None,
            random_fn=lambda: 0.5,
        )

    assert attempts["count"] == 1
    assert is_retryable_error("429 temporary throttle") is True
