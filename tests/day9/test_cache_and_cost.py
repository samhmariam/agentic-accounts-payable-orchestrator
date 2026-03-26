from __future__ import annotations

from aegisap.cache.cache_policy import build_cache_key, evaluate_cache_policy
from aegisap.cost.cost_ledger import CostLedgerEntry, append_cost_ledger_entry, ledger_rollup


def test_cache_policy_bypasses_high_risk_cases(monkeypatch) -> None:
    monkeypatch.setenv("AEGISAP_CACHE_ENABLED", "true")

    decision = evaluate_cache_policy(
        task_class="retrieve_summarise",
        risk_flags=["high_value"],
        retrieval_confidence=0.96,
    )

    assert decision.allowed is False
    assert decision.bypass_reason == "high_risk_case"


def test_cache_key_includes_stable_dimensions() -> None:
    first = build_cache_key(
        tenant="tenant-a",
        task_class="retrieve_summarise",
        policy_version="v1",
        source_snapshot_hash="src-1",
        prompt_text="summarise policy",
    )
    second = build_cache_key(
        tenant="tenant-a",
        task_class="retrieve_summarise",
        policy_version="v1",
        source_snapshot_hash="src-1",
        prompt_text="summarise policy",
    )

    assert first == second


def test_cost_ledger_rolls_up_workflow_cost() -> None:
    ledger, total = append_cost_ledger_entry(
        [],
        entry=CostLedgerEntry(
            task_class="extract",
            node_name="invoice_extraction",
            deployment_name="gpt-4.1-mini",
            prompt_tokens=100,
            completion_tokens=20,
            total_tokens=120,
            cached_hit=False,
            latency_ms=220,
            retry_count=0,
            estimated_cost=0.0042,
            input_hash="abc",
            policy_version="v1",
            workflow_run_id="wf-1",
        ),
    )

    assert total == 0.0042
    assert ledger_rollup(ledger)["total_tokens"] == 120
