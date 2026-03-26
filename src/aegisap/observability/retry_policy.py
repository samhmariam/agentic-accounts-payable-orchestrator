from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, ParamSpec, TypeVar

from aegisap.observability.failure_classifier import classify_failure
from aegisap.observability.metrics import record_retry
from aegisap.observability.tracing import add_span_event, current_span, set_span_attributes

P = ParamSpec("P")
T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 3
    initial_backoff_ms: int = 200
    max_backoff_ms: int = 2_000
    jitter_ratio: float = 0.2
    deadline_ms: int = 5_000


TRANSIENT_STATUS_CODES = ("429", "500", "502", "503", "504")


def is_retryable_error(error: BaseException | str | None) -> bool:
    classification = classify_failure(error)
    if classification.retryable:
        return True
    text = str(error).lower() if error is not None else ""
    return any(code in text for code in TRANSIENT_STATUS_CODES)


def execute_with_retry(
    fn: Callable[P, T],
    *,
    policy: RetryPolicy,
    node_name: str,
    dependency_name: str,
    idempotent: bool,
    decision_reason_code: str | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
    random_fn: Callable[[], float] = random.random,
    args: tuple | None = None,
    kwargs: dict | None = None,
) -> T:
    if not idempotent:
        return fn(*(args or ()), **(kwargs or {}))

    started = time.perf_counter()
    last_error: BaseException | None = None
    for attempt in range(1, policy.max_attempts + 1):
        remaining_budget_ms = policy.deadline_ms - int((time.perf_counter() - started) * 1000)
        set_span_attributes(
            {
                "aegis.node_attempt": attempt,
                "aegis.retry_count": attempt - 1,
                "aegis.idempotent": idempotent,
            }
        )
        try:
            return fn(*(args or ()), **(kwargs or {}))
        except Exception as exc:
            last_error = exc
            classifier = classify_failure(exc, dependency_name=dependency_name)
            if attempt >= policy.max_attempts or remaining_budget_ms <= 0 or not is_retryable_error(exc):
                add_span_event(
                    "retry_aborted",
                    {
                        "error_class": classifier.reason,
                        "attempt_number": attempt,
                        "backoff_ms": 0,
                        "remaining_budget_ms": max(remaining_budget_ms, 0),
                        "dependency_name": dependency_name,
                        "decision_reason_code": decision_reason_code,
                    },
                )
                raise

            backoff_ms = min(policy.max_backoff_ms, policy.initial_backoff_ms * (2 ** (attempt - 1)))
            jittered = int(backoff_ms * (1 + ((random_fn() * 2) - 1) * policy.jitter_ratio))
            add_span_event(
                "retry_scheduled",
                {
                    "error_class": classifier.reason,
                    "attempt_number": attempt,
                    "backoff_ms": max(jittered, 0),
                    "remaining_budget_ms": max(remaining_budget_ms, 0),
                    "dependency_name": dependency_name,
                    "decision_reason_code": decision_reason_code,
                },
            )
            record_retry(
                dependency_name=dependency_name,
                node_name=node_name,
                failure_class=classifier.top_level,
                error_class=classifier.reason,
            )
            sleep_fn(max(jittered, 0) / 1000)

    assert last_error is not None
    raise last_error


def emit_timeout_budget_exhausted(
    *,
    dependency_name: str,
    attempt_number: int,
    remaining_budget_ms: int,
    decision_reason_code: str | None = None,
) -> None:
    add_span_event(
        "timeout_budget_exhausted",
        {
            "error_class": "timeout_budget_exhausted",
            "attempt_number": attempt_number,
            "backoff_ms": 0,
            "remaining_budget_ms": remaining_budget_ms,
            "dependency_name": dependency_name,
            "decision_reason_code": decision_reason_code,
        },
    )
    span = current_span()
    if span is not None:
        set_span_attributes({"aegis.failure_class": "dependency_failure"})
