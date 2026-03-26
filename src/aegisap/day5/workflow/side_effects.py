from __future__ import annotations

from collections.abc import Callable
from typing import Any

from aegisap.day5.persistence.durable_state_store import DurableStateStore
from aegisap.day5.state.checksum import compute_payload_checksum


class SideEffectConflictError(RuntimeError):
    pass


class IdempotentEffectRunner:
    """
    All irreversible effects pass through this wrapper.

    Policy:
    - compute stable effect key
    - reserve the effect key before executing external work
    - return prior result if the effect already completed
    - fail fast if another worker is still executing the same effect
    """

    def __init__(self, store: DurableStateStore) -> None:
        self.store = store

    def run(
        self,
        *,
        effect_key: str,
        thread_id: str,
        checkpoint_id: str,
        effect_type: str,
        payload: dict[str, Any],
        apply_fn: Callable[[dict[str, Any]], dict[str, Any]],
    ) -> dict[str, Any]:
        payload_hash = compute_payload_checksum(payload)
        started = self.store.try_start_side_effect(
            effect_key=effect_key,
            thread_id=thread_id,
            checkpoint_id=checkpoint_id,
            effect_type=effect_type,
            effect_payload_hash=payload_hash,
        )
        if not started:
            existing = self.store.get_side_effect(effect_key)
            if existing is not None and existing.status == "applied":
                return {
                    "deduplicated": True,
                    "result": existing.effect_result_json,
                }
            raise SideEffectConflictError(
                f"Side effect '{effect_key}' is already in progress or requires operator retry."
            )

        try:
            result = apply_fn(payload)
        except Exception:
            self.store.fail_side_effect(effect_key=effect_key)
            raise

        self.store.complete_side_effect(
            effect_key=effect_key,
            effect_result_json=result,
        )
        return {
            "deduplicated": False,
            "result": result,
        }


def build_payment_recommendation_effect_key(
    *,
    thread_id: str,
    plan_version: str,
    recommendation_kind: str = "payment_ready",
) -> str:
    return f"{thread_id}:{plan_version}:{recommendation_kind}"


def build_audit_entry_effect_key(
    *,
    thread_id: str,
    checkpoint_seq: int,
    audit_kind: str,
) -> str:
    return f"{thread_id}:{checkpoint_seq}:{audit_kind}"
