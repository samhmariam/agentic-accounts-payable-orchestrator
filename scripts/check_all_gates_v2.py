#!/usr/bin/env python3
"""
scripts/check_all_gates_v2.py
------------------------------
Runs all 17 gates (Gates 1-6 from gates.py + Gates 7-17 from gates_v2.py)
and prints a formatted table.  Exits 1 if any gate fails.

Companion to scripts/check_all_gates.py which runs only Gates 1-6.

Usage:
    python scripts/check_all_gates_v2.py
    python scripts/check_all_gates_v2.py --json         # machine-readable output
    python scripts/check_all_gates_v2.py --fail-fast    # exit on first failure
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))


def _load_gates():
    from aegisap.deploy.gates import (
        gate_security_posture,
        gate_eval_regression,
        gate_budget,
        gate_resume_safety,
        gate_aca_health,
        gate_refusal_safety,
    )
    from aegisap.deploy.gates_v2 import (
        gate_delegated_identity,
        gate_obo_app_identity,
        gate_obo_exchange,
        gate_actor_binding,
        gate_private_network_static,
        gate_private_network_posture,
        gate_trace_correlation,
        gate_data_residency,
        gate_dlq_drain_health,
        gate_mcp_contract_integrity,
        gate_canary_regression,
        gate_stale_index_detection,
        gate_webhook_reliability,
        gate_rollback_readiness,
    )
    return [
        gate_security_posture,
        gate_eval_regression,
        gate_budget,
        gate_resume_safety,
        gate_aca_health,
        gate_refusal_safety,
        gate_delegated_identity,
        gate_obo_app_identity,
        gate_obo_exchange,
        gate_actor_binding,
        gate_private_network_static,
        gate_private_network_posture,
        gate_trace_correlation,
        gate_data_residency,
        gate_dlq_drain_health,
        gate_mcp_contract_integrity,
        gate_canary_regression,
        gate_stale_index_detection,
        gate_webhook_reliability,
        gate_rollback_readiness,
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run all 17 AegisAP deployment gates")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")
    parser.add_argument("--fail-fast", action="store_true",
                        help="Exit on first failure")
    args = parser.parse_args(argv)

    try:
        gate_fns = _load_gates()
    except ImportError as exc:
        print(f"ERROR: could not load gate modules: {exc}", file=sys.stderr)
        return 1

    results = []
    any_failed = False

    for fn in gate_fns:
        try:
            r = fn()
            entry = {
                "gate": r.name,
                "passed": r.passed,
                "detail": r.detail,
            }
        except Exception as exc:
            entry = {
                "gate": fn.__name__,
                "passed": False,
                "detail": str(exc),
            }

        results.append(entry)
        if not entry["passed"]:
            any_failed = True
            if args.fail_fast:
                break

    if args.json:
        print(json.dumps({
            "all_gates_passed": not any_failed,
            "passed": sum(1 for r in results if r["passed"]),
            "total": len(results),
            "gates": results,
        }, indent=2))
    else:
        col_w = 36
        print(f"\n{'Gate':<{col_w}}  Status  Detail")
        print("-" * 82)
        for r in results:
            status = "PASS" if r["passed"] else "FAIL"
            status_col = status
            detail = r["detail"]
            if len(detail) > 40:
                detail = detail[:37] + "..."
            print(f"{r['gate']:<{col_w}}  {status_col:<6}  {detail}")
        print("-" * 82)
        pass_count = sum(1 for r in results if r["passed"])
        print(f"\n{pass_count}/{len(results)} gates passed.\n")

    return 1 if any_failed else 0


if __name__ == "__main__":
    sys.exit(main())
