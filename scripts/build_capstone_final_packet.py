#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

from aegisap.training.capstone import build_capstone_final_packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the Day 14 Capstone A final CAB packet for the AegisAP bootcamp.",
    )
    parser.add_argument("--trainee-id", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument(
        "--foundation-packet",
        default=None,
        help="Optional path to the Day 10 foundation release packet. Defaults to build/capstone/<trainee_id>/release_packet.json",
    )
    parser.add_argument(
        "--revert-proof",
        default="docs/curriculum/artifacts/day14/REVERT_PROOF.md",
        help="Path to the Day 14 Revert Proof artifact.",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Optional output path. Defaults to build/capstone/<trainee_id>/final_packet.json",
    )
    args = parser.parse_args(argv)

    path, _payload = build_capstone_final_packet(
        trainee_id=args.trainee_id,
        summary=args.summary,
        foundation_packet_path=args.foundation_packet,
        revert_proof_path=args.revert_proof,
        out_path=args.out,
    )
    print(f"Capstone final packet written to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
