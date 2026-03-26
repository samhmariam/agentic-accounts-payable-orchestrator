#!/usr/bin/env python3
from __future__ import annotations

import argparse

from aegisap.day6.audit.decision_log import build_operator_summary
from aegisap.day6.state.models import ReviewOutcome
from aegisap.day5.workflow.training_runtime import load_thread_snapshot
from aegisap.training.postgres import build_store_from_env


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect the latest persisted Day 6 review state for a thread.")
    parser.add_argument(
        "--thread-id",
        required=True,
        help="Thread ID to inspect.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    snapshot = load_thread_snapshot(store=build_store_from_env(), thread_id=args.thread_id)
    review_payload = snapshot.get("review_outcome")
    if not review_payload:
        raise SystemExit(f"No Day 6 review outcome persisted for thread {args.thread_id}.")

    review = ReviewOutcome.model_validate(review_payload)
    print(f"Thread: {args.thread_id}")
    print(f"Outcome: {review.outcome}")
    print(f"Summary: {snapshot.get('review_summary') or build_operator_summary(review)}")
    print(f"Reasons: {len(review.reasons)}")


if __name__ == "__main__":
    main()
