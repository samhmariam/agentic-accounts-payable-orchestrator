#!/usr/bin/env python3
"""
scripts/generate_cto_trace_report.py
--------------------------------------
Runs all 17 gates and generates the CTO trace report.  Writes:
    build/day14/cto_trace_report.json

Requires all gate artifacts from build/day11/ through build/day14/ to exist.
Run the verify_* scripts first if you are in a live Azure environment.

Environment variables:
    AEGISAP_CORRELATION_ID   Optional correlation ID
"""
from __future__ import annotations

import datetime
import json
import os
import sys
import uuid
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

BUILD_DIR = _ROOT / "build" / "day14"


def main() -> int:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    correlation_id = os.environ.get(
        "AEGISAP_CORRELATION_ID", str(uuid.uuid4()))

    try:
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
    except ImportError as exc:
        print(f"ERROR: could not import gate modules: {exc}", file=sys.stderr)
        return 1

    gate_fns = [
        gate_security_posture, gate_eval_regression, gate_budget,
        gate_resume_safety, gate_aca_health, gate_refusal_safety,
        gate_delegated_identity, gate_obo_app_identity, gate_obo_exchange,
        gate_actor_binding, gate_private_network_static, gate_private_network_posture,
        gate_trace_correlation, gate_data_residency, gate_dlq_drain_health,
        gate_mcp_contract_integrity, gate_canary_regression,
        gate_stale_index_detection, gate_webhook_reliability, gate_rollback_readiness,
    ]

    results = []
    for fn in gate_fns:
        try:
            r = fn()
            results.append({
                "gate": r.name,
                "passed": r.passed,
                "detail": r.detail,
                "evidence": r.evidence,
            })
        except Exception as exc:
            results.append({
                "gate": fn.__name__,
                "passed": False,
                "detail": str(exc),
                "evidence": {},
            })

    all_passed = all(r["passed"] for r in results)
    pass_count = sum(1 for r in results if r["passed"])

    report = {
        "correlation_id": correlation_id,
        "all_gates_passed": all_passed,
        "passed": pass_count,
        "total": len(results),
        "gates": results,
        "run_at": datetime.datetime.utcnow().isoformat() + "Z",
    }

    path = BUILD_DIR / "cto_trace_report.json"
    path.write_text(json.dumps(report, indent=2))
    print(f"Wrote {path}")

    # Print table
    col_w = 38
    print(f"\n{'Gate':<{col_w}}  Status  Detail")
    print("-" * 80)
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        detail = r["detail"][:35] + \
            "..." if len(r["detail"]) > 38 else r["detail"]
        print(f"{r['gate']:<{col_w}}  {status:<6}  {detail}")
    print("-" * 80)
    print(f"\n{pass_count}/{len(results)} gates passed.")

    if not all_passed:
        print("\nFAIL: not all gates passed.", file=sys.stderr)
        return 1
    print("\nOK: all 17 gates passed. CTO trace report written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
