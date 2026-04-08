#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from aegisap.common.paths import repo_root
from aegisap.lab.review import build_review_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a principal review draft for a PR diff.")
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--head-ref", default="HEAD")
    parser.add_argument("--mode", choices=("shadow", "blocking"), default="shadow")
    parser.add_argument("--strategy-file", default="")
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    parser.add_argument("--telemetry-out", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root(__file__)
    payload = build_review_payload(
        repo_root=root,
        base_ref=args.base_ref,
        head_ref=args.head_ref,
        mode=args.mode,
        strategy_path=args.strategy_file or None,
    )

    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    out_md.write_text(payload["markdown"], encoding="utf-8")
    if args.telemetry_out:
        telemetry_path = Path(args.telemetry_out)
        telemetry_path.parent.mkdir(parents=True, exist_ok=True)
        telemetry_path.write_text(json.dumps(payload["telemetry"], indent=2), encoding="utf-8")
    print(payload["markdown"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
