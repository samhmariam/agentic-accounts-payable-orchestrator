#!/usr/bin/env python3
from __future__ import annotations

import argparse

from aegisap.training.labs import run_day2_from_day1_artifact


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Day 2 AegisAP workflow lab.")
    parser.add_argument(
        "--day1-artifact",
        default="build/day1/golden_thread_day1.json",
        help="Path to the Day 1 artifact JSON file.",
    )
    parser.add_argument(
        "--known-vendor",
        dest="known_vendor",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Override known-vendor status for the training run.",
    )
    parser.add_argument(
        "--artifact-name",
        default="golden_thread_day2",
        help="Artifact file name under build/day2 without the .json suffix.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    artifact_path, payload = run_day2_from_day1_artifact(
        artifact_path=args.day1_artifact,
        known_vendor=args.known_vendor,
        artifact_name=args.artifact_name,
    )
    state = payload["workflow_state"]
    print(f"Day 2 complete: {artifact_path}")
    print(
        f"Workflow {state['workflow_id']} routed invoice {state['invoice_id']} "
        f"to '{state['route']}' with status '{state['status']}'."
    )


if __name__ == "__main__":
    main()
