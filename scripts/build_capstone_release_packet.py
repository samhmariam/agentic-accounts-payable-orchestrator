#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

from aegisap.training.capstone import build_capstone_release_packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a capstone release packet for the AegisAP bootcamp.",
    )
    parser.add_argument("--trainee-id", required=True)
    parser.add_argument("--enhancement-category", required=True)
    parser.add_argument(
        "--release-envelope",
        default="build/day10/release_envelope.json",
        help="Path to the Day 10 release envelope.",
    )
    parser.add_argument(
        "--checkpoint-artifact",
        action="append",
        default=[],
        help="Checkpoint artifact to include. Repeat for multiple artifacts.",
    )
    parser.add_argument("--rollback-command", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument(
        "--out",
        default=None,
        help="Optional output path. Defaults to build/capstone/<trainee_id>/release_packet.json",
    )
    args = parser.parse_args(argv)

    path, _payload = build_capstone_release_packet(
        trainee_id=args.trainee_id,
        enhancement_category=args.enhancement_category,
        release_envelope_path=args.release_envelope,
        checkpoint_artifacts=args.checkpoint_artifact,
        rollback_command=args.rollback_command,
        summary=args.summary,
        out_path=args.out,
    )
    print(f"Capstone release packet written to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
