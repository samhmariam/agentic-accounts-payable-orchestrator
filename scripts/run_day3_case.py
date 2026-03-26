#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from aegisap.training.fixtures import golden_thread_path
from aegisap.training.labs import run_day3_case_artifact


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Day 3 retrieval and authority lab.")
    parser.add_argument(
        "--invoice",
        default=str(golden_thread_path("day3_invoice.json")),
        help="Path to the Day 3 invoice JSON file.",
    )
    parser.add_argument(
        "--retrieval-mode",
        choices=["fixture", "azure_search_live", "pgvector_fixture"],
        default="azure_search_live",
        help="Retrieval backend to use.",
    )
    parser.add_argument(
        "--artifact-name",
        default="golden_thread_day3",
        help="Artifact file name under build/day3 without the .json suffix.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    invoice = json.loads(Path(args.invoice).read_text(encoding="utf-8"))
    artifact_path, payload = run_day3_case_artifact(
        invoice=invoice,
        retrieval_mode=args.retrieval_mode,
        artifact_name=args.artifact_name,
    )
    decision = payload["workflow_state"]["agent_findings"]["decision"]
    print(f"Day 3 complete: {artifact_path}")
    print(
        f"Recommendation '{decision['recommendation']}' with next step "
        f"'{decision['next_step']}' using {args.retrieval_mode}."
    )


if __name__ == "__main__":
    main()
