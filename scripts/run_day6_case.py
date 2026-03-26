#!/usr/bin/env python3
from __future__ import annotations

import argparse

from aegisap.training.labs import (
    load_day6_review_input,
    run_day6_review_artifact_from_day4,
    run_day6_review_artifact_from_input,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Day 6 graceful refusal review gate.")
    parser.add_argument(
        "--day4-artifact",
        default="build/day4/golden_thread_day4.json",
        help="Path to a Day 4 artifact JSON file.",
    )
    parser.add_argument(
        "--review-input",
        default=None,
        help="Optional path to a Day 6 review input JSON file.",
    )
    parser.add_argument(
        "--thread-id",
        default="thread-golden-001",
        help="Thread ID used for the Day 6 review artifact.",
    )
    parser.add_argument(
        "--artifact-name",
        default="golden_thread_day6",
        help="Artifact file name under build/day6 without the .json suffix.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.review_input:
        artifact_path, _payload, review_outcome = run_day6_review_artifact_from_input(
            review_input=load_day6_review_input(args.review_input),
            artifact_name=args.artifact_name,
        )
    else:
        artifact_path, _payload, review_outcome = run_day6_review_artifact_from_day4(
            day4_artifact_path=args.day4_artifact,
            thread_id=args.thread_id,
            artifact_name=args.artifact_name,
        )

    print(f"Day 6 complete: {artifact_path}")
    print(f"Outcome: {review_outcome.outcome}")
    print(f"Summary: {review_outcome.decision_summary}")


if __name__ == "__main__":
    main()
