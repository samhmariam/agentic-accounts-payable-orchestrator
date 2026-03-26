#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from evals.common import load_thresholds


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate workflow cost ceilings from an eval summary.")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--thresholds", default="evals/score_thresholds.yaml")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = json.loads(Path(args.summary).read_text(encoding="utf-8"))
    thresholds = load_thresholds(args.thresholds)
    failures: list[str] = []
    for result in summary.get("synthetic", {}).get("results", []):
        ceiling = (
            thresholds["clean_path_cost_max"]
            if result["cost_class"] == "clean"
            else thresholds["exception_path_cost_max"]
        )
        if float(result.get("workflow_cost_estimate", 0.0) or 0.0) > ceiling:
            failures.append(
                f"{result['case_name']} exceeded {ceiling:.2f} with {result['workflow_cost_estimate']}"
            )
    if failures:
        raise SystemExit("\n".join(failures))
    print(json.dumps({"status": "ok", "checked_cases": len(summary.get("synthetic", {}).get("results", []))}, indent=2))


if __name__ == "__main__":
    main()
