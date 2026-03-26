#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio

from aegisap.training.fixtures import golden_thread_path
from aegisap.training.labs import load_case_facts, run_day4_case_artifact


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Day 4 explicit planning lab.")
    parser.add_argument(
        "--case-facts",
        default=str(golden_thread_path("day4_case.json")),
        help="Path to the Day 4 case facts JSON file.",
    )
    parser.add_argument(
        "--planner-mode",
        choices=["fixture", "azure_openai"],
        default="fixture",
        help="Planner backend to use.",
    )
    parser.add_argument(
        "--artifact-name",
        default="golden_thread_day4",
        help="Artifact file name under build/day4 without the .json suffix.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    artifact_path, payload, state = asyncio.run(
        run_day4_case_artifact(
            case_facts=load_case_facts(args.case_facts),
            planner_mode=args.planner_mode,
            artifact_name=args.artifact_name,
        )
    )
    final_status = "recommendation_ready" if state.recommendation is not None else "manual_review_required"
    print(f"Day 4 complete: {artifact_path}")
    print(f"Planner mode: {args.planner_mode} | Outcome: {final_status}")
    if payload["validated_plan"] is not None:
        print(f"Plan ID: {payload['validated_plan']['plan_id']}")


if __name__ == "__main__":
    main()
