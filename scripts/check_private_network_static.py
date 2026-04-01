#!/usr/bin/env python3
"""
scripts/check_private_network_static.py
-----------------------------------------
Compiles all Bicep templates in ``infra/`` to ARM JSON via ``az bicep build``
and verifies that every AI-tier resource has ``publicNetworkAccess == "Disabled"``.

Writes: ``build/day12/static_bicep_analysis.json``

Does NOT require Azure credentials — Bicep compilation is a local operation.

Usage::

    python scripts/check_private_network_static.py
    python scripts/check_private_network_static.py --infra-root infra/
    python scripts/check_private_network_static.py --json        # machine-readable

Exit codes:
    0  All AI resources have publicNetworkAccess=Disabled (or no AI resources found)
    1  One or more violations detected, or compilation failed
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

BUILD_DIR = _ROOT / "build" / "day12"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Static Bicep network-policy checker for AegisAP"
    )
    parser.add_argument(
        "--infra-root",
        default=str(_ROOT / "infra"),
        help="Directory containing *.bicep files (default: infra/)",
    )
    parser.add_argument(
        "--json",
        dest="emit_json",
        action="store_true",
        help="Print the analysis result as JSON to stdout",
    )
    args = parser.parse_args(argv)

    infra_root = Path(args.infra_root)
    if not infra_root.exists():
        print(
            f"ERROR: infra-root {infra_root} does not exist.", file=sys.stderr)
        return 1

    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    from aegisap.network.bicep_policy_checker import BicepPolicyChecker

    checker = BicepPolicyChecker(infra_root=infra_root)
    result = checker.run()
    report = result.to_dict()

    out_path = BUILD_DIR / "static_bicep_analysis.json"
    out_path.write_text(json.dumps(report, indent=2))

    if args.emit_json:
        print(json.dumps(report, indent=2))
        return 0 if result.all_passed else 1

    # Human-readable output
    n_files = len(result.bicep_files_compiled)
    n_checked = result.resources_checked
    n_violations = len(result.violations)

    if result.error:
        print(f"ERROR: {result.error}")
        print(f"\nArtifact written to: {out_path}")
        return 1

    print(f"Bicep files compiled : {n_files}")
    print(f"AI resources checked : {n_checked}")
    print(f"Violations           : {n_violations}")

    if result.violations:
        print("\nViolations:")
        for v in result.violations:
            print(
                f"  [{v.resource_type}] {v.resource} — {v.violation}  (from {v.bicep_source})")
        print(f"\nArtifact written to: {out_path}")
        return 1

    print(f"\nAll AI resources have publicNetworkAccess=Disabled. ✓")
    print(f"Artifact written to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
