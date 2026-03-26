from __future__ import annotations

import pytest

from aegisap.day5.workflow.side_effects import (
    IdempotentEffectRunner,
    SideEffectConflictError,
    build_payment_recommendation_effect_key,
)


class FakeStore:
    def __init__(self) -> None:
        self.effects: dict[str, dict] = {}

    def try_start_side_effect(
        self,
        *,
        effect_key: str,
        thread_id: str,
        checkpoint_id: str,
        effect_type: str,
        effect_payload_hash: str,
    ) -> bool:
        if effect_key in self.effects:
            return False
        self.effects[effect_key] = {
            "effect_key": effect_key,
            "effect_type": effect_type,
            "effect_result_json": {},
            "status": "pending",
            "thread_id": thread_id,
            "checkpoint_id": checkpoint_id,
            "effect_payload_hash": effect_payload_hash,
        }
        return True

    def get_side_effect(self, effect_key: str):
        effect = self.effects.get(effect_key)
        if effect is None:
            return None

        class Stored:
            effect_key = effect["effect_key"]
            effect_type = effect["effect_type"]
            effect_result_json = effect["effect_result_json"]
            status = effect["status"]

        return Stored()

    def complete_side_effect(self, *, effect_key: str, effect_result_json: dict) -> None:
        self.effects[effect_key]["effect_result_json"] = effect_result_json
        self.effects[effect_key]["status"] = "applied"

    def fail_side_effect(self, *, effect_key: str) -> None:
        self.effects[effect_key]["status"] = "failed"


def build_runner() -> tuple[FakeStore, IdempotentEffectRunner]:
    store = FakeStore()
    runner = IdempotentEffectRunner(store=store)  # type: ignore[arg-type]
    return store, runner


def build_effect_key() -> str:
    return build_payment_recommendation_effect_key(
        thread_id="thread-42",
        plan_version="v3",
    )


def build_payload() -> dict[str, str]:
    return {
        "supplier": "Asmara Trading",
        "invoice_number": "INV-991",
        "gross_amount": "19850.00",
        "currency": "GBP",
    }


def test_payment_recommendation_is_not_duplicated_on_resume() -> None:
    _store, runner = build_runner()
    effect_key = build_effect_key()
    payload = build_payload()

    first = runner.run(
        effect_key=effect_key,
        thread_id="thread-42",
        checkpoint_id="cp-9",
        effect_type="payment_recommendation",
        payload=payload,
        apply_fn=lambda p: {"recommendation_id": "pr-1001", "status": "ready"},
    )
    second = runner.run(
        effect_key=effect_key,
        thread_id="thread-42",
        checkpoint_id="cp-9",
        effect_type="payment_recommendation",
        payload=payload,
        apply_fn=lambda p: {"recommendation_id": "pr-9999", "status": "ready"},
    )

    assert first["deduplicated"] is False
    assert first["result"]["recommendation_id"] == "pr-1001"
    assert second["deduplicated"] is True
    assert second["result"]["recommendation_id"] == "pr-1001"


def test_inflight_duplicate_fails_fast_without_rerunning_side_effect() -> None:
    store, runner = build_runner()
    effect_key = build_effect_key()
    payload = build_payload()
    store.effects[effect_key] = {
        "effect_key": effect_key,
        "effect_type": "payment_recommendation",
        "effect_result_json": {},
        "status": "pending",
    }

    with pytest.raises(SideEffectConflictError, match="already in progress"):
        runner.run(
            effect_key=effect_key,
            thread_id="thread-42",
            checkpoint_id="cp-9",
            effect_type="payment_recommendation",
            payload=payload,
            apply_fn=lambda p: {"recommendation_id": "pr-should-not-run", "status": "ready"},
        )


def test_failed_side_effect_is_marked_failed_and_reraised() -> None:
    store, runner = build_runner()
    effect_key = build_effect_key()
    payload = build_payload()

    with pytest.raises(RuntimeError, match="boom"):
        runner.run(
            effect_key=effect_key,
            thread_id="thread-42",
            checkpoint_id="cp-9",
            effect_type="payment_recommendation",
            payload=payload,
            apply_fn=lambda p: (_ for _ in ()).throw(RuntimeError("boom")),
        )

    assert store.effects[effect_key]["status"] == "failed"
