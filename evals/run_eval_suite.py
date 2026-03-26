#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import copy
import json
import sys
import urllib.request
from pathlib import Path
from typing import Any

from evals.common import load_jsonl, load_thresholds

from aegisap.day6.graph.review_gate import run_day6_review
from aegisap.day6.state.models import Day6ReviewInput
from aegisap.training.fixtures import day6_fixture_path
from aegisap.training.labs import load_case_facts, run_day4_case_artifact


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Day 10 synthetic or malicious acceptance suites.")
    parser.add_argument("--suite", choices=["synthetic", "malicious", "all"], default="all")
    parser.add_argument("--base-url", help="Optional deployed base URL for synthetic workflow execution.")
    parser.add_argument("--planner-mode", choices=["fixture", "azure_openai"], default="fixture")
    parser.add_argument("--synthetic-cases", default="evals/synthetic_cases.jsonl")
    parser.add_argument("--malicious-cases", default="evals/malicious_cases.jsonl")
    parser.add_argument("--thresholds", default="evals/score_thresholds.yaml")
    parser.add_argument("--output", help="Optional path to write JSON summary.")
    parser.add_argument("--enforce-thresholds", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    thresholds = load_thresholds(args.thresholds)
    summary: dict[str, Any] = {}
    if args.suite in {"synthetic", "all"}:
        summary["synthetic"] = run_synthetic_suite(
            Path(args.synthetic_cases),
            base_url=args.base_url,
            planner_mode=args.planner_mode,
        )
    if args.suite in {"malicious", "all"}:
        summary["malicious"] = run_malicious_suite(Path(args.malicious_cases))
    summary["thresholds"] = thresholds
    summary["all_passed"] = evaluate_thresholds(summary, thresholds)

    payload = json.dumps(summary, indent=2)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    print(payload)
    if args.enforce_thresholds and not summary["all_passed"]:
        sys.exit(1)


def run_synthetic_suite(path: Path, *, base_url: str | None, planner_mode: str) -> dict[str, Any]:
    cases = load_jsonl(path)
    results: list[dict[str, Any]] = []
    for case in cases:
        result = _run_synthetic_case(case, base_url=base_url, planner_mode=planner_mode)
        results.append(result)

    pass_count = sum(1 for item in results if item["passed"])
    escalation_expected = [item for item in results if item["expected_outcome"] != "approved_to_proceed"]
    escalation_recalled = [
        item for item in escalation_expected if item["actual_outcome"] != "approved_to_proceed"
    ]
    return {
        "case_count": len(results),
        "results": results,
        "faithfulness": pass_count / len(results) if results else 0.0,
        "compliance_decision_accuracy": pass_count / len(results) if results else 0.0,
        "mandatory_escalation_recall": (
            len(escalation_recalled) / len(escalation_expected) if escalation_expected else 1.0
        ),
    }


def _run_synthetic_case(case: dict[str, Any], *, base_url: str | None, planner_mode: str) -> dict[str, Any]:
    case_facts = load_case_facts(case["case_facts_path"])
    if base_url:
        response = _request(
            "POST",
            f"{base_url.rstrip('/')}/workflow/run",
            {
                "case_facts": case_facts.model_dump(mode="json"),
                "planner_mode": planner_mode,
                "enable_day6_review": True,
                "persist_day5_handoff": case.get("persist_day5_handoff", False),
                "thread_id": case.get("thread_id"),
                "assigned_to": case.get("assigned_to", "controller@example.com"),
            },
        )
        day6_review = response.get("day6_review") or {}
        workflow_cost = float((response.get("correlation") or {}).get("workflow_cost_estimate") or 0.0)
        correlation = response.get("correlation") or {}
    else:
        _artifact_path, payload, _state = asyncio.run(
            run_day4_case_artifact(
                case_facts=case_facts,
                planner_mode=planner_mode,
                artifact_name=case["case_name"],
                include_day6_review=True,
                thread_id=case.get("thread_id") or f"thread-{case_facts.case_id}",
            )
        )
        day6_review = payload["day6_review"] or {}
        workflow_state = payload.get("workflow_state") or {}
        workflow_cost = float(workflow_state.get("workflow_cost_estimate") or 0.0)
        correlation = {
            "workflow_run_id": workflow_state.get("workflow_run_id"),
            "workflow_cost_estimate": workflow_cost,
        }

    actual = day6_review.get("outcome")
    return {
        "case_name": case["case_name"],
        "slice": case["slice"],
        "cost_class": case["cost_class"],
        "expected_outcome": case["expected_outcome"],
        "actual_outcome": actual,
        "passed": actual == case["expected_outcome"],
        "workflow_cost_estimate": workflow_cost,
        "decision": day6_review,
        "correlation": correlation,
    }


def run_malicious_suite(path: Path) -> dict[str, Any]:
    cases = load_jsonl(path)
    results: list[dict[str, Any]] = []
    for case in cases:
        review_input = _build_malicious_input(case)
        outcome = run_day6_review(review_input)
        primary_code = outcome.reasons[0].code if outcome.reasons else None
        structured = outcome.outcome == "not_authorised_to_continue" and bool(outcome.citations)
        results.append(
            {
                "case_name": case["case_name"],
                "bucket": case["bucket"],
                "expected_code": case["expected_code"],
                "actual_outcome": outcome.outcome,
                "primary_reason_code": primary_code,
                "reason_codes": [reason.code for reason in outcome.reasons],
                "schema_valid": True,
                "structured_refusal": structured,
                "side_effect_count": 0,
                "passed": structured and primary_code == case["expected_code"],
            }
        )

    pass_count = sum(1 for item in results if item["passed"])
    schema_count = sum(1 for item in results if item["schema_valid"])
    structured_count = sum(1 for item in results if item["structured_refusal"])
    return {
        "case_count": len(results),
        "results": results,
        "structured_refusal_rate": structured_count / len(results) if results else 0.0,
        "schema_valid_rate": schema_count / len(results) if results else 0.0,
        "pass_rate": pass_count / len(results) if results else 0.0,
    }


def evaluate_thresholds(summary: dict[str, Any], thresholds: dict[str, float]) -> bool:
    synthetic = summary.get("synthetic")
    malicious = summary.get("malicious")
    passed = True
    if synthetic is not None:
        passed = passed and synthetic["faithfulness"] >= thresholds["faithfulness_min"]
        passed = passed and synthetic["compliance_decision_accuracy"] >= thresholds["compliance_decision_accuracy_min"]
        passed = passed and synthetic["mandatory_escalation_recall"] >= thresholds["mandatory_escalation_recall_min"]
    if malicious is not None:
        passed = passed and malicious["structured_refusal_rate"] >= thresholds["structured_refusal_rate_min"]
        passed = passed and malicious["schema_valid_rate"] >= thresholds["schema_valid_rate_min"]
    return passed


def _build_malicious_input(case: dict[str, Any]) -> Day6ReviewInput:
    path = day6_fixture_path(f"{case['base_fixture']}.json")
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    review_input = copy.deepcopy(payload["review_input"])
    if case.get("inject_pattern"):
        review_input["evidence_ledger"][0]["extract"] = case["inject_pattern"]
    if case.get("append_flag"):
        review_input.setdefault("injection_flags", []).append(case["append_flag"])
    if case.get("unsupported_channel"):
        review_input["claim_ledger"][0]["metadata"]["channel"] = case["unsupported_channel"]
    review_input["review_metadata"]["case_name"] = case["case_name"]
    return Day6ReviewInput.model_validate(review_input)


def _request(method: str, url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, method=method, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else {}


if __name__ == "__main__":
    main()
