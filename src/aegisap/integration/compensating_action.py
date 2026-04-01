"""Compensating action runner for AegisAP (Day 13).

When an integration call fails after all retries, AegisAP must execute a
compensating action to restore consistency — e.g., rolling back a partial
ERP entry or sending a failure notification.

A compensating action is the inverse of the original action.  AegisAP
maintains a registry of ``(action_name, compensator_fn)`` pairs and invokes
the compensator if the original action has been partially applied.

Usage::

    runner = CompensatingActionRunner()
    runner.register("post_invoice_to_erp", compensator=rollback_erp_invoice)

    with runner.guarded("post_invoice_to_erp", invoice_id="INV-001") as ctx:
        erp_client.post(ctx.payload)
        # If this raises, runner.compensate("post_invoice_to_erp", ...) is called
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Callable, Generator

log = logging.getLogger(__name__)


class CompensatingActionRunner:
    """Registry and executor of compensating actions."""

    def __init__(self) -> None:
        self._registry: dict[str, Callable[..., None]] = {}

    def register(
        self,
        action_name: str,
        compensator: Callable[..., None],
    ) -> None:
        """Register a compensating function for an action.

        Args:
            action_name: Logical name of the original action.
            compensator: Callable that accepts the same ``**kwargs`` as the
                         guarded block and performs the compensating work.
        """
        self._registry[action_name] = compensator

    def compensate(self, action_name: str, **kwargs: Any) -> None:
        """Execute the compensating action for ``action_name``.

        Silently logs and continues if no compensator is registered —
        this is intentional: an unregistered action has no known compensation.
        """
        fn = self._registry.get(action_name)
        if fn is None:
            log.warning(
                "No compensator registered for action '%s'", action_name)
            return
        try:
            fn(**kwargs)
            log.info("Compensating action '%s' completed successfully", action_name)
        except Exception:
            log.exception(
                "Compensating action '%s' itself failed — manual intervention required",
                action_name,
            )

    @contextmanager
    def guarded(
        self,
        action_name: str,
        **kwargs: Any,
    ) -> Generator[None, None, None]:
        """Context manager that runs the compensating action on exception.

        Usage::

            with runner.guarded("post_invoice_to_erp", invoice_id="INV-001"):
                erp_client.post(...)
        """
        try:
            yield
        except Exception:
            log.exception(
                "Action '%s' failed; triggering compensating action", action_name
            )
            self.compensate(action_name, **kwargs)
            raise
