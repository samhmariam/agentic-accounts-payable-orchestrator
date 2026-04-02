"""AegisAP acceptance gates for Days 11-14 (v2 gate set).

This module adds 11 new gates.  The original 6 gates (gates.py) are unchanged.
Day 14's ``check_all_gates_v2.py`` runs both sets.

Gate inventory:
    7.  gate_private_network_static      — Day 12: CI PR gate (static_bicep_analysis.json)
    8.  gate_private_network_posture     — Day 12: live staging gate (posture report)
    9.  gate_delegated_identity          — Day 11: OBO contract (3 sub-checks)
        gate_delegated_identity_contract — alias for gate 9
    10. gate_obo_app_identity            — Day 11: MI token sub-check
    11. gate_obo_exchange                — Day 11: MSAL OBO exchange sub-check
    12. gate_actor_binding               — Day 11: approver OID bound to Entra group
    13. gate_trace_correlation           — Day 14: correlation IDs + dual-sink (mode keyed to Day 12 posture)
    14. gate_data_residency              — Day 14: ARM API location check
    15. gate_webhook_reliability         — Day 13: webhook reliability report
    16. gate_dlq_drain_health            — Day 13: DLQ report exists + zero error rate
        gate_dead_letter_budget          — alias for gate 16
    17. gate_mcp_contract_integrity      — Day 13: MCP /capabilities contract + write-path tool
    18. gate_canary_regression           — Day 14: canary run passes all eval thresholds
    19. gate_stale_index_detection       — Day 12: AI Search index freshness (soft/warn)
    20. gate_rollback_readiness          — Day 14: last known-good revision locatable
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]


@dataclass
class GateResult:
    name: str
    passed: bool
    detail: str
    evidence: dict | None = None


def _artifact_is_training_only(data: dict) -> bool:
    note = str(data.get("note", "")).upper()
    return (
        data.get("training_artifact") is True
        or data.get("authoritative_evidence") is False
        or data.get("execution_tier") == 1
        or note.startswith("STUB")
        or "TRAINING_ONLY" in note
    )


def _require_authoritative_evidence(
    *,
    gate_name: str,
    data: dict,
    remediation: str,
) -> GateResult | None:
    if not _artifact_is_training_only(data):
        return None
    return GateResult(
        name=gate_name,
        passed=False,
        detail=(
            "Training-only artifact detected; authoritative production evidence is still missing. "
            + remediation
        ),
        evidence={
            "training_artifact": data.get("training_artifact"),
            "authoritative_evidence": data.get("authoritative_evidence"),
            "execution_tier": data.get("execution_tier"),
            "note": data.get("note"),
        },
    )


# ---------------------------------------------------------------------------
# Gate 7 — Delegated Identity (composite)
# ---------------------------------------------------------------------------
def gate_delegated_identity() -> GateResult:
    """Composite gate: all three OBO sub-checks must pass."""
    sub_results = [
        gate_obo_app_identity(),
        gate_obo_exchange(),
        gate_actor_binding(),
    ]
    failed = [g.name for g in sub_results if not g.passed]
    passed = len(failed) == 0
    detail = (
        "All delegated-identity sub-checks passed."
        if passed
        else f"Failed sub-checks: {', '.join(failed)}"
    )
    return GateResult(
        name="delegated_identity",
        passed=passed,
        detail=detail,
        evidence={
            "sub_results": [
                {"name": g.name, "passed": g.passed, "detail": g.detail}
                for g in sub_results
            ]
        },
    )


def gate_obo_app_identity() -> GateResult:
    """Sub-check 1: orchestrator's Managed Identity token is acquirable."""
    try:
        artifact_path = _ROOT / "build" / "day11" / "obo_contract.json"
        if not artifact_path.exists():
            return GateResult(
                name="obo_app_identity",
                passed=False,
                detail="Day 11 artifact not found. Run Day 11 notebook first.",
            )
        data = json.loads(artifact_path.read_text())
        passed = bool(data.get("app_identity_check", {}).get("passed", False))
        detail = data.get("app_identity_check", {}).get(
            "detail", "No detail in artifact.")
        return GateResult(
            name="obo_app_identity",
            passed=passed,
            detail=detail,
            evidence=data.get("app_identity_check"),
        )
    except Exception as exc:
        return GateResult(name="obo_app_identity", passed=False, detail=str(exc))


def gate_obo_exchange() -> GateResult:
    """Sub-check 2: MSAL OBO exchange returns a downstream access token."""
    try:
        artifact_path = _ROOT / "build" / "day11" / "obo_contract.json"
        if not artifact_path.exists():
            return GateResult(
                name="obo_exchange",
                passed=False,
                detail="Day 11 artifact not found. Run Day 11 notebook first.",
            )
        data = json.loads(artifact_path.read_text())
        passed = bool(data.get("obo_exchange_check", {}).get("passed", False))
        detail = data.get("obo_exchange_check", {}).get(
            "detail", "No detail in artifact.")
        return GateResult(
            name="obo_exchange",
            passed=passed,
            detail=detail,
            evidence=data.get("obo_exchange_check"),
        )
    except Exception as exc:
        return GateResult(name="obo_exchange", passed=False, detail=str(exc))


def gate_actor_binding() -> GateResult:
    """Sub-check 3: approver's Entra OID is bound to the required Entra group."""
    try:
        artifact_path = _ROOT / "build" / "day11" / "obo_contract.json"
        if not artifact_path.exists():
            return GateResult(
                name="actor_binding",
                passed=False,
                detail="Day 11 artifact not found. Run Day 11 notebook first.",
            )
        data = json.loads(artifact_path.read_text())
        passed = bool(data.get("actor_binding_check", {}).get("passed", False))
        detail = data.get("actor_binding_check", {}).get(
            "detail", "No detail in artifact.")
        return GateResult(
            name="actor_binding",
            passed=passed,
            detail=detail,
            evidence=data.get("actor_binding_check"),
        )
    except Exception as exc:
        return GateResult(name="actor_binding", passed=False, detail=str(exc))


# ---------------------------------------------------------------------------
# Gate 11 — Private Network Static (CI PR gate)
# ---------------------------------------------------------------------------
def gate_private_network_static() -> GateResult:
    """CI gate: static_bicep_analysis.json written by check_private_network_static.

    The artifact is produced by ``scripts/check_private_network_static.py`` which
    compiles every Bicep template in ``infra/`` to ARM JSON via ``az bicep build``
    and verifies that every AI-tier resource has ``publicNetworkAccess == "Disabled"``.
    """
    try:
        artifact_path = _ROOT / "build" / "day12" / "static_bicep_analysis.json"
        if not artifact_path.exists():
            return GateResult(
                name="private_network_static",
                passed=False,
                detail=(
                    "static_bicep_analysis.json not found. "
                    "Run scripts/check_private_network_static.py first."
                ),
            )
        data = json.loads(artifact_path.read_text())
        # Trust verification: only accept artifacts written by the static checker
        written_by = data.get("written_by", "")
        if written_by != "check_private_network_static":
            return GateResult(
                name="private_network_static",
                passed=False,
                detail=(
                    f"Artifact trust check failed: written_by={written_by!r}; "
                    "expected 'check_private_network_static'."
                ),
            )
        if data.get("error"):
            return GateResult(
                name="private_network_static",
                passed=False,
                detail=f"Static analysis error: {data['error']}",
                evidence=data,
            )
        all_passed = bool(data.get("all_passed", False))
        violations = data.get("violations", [])
        detail = (
            f"All {data.get('resources_checked', 0)} AI resources have publicNetworkAccess=Disabled."
            if all_passed
            else f"{len(violations)} violation(s): " + "; ".join(
                f"{v.get('resource', '?')} ({v.get('violation', 'unknown')})" for v in violations[:3]
            )
        )
        return GateResult(
            name="private_network_static",
            passed=all_passed,
            detail=detail,
            evidence=data,
        )
    except Exception as exc:
        return GateResult(name="private_network_static", passed=False, detail=str(exc))


# ---------------------------------------------------------------------------
# Gate 12 — Private Network Posture (live staging gate)
# ---------------------------------------------------------------------------
def gate_private_network_posture() -> GateResult:
    """Staging gate: full posture report from probe script must show all_passed."""
    try:
        posture_path = _ROOT / "build" / "day12" / "private_network_posture.json"
        if not posture_path.exists():
            return GateResult(
                name="private_network_posture",
                passed=False,
                detail=(
                    "private_network_posture.json not found. "
                    "Run scripts/verify_private_network_posture.py against staging."
                ),
            )
        data = json.loads(posture_path.read_text())
        training_only = _require_authoritative_evidence(
            gate_name="private_network_posture",
            data=data,
            remediation=(
                "Run the live posture probe from the VNET-injected staging environment "
                "to verify DNS and public-endpoint inaccessibility."
            ),
        )
        if training_only is not None:
            return training_only
        passed = bool(data.get("all_passed", False))
        services = data.get("services", [])
        failed_services = [s["hostname"]
                           for s in services if not s.get("passed")]
        detail = (
            "All service private endpoints verified."
            if passed
            else f"Failed services: {', '.join(failed_services)}"
        )
        return GateResult(
            name="private_network_posture",
            passed=passed,
            detail=detail,
            evidence={"failed_services": failed_services,
                      "total_services": len(services)},
        )
    except Exception as exc:
        return GateResult(name="private_network_posture", passed=False, detail=str(exc))


# ---------------------------------------------------------------------------
# Gate 13 — Trace Correlation
# ---------------------------------------------------------------------------
def gate_trace_correlation() -> GateResult:
    """All workflow traces must carry a correlation ID.

    Dual-sink mode is *required* when Day 12 private-network posture confirms
    all services are on private endpoints (``build/day12/private_network_posture.json
    all_passed=True``).  This ensures the mode decision follows the network
    evidence chain rather than an unrelated Day 8 artifact.
    """
    try:
        report_path = _ROOT / "build" / "day14" / "trace_correlation_report.json"
        if not report_path.exists():
            return GateResult(
                name="trace_correlation",
                passed=False,
                detail=(
                    "trace_correlation_report.json not found. "
                    "Run scripts/generate_cto_trace_report.py first."
                ),
            )
        data = json.loads(report_path.read_text())
        training_only = _require_authoritative_evidence(
            gate_name="trace_correlation",
            data=data,
            remediation=(
                "Export live traces to the required sink(s) and regenerate the "
                "correlation report from real telemetry."
            ),
        )
        if training_only is not None:
            return training_only

        # Derive dual-sink requirement from Day 12 network posture evidence.
        dual_sink_required = False
        posture_path = _ROOT / "build" / "day12" / "private_network_posture.json"
        if posture_path.exists():
            try:
                posture = json.loads(posture_path.read_text())
                dual_sink_required = bool(posture.get("all_passed", False))
            except Exception:
                pass

        passed = bool(data.get("passed", False))
        uncorrelated = data.get("uncorrelated", 0)
        dual_ok = data.get("dual_sink_ok", True)

        if dual_sink_required and not dual_ok:
            passed = False
            detail = (
                "Trace correlation failed: private network posture confirmed "
                "but dual-sink (Azure Monitor + OTLP) is not configured."
            )
        elif not passed:
            detail = f"Trace correlation failed: {uncorrelated} trace(s) missing correlation_id."
        else:
            detail = (
                f"All {data.get('total_traces', 0)} traces correlated. "
                f"Dual-sink required: {dual_sink_required}; satisfied: {dual_ok}."
            )
        return GateResult(
            name="trace_correlation",
            passed=passed,
            detail=detail,
            evidence={
                "uncorrelated": uncorrelated,
                "dual_sink_required": dual_sink_required,
                "dual_sink_satisfied": dual_ok,
                "posture_source": str(posture_path),
            },
        )
    except Exception as exc:
        return GateResult(name="trace_correlation", passed=False, detail=str(exc))


# ---------------------------------------------------------------------------
# Gate 14 — Data Residency (ARM API check)
# ---------------------------------------------------------------------------
def gate_data_residency() -> GateResult:
    """All AI resource locations must match the approved region (ARM API)."""
    try:
        residency_path = _ROOT / "build" / "day14" / "data_residency_report.json"
        if not residency_path.exists():
            return GateResult(
                name="data_residency",
                passed=False,
                detail=(
                    "data_residency_report.json not found. "
                    "Run scripts/verify_private_network_static.py with --data-residency flag."
                ),
            )
        data = json.loads(residency_path.read_text())
        training_only = _require_authoritative_evidence(
            gate_name="data_residency",
            data=data,
            remediation=(
                "Query the ARM API against the target resource group to produce a "
                "real region-verification report."
            ),
        )
        if training_only is not None:
            return training_only
        passed = bool(data.get("all_passed", False))
        approved_region = data.get("approved_region", "unknown")
        violations = data.get("violations", [])
        detail = (
            f"All resources are in approved region '{approved_region}'."
            if passed
            else (
                f"Data residency violations: "
                f"{', '.join(v.get('resource_id', 'unknown') for v in violations)}"
            )
        )
        return GateResult(
            name="data_residency",
            passed=passed,
            detail=detail,
            evidence={"approved_region": approved_region,
                      "violation_count": len(violations)},
        )
    except Exception as exc:
        return GateResult(name="data_residency", passed=False, detail=str(exc))


# ---------------------------------------------------------------------------
# Gate 15 — DLQ Drain Health
# ---------------------------------------------------------------------------
def gate_dlq_drain_health() -> GateResult:
    """DLQ report must exist and show zero error rate."""
    try:
        dlq_path = _ROOT / "build" / "day13" / "dlq_drain_report.json"
        if not dlq_path.exists():
            return GateResult(
                name="dlq_drain_health",
                passed=False,
                detail=(
                    "dlq_drain_report.json not found. "
                    "Run Day 13 notebook DLQ drain cell first."
                ),
            )
        data = json.loads(dlq_path.read_text())
        training_only = _require_authoritative_evidence(
            gate_name="dlq_drain_health",
            data=data,
            remediation=(
                "Drain the real dead-letter queue and record the resulting DLQ report "
                "before claiming production reliability."
            ),
        )
        if training_only is not None:
            return training_only
        error_count = int(data.get("error_count", 0))
        total = int(data.get("total", 0))
        passed = error_count == 0
        detail = (
            f"DLQ drain: {total} messages processed, 0 errors."
            if passed
            else f"DLQ drain: {error_count} error(s) out of {total} messages."
        )
        return GateResult(
            name="dlq_drain_health",
            passed=passed,
            detail=detail,
            evidence={"total": total, "error_count": error_count},
        )
    except Exception as exc:
        return GateResult(name="dlq_drain_health", passed=False, detail=str(exc))


# ---------------------------------------------------------------------------
# Gate 16 — MCP Contract Integrity
# ---------------------------------------------------------------------------
def gate_mcp_contract_integrity() -> GateResult:
    """MCP /capabilities response must match the declared schema."""
    try:
        contract_path = _ROOT / "build" / "day13" / "mcp_contract_report.json"
        if not contract_path.exists():
            return GateResult(
                name="mcp_contract_integrity",
                passed=False,
                detail=(
                    "mcp_contract_report.json not found. "
                    "Run scripts/verify_mcp_contract_integrity.py first."
                ),
            )
        data = json.loads(contract_path.read_text())
        training_only = _require_authoritative_evidence(
            gate_name="mcp_contract_integrity",
            data=data,
            remediation=(
                "Fetch `/capabilities` from the live MCP server and validate the "
                "declared tool contract, including the write-path tool."
            ),
        )
        if training_only is not None:
            return training_only
        passed = bool(data.get("passed", False))
        errors = data.get("errors", [])
        detail = (
            "MCP contract integrity verified."
            if passed
            else f"Contract violations: {'; '.join(str(e) for e in errors[:3])}"
        )
        return GateResult(
            name="mcp_contract_integrity",
            passed=passed,
            detail=detail,
            evidence={"error_count": len(errors)},
        )
    except Exception as exc:
        return GateResult(name="mcp_contract_integrity", passed=False, detail=str(exc))


# ---------------------------------------------------------------------------
# Gate 17 — Canary Regression
# ---------------------------------------------------------------------------
def gate_canary_regression() -> GateResult:
    """Canary run eval results must not regress against the Day 8 baseline."""
    try:
        canary_path = _ROOT / "build" / "day14" / "canary_regression_report.json"
        if not canary_path.exists():
            return GateResult(
                name="canary_regression",
                passed=False,
                detail=(
                    "canary_regression_report.json not found. "
                    "Run Day 14 canary exercise first."
                ),
            )
        data = json.loads(canary_path.read_text())
        training_only = _require_authoritative_evidence(
            gate_name="canary_regression",
            data=data,
            remediation=(
                "Run a real canary against the candidate revision and compare it to "
                "the protected Day 8 baseline before promotion."
            ),
        )
        if training_only is not None:
            return training_only
        passed = bool(data.get("passed", False))
        regressions = data.get("regressions", [])
        detail = (
            "No canary regressions detected."
            if passed
            else f"Canary regressions: {', '.join(str(r) for r in regressions)}"
        )
        return GateResult(
            name="canary_regression",
            passed=passed,
            detail=detail,
            evidence={"regression_count": len(regressions)},
        )
    except Exception as exc:
        return GateResult(name="canary_regression", passed=False, detail=str(exc))


# ---------------------------------------------------------------------------
# Gate 19 — Stale Index Detection  (soft / warn)
# ---------------------------------------------------------------------------
def gate_stale_index_detection() -> GateResult:
    """Warn if the AI Search index freshness report shows stale documents.

    This is a *soft* gate: it records a warning rather than blocking deployment.
    Staleness means the vector index was last rebuilt more than the configured
    threshold (default 24 h) ago.
    """
    try:
        report_path = _ROOT / "build" / "day12" / "stale_index_report.json"
        if not report_path.exists():
            return GateResult(
                name="stale_index_detection",
                passed=False,
                detail=(
                    "stale_index_report.json not found. "
                    "Run Day 12 or Day 14 stale-index lab cell first."
                ),
            )
        data = json.loads(report_path.read_text())
        raw = data.get("stale_indexes", 0)
        stale_count = len(raw) if isinstance(raw, list) else int(raw)
        # Soft gate: always passes — warn only, never block deployment.
        passed = True
        threshold_hours = data.get("threshold_hours", 24)
        detail = (
            f"All indexes refreshed within {threshold_hours} h threshold."
            if stale_count == 0
            else (
                f"WARN: {stale_count} index(es) not rebuilt within "
                f"{threshold_hours} h — consider triggering re-index."
            )
        )
        return GateResult(
            name="stale_index_detection",
            passed=passed,
            detail=detail,
            evidence={"stale_indexes": stale_count,
                      "threshold_hours": threshold_hours},
        )
    except Exception as exc:
        return GateResult(name="stale_index_detection", passed=False, detail=str(exc))


# ---------------------------------------------------------------------------
# Gate 11 — Webhook Reliability
# ---------------------------------------------------------------------------
def gate_webhook_reliability() -> GateResult:
    """Webhook reliability report must exist and show all_handled=True."""
    try:
        report_path = _ROOT / "build" / "day13" / "webhook_reliability_report.json"
        if not report_path.exists():
            return GateResult(
                name="webhook_reliability",
                passed=False,
                detail=(
                    "webhook_reliability_report.json not found. "
                    "Run scripts/verify_webhook_reliability.py or Day 13 DLQ cell."
                ),
            )
        data = json.loads(report_path.read_text())
        training_only = _require_authoritative_evidence(
            gate_name="webhook_reliability",
            data=data,
            remediation=(
                "Exercise the live integration boundary and capture the real webhook "
                "reliability report before marking the boundary release-ready."
            ),
        )
        if training_only is not None:
            return training_only
        passed = bool(data.get("all_handled", False))
        unhandled = int(data.get("unhandled_count", 0))
        detail = (
            "All DLQ messages handled with compensating actions."
            if passed
            else f"{unhandled} DLQ message(s) not handled — compensating action required."
        )
        return GateResult(
            name="webhook_reliability",
            passed=passed,
            detail=detail,
            evidence={"unhandled_count": unhandled},
        )
    except Exception as exc:
        return GateResult(name="webhook_reliability", passed=False, detail=str(exc))


# ---------------------------------------------------------------------------
# Gate 20 — Rollback Readiness
# ---------------------------------------------------------------------------
def gate_rollback_readiness() -> GateResult:
    """Last known-good revision must be locatable and documented."""
    try:
        report_path = _ROOT / "build" / "day14" / "rollback_readiness_report.json"
        if not report_path.exists():
            return GateResult(
                name="rollback_readiness",
                passed=False,
                detail=(
                    "rollback_readiness_report.json not found. "
                    "Run Day 14 rollback-readiness lab cell first."
                ),
            )
        data = json.loads(report_path.read_text())
        passed = bool(data.get("stable_revision_known", False))
        revision = data.get("stable_revision", "unknown")
        runbook_present = bool(data.get("runbook_present", False))
        if passed and not runbook_present:
            passed = False
            detail = f"Stable revision '{revision}' known but rollback runbook not found."
        elif passed:
            detail = f"Rollback ready: stable revision '{revision}' documented with runbook."
        else:
            detail = "No stable revision documented — run Day 14 rollback-readiness cell."
        return GateResult(
            name="rollback_readiness",
            passed=passed,
            detail=detail,
            evidence={"stable_revision": revision,
                      "runbook_present": runbook_present},
        )
    except Exception as exc:
        return GateResult(name="rollback_readiness", passed=False, detail=str(exc))


# ---------------------------------------------------------------------------
# Aliases for taxonomy name consistency
# ---------------------------------------------------------------------------
def gate_delegated_identity_contract() -> GateResult:
    """Alias: same as gate_delegated_identity."""
    return gate_delegated_identity()


def gate_dead_letter_budget() -> GateResult:
    """Alias: same as gate_dlq_drain_health."""
    return gate_dlq_drain_health()
