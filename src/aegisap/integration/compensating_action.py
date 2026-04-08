"""Compensating action runner for AegisAP (Day 13)."""

from __future__ import annotations

import inspect
import logging
from typing import Any, Awaitable, Callable

log = logging.getLogger(__name__)

Compensator = Callable[[str, dict[str, Any]], Awaitable[dict[str, Any] | None] | dict[str, Any] | None]


class CompensatingActionRunner:
    """Registry and executor of compensating actions."""

    def __init__(self) -> None:
        self._registry: dict[str, Compensator] = {}

    def register(
        self,
        action_name: str,
        compensator: Compensator | None = None,
    ) -> Callable[[Compensator], Compensator] | Compensator:
        """Register a compensator directly or as a decorator."""

        def decorator(fn: Compensator) -> Compensator:
            self._registry[action_name] = fn
            return fn

        if compensator is not None:
            return decorator(compensator)
        return decorator

    async def compensate(
        self,
        message_id: str,
        payload: dict[str, Any] | None = None,
        classification: str | None = None,
    ) -> dict[str, Any] | None:
        if not classification:
            raise ValueError("classification is required for compensation.")
        fn = self._registry.get(classification)
        if fn is None:
            raise KeyError(classification)
        result = fn(message_id, payload or {})
        if inspect.isawaitable(result):
            return await result
        return result

    def guarded(self, classification: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator that runs the compensator when the wrapped callable fails."""

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            if inspect.iscoroutinefunction(fn):

                async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                    try:
                        return await fn(*args, **kwargs)
                    except Exception:
                        log.exception("Action '%s' failed; triggering compensating action", classification)
                        try:
                            await self.compensate("guarded-call", {}, classification)
                        except Exception:
                            log.exception(
                                "Compensating action '%s' failed — manual intervention required",
                                classification,
                            )
                        raise

                return async_wrapper

            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    log.exception("Action '%s' failed; triggering compensating action", classification)
                    raise

            return sync_wrapper

        return decorator
