#!/usr/bin/env python3
"""CLI wrapper for the shared AegisAP Day 10 gate runner."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))
from aegisap.deploy.gates import GateResult, build_release_envelope, format_gate_row, run_all_gates


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="AegisAP pre-release gate runner")
    parser.add_argument(
        "--skip-deploy",
        action="store_true",
        help="Skip the ACA health probe (useful in CI before deployment step)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Path to write gate results JSON (e.g. build/day10/release_envelope.json)",
    )
    args = parser.parse_args(argv)

    print("AegisAP pre-release gates")
    print("=" * 60)
    results = run_all_gates(skip_deploy=args.skip_deploy)
    all_passed = True
    for r in results:
        print(format_gate_row(r))
        if not r.passed:
            all_passed = False
    print("=" * 60)
    print(f"Overall: {'PASS' if all_passed else 'FAIL'}")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        payload = build_release_envelope(results)
        args.out.write_text(json.dumps(payload, indent=2))
        print(f"Gate results written to {args.out}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
