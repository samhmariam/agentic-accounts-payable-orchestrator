from __future__ import annotations

import asyncio
import json
from pathlib import Path

from aegisap.day4.execution.task_registry import create_default_task_registry
from aegisap.day4.graph.day4_explicit_planning_graph import run_day4_explicit_planning_case
from aegisap.day6.graph.review_gate import run_day6_review_from_day4
from aegisap.training.day4_plans import build_training_plan
from aegisap.training.fixtures import golden_thread_path
from aegisap.training.labs import StaticPlanModel, load_case_facts, load_day6_review_input


def _dataset() -> list[dict]:
    path = Path("data/day8/eval/day8_regression_cases.jsonl")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _run_day4_fixture(path: str | Path):
    case_facts = load_case_facts(path)
    plan = build_training_plan(case_facts, plan_id=f"plan_{case_facts.case_id}")
    return asyncio.run(
        run_day4_explicit_planning_case(
            case_facts=case_facts,
            model=StaticPlanModel(plan),
            registry=create_default_task_registry(),
        )
    )


def test_day8_dataset_contains_required_buckets() -> None:
    buckets = {item["bucket"] for item in _dataset()}

    assert {
        "happy_path",
        "locale_mismatch",
        "missing_po",
        "known_vendor_stable",
        "vendor_bank_change",
        "contradictory_evidence",
        "policy_refusal",
        "pause_resume",
        "retrieval_timeout",
        "orchestration_bug",
        "high_value",
    }.issubset(buckets)


def test_fixture_backed_cases_match_expected_outcomes() -> None:
    happy = next(item for item in _dataset() if item["case_name"] == "happy_path_invoice")
    missing_po = next(item for item in _dataset() if item["case_name"] == "missing_po")

    happy_state = _run_day4_fixture(golden_thread_path("day4_case.json"))
    _, happy_review = run_day6_review_from_day4(happy_state, thread_id="thread-happy")
    assert happy_review.outcome == happy["expected_outcome_type"]

    missing_po_state = _run_day4_fixture("fixtures/day4/missing_po.json")
    _, missing_po_review = run_day6_review_from_day4(missing_po_state, thread_id="thread-missing-po")
    assert missing_po_review.outcome == missing_po["expected_outcome_type"]


def test_review_input_cases_match_expected_outcomes() -> None:
    contradictory = next(item for item in _dataset() if item["case_name"] == "contradictory_evidence")
    refusal = next(item for item in _dataset() if item["case_name"] == "policy_refusal")

    contradictory_input = load_day6_review_input(contradictory["fixture"])
    contradictory_review = run_day6_review_from_day4(
        _run_day4_fixture(golden_thread_path("day4_case.json")),
        thread_id=contradictory_input.thread_id,
    )[1]
    assert contradictory["expected_outcome_type"] in {"needs_human_review", contradictory_review.outcome}

    refusal_input = load_day6_review_input(refusal["fixture"])
    from aegisap.day6.graph.review_gate import run_day6_review

    refusal_review = run_day6_review(refusal_input)
    assert refusal_review.outcome == refusal["expected_outcome_type"]
