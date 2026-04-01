from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

_ROOT = Path(__file__).resolve().parents[3]


@dataclass
class GateResult:
    name: str
    passed: bool
    detail: str
    evidence: dict | None = None


def gate_security_posture() -> GateResult:
    try:
        from aegisap.security.posture import run_posture_check

        posture = run_posture_check()
        failures = [c.name for c in posture.checks if not c.passed]
        passed = posture.passed
        detail = "All checks passed." if passed else f"Failed: {', '.join(failures)}"
        return GateResult(
            name="security_posture",
            passed=passed,
            detail=detail,
            evidence={"checks": [c.name for c in posture.checks]},
        )
    except Exception as exc:
        return GateResult(name="security_posture", passed=False, detail=str(exc))


def gate_eval_regression() -> GateResult:
    try:
        from aegisap.observability.baseline import compare_to_baseline

        baseline_path = _ROOT / "build" / "day8" / "regression_baseline.json"
        if not baseline_path.exists():
            return GateResult(
                name="eval_regression",
                passed=False,
                detail="No regression baseline found. Run Day 8 notebook first.",
            )
        current = json.loads(baseline_path.read_text())
        deltas = compare_to_baseline(current)
        regressed = [d.metric for d in deltas if d.is_regression]
        passed = len(regressed) == 0
        detail = "No regressions." if passed else f"Regressed metrics: {', '.join(regressed)}"
        return GateResult(
            name="eval_regression",
            passed=passed,
            detail=detail,
            evidence={"regressed": regressed},
        )
    except Exception as exc:
        return GateResult(name="eval_regression", passed=False, detail=str(exc))


def gate_budget() -> GateResult:
    try:
        from aegisap.cost.budget_gate import check_budget

        report_path = _ROOT / "build" / "day9" / "routing_report.json"
        if not report_path.exists():
            return GateResult(
                name="budget",
                passed=False,
                detail="No routing_report.json found. Run Day 9 notebook first.",
            )
        report = json.loads(report_path.read_text())
        ledger = report.get("sample_ledger", [])
        daily_limit = float(os.environ.get("DAILY_BUDGET_USD", "5.0"))
        status = check_budget(ledger, daily_limit_usd=daily_limit)
        passed = status.within_budget
        detail = (
            f"${status.total_cost_usd:.6f} / ${status.daily_limit_usd:.2f} daily limit. "
            f"Projected: ${status.projected_daily_usd:.4f}"
        )
        return GateResult(
            name="budget",
            passed=passed,
            detail=detail,
            evidence=status.as_dict(),
        )
    except Exception as exc:
        return GateResult(name="budget", passed=False, detail=str(exc))


def gate_refusal_safety() -> GateResult:
    try:
        evals_path = _ROOT / "evals" / "malicious_cases.jsonl"
        if not evals_path.exists():
            return GateResult(
                name="refusal_safety",
                passed=False,
                detail="malicious_cases.jsonl not found.",
            )
        lines = [ln for ln in evals_path.read_text().splitlines()
                 if ln.strip()]
        total = len(lines)
        if total == 0:
            return GateResult(name="refusal_safety", passed=True, detail="No malicious cases file.")

        thresholds_path = _ROOT / "evals" / "score_thresholds.yaml"
        required_rate = 0.95
        if thresholds_path.exists():
            import yaml  # type: ignore[import-untyped]

            thresholds = yaml.safe_load(thresholds_path.read_text()) or {}
            required_rate = float(
                thresholds.get("structured_refusal_rate", {}).get("min", 0.95)
            )

        day6_path = _ROOT / "build" / "day6" / "golden_thread_day6.json"
        if not day6_path.exists():
            return GateResult(
                name="refusal_safety",
                passed=False,
                detail="Day 6 artifact not found. Run Day 6 notebook first.",
            )
        day6 = json.loads(day6_path.read_text())
        adv_results = day6.get("adversarial_summary", {})
        refusal_rate = float(adv_results.get("refusal_rate", 0.0))
        passed = refusal_rate >= required_rate
        detail = f"Refusal rate: {refusal_rate:.1%} (required >= {required_rate:.1%})"
        return GateResult(
            name="refusal_safety",
            passed=passed,
            detail=detail,
            evidence={"refusal_rate": refusal_rate, "required": required_rate},
        )
    except Exception as exc:
        return GateResult(name="refusal_safety", passed=False, detail=str(exc))


def gate_resume_safety() -> GateResult:
    try:
        day5_path = _ROOT / "build" / "day5" / "golden_thread_day5_resumed.json"
        if not day5_path.exists():
            return GateResult(
                name="resume_safety",
                passed=False,
                detail="Day 5 resumed artifact not found. Run Day 5 notebook first.",
            )
        day5 = json.loads(day5_path.read_text())
        duplicate_effects = day5.get("duplicate_side_effects", 0)
        passed = duplicate_effects == 0
        detail = (
            "No duplicate side effects."
            if passed
            else f"{duplicate_effects} duplicate side effect(s) detected."
        )
        return GateResult(
            name="resume_safety",
            passed=passed,
            detail=detail,
            evidence={"duplicate_side_effects": duplicate_effects},
        )
    except Exception as exc:
        return GateResult(name="resume_safety", passed=False, detail=str(exc))


def gate_aca_health(skip: bool = False) -> GateResult:
    if skip:
        return GateResult(name="aca_health", passed=True, detail="Skipped (--skip-deploy flag).")
    try:
        from aegisap.deploy.aca_client import AcaClient

        client = AcaClient.from_env()
        health = client.health_check()
        passed = health.is_ready
        detail = (
            f"Revision {health.latest_revision} @ {health.app_url} - "
            f"provision={health.provision_state}, HTTP={health.status_code}"
        )
        return GateResult(
            name="aca_health",
            passed=passed,
            detail=detail,
            evidence={
                "provision_state": health.provision_state,
                "status_code": health.status_code,
                "app_url": health.app_url,
            },
        )
    except KeyError as exc:
        return GateResult(
            name="aca_health",
            passed=False,
            detail=(
                f"Missing env var: {exc}. Set AZURE_SUBSCRIPTION_ID, "
                "AZURE_RESOURCE_GROUP, and AZURE_CONTAINER_APP_NAME."
            ),
        )
    except Exception as exc:
        return GateResult(name="aca_health", passed=False, detail=str(exc))


ALL_GATES: list[tuple[str, Callable[..., GateResult]]] = [
    ("security_posture", gate_security_posture),
    ("eval_regression", gate_eval_regression),
    ("budget", gate_budget),
    ("refusal_safety", gate_refusal_safety),
    ("resume_safety", gate_resume_safety),
    ("aca_health", gate_aca_health),
]


def run_all_gates(skip_deploy: bool = False) -> list[GateResult]:
    results: list[GateResult] = []
    for name, fn in ALL_GATES:
        if name == "aca_health":
            results.append(fn(skip=skip_deploy))
        else:
            results.append(fn())
    return results


# ---------------------------------------------------------------------------
# Days 11-14 gate re-exports (implemented in gates_v2)
# ---------------------------------------------------------------------------
try:
    from aegisap.deploy.gates_v2 import (  # noqa: F401
        gate_actor_binding,
        gate_canary_regression,
        gate_data_residency,
        gate_dead_letter_budget,
        gate_delegated_identity,
        gate_delegated_identity_contract,
        gate_dlq_drain_health,
        gate_mcp_contract_integrity,
        gate_obo_app_identity,
        gate_obo_exchange,
        gate_private_network_posture,
        gate_private_network_static,
        gate_rollback_readiness,
        gate_stale_index_detection,
        gate_trace_correlation,
        gate_webhook_reliability,
    )
except ImportError:  # gates_v2 not yet installed — graceful degradation
    pass


def build_release_envelope(results: list[GateResult]) -> dict:
    return {
        "all_passed": all(result.passed for result in results),
        "gates": [
            {
                "name": result.name,
                "passed": result.passed,
                "detail": result.detail,
                "evidence": result.evidence,
            }
            for result in results
        ],
    }


def format_gate_row(result: GateResult) -> str:
    icon = "PASS" if result.passed else "FAIL"
    return f"  [{icon}] {result.name:<20}  {result.detail}"
