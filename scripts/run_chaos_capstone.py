#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write the Day 14 chaos-capstone drill artifacts.")
    parser.add_argument(
        "--out-dir",
        default=str(_ROOT / "build" / "day14"),
        help="Directory where the Day 14 chaos-capstone artifacts should be written.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from aegisap.training.chaos import build_chaos_capstone_artifacts

    result = build_chaos_capstone_artifacts(out_dir=args.out_dir)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
