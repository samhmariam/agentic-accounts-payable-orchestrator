#!/usr/bin/env python3
from __future__ import annotations

import argparse

from aegisap.training.fixtures import golden_thread_path
from aegisap.training.labs import run_day1_fixture, run_day1_live


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Day 1 AegisAP intake lab.")
    parser.add_argument(
        "--package",
        default=str(golden_thread_path("package.json")),
        help="Path to an invoice package JSON file.",
    )
    parser.add_argument(
        "--candidate",
        default=str(golden_thread_path("candidate.json")),
        help="Path to an extracted candidate JSON file for fixture mode.",
    )
    parser.add_argument(
        "--mode",
        choices=["fixture", "live"],
        default="fixture",
        help="Use fixture candidate input or live Azure OpenAI extraction.",
    )
    parser.add_argument(
        "--artifact-name",
        default="golden_thread_day1",
        help="Artifact file name under build/day1 without the .json suffix.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode == "live":
        artifact_path, payload = run_day1_live(
            package_path=args.package,
            artifact_name=args.artifact_name,
        )
    else:
        artifact_path, payload = run_day1_fixture(
            package_path=args.package,
            candidate_path=args.candidate,
            artifact_name=args.artifact_name,
        )

    canonical = payload["canonical_invoice"]
    print(f"Day 1 complete: {artifact_path}")
    print(
        f"Invoice {canonical['invoice_number']} from {canonical['supplier_name']} "
        f"canonicalized in {payload['mode']} mode."
    )


if __name__ == "__main__":
    main()
