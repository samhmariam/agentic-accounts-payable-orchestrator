from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from aegisap.training.artifacts import build_root, write_json_artifact


DEFAULT_DRILLS: tuple[dict[str, Any], ...] = (
    {
        "id": "drill_01_obo_group_mismatch",
        "title": "OBO actor-binding mismatch",
        "category": "identity",
        "status": "passed",
        "mttr_minutes": 8,
        "first_signal": "Approver group check failed during delegated approval.",
    },
    {
        "id": "drill_02_token_claim_drift",
        "title": "Delegated token claim drift",
        "category": "identity",
        "status": "passed",
        "mttr_minutes": 9,
        "first_signal": "OBO exchange succeeded but actor claims no longer matched the authority model.",
    },
    {
        "id": "drill_03_public_endpoint_reenabled",
        "title": "Public AI endpoint re-enabled",
        "category": "network",
        "status": "passed",
        "mttr_minutes": 11,
        "first_signal": "Static Bicep analysis and portal posture disagreed on public access.",
    },
    {
        "id": "drill_04_private_dns_drift",
        "title": "Private DNS drift",
        "category": "network",
        "status": "passed",
        "mttr_minutes": 10,
        "first_signal": "Private endpoint existed but hostname resolution left RFC-1918 space.",
    },
    {
        "id": "drill_05_mcp_capability_loss",
        "title": "MCP capability contract drift",
        "category": "boundary",
        "status": "passed",
        "mttr_minutes": 7,
        "first_signal": "Partner could not discover the governed write-path tool.",
    },
    {
        "id": "drill_06_dlq_overflow",
        "title": "DLQ backlog growth",
        "category": "boundary",
        "status": "passed",
        "mttr_minutes": 12,
        "first_signal": "Dead-letter queue count exceeded the safe threshold during retries.",
    },
    {
        "id": "drill_07_trace_dual_sink_gap",
        "title": "Missing dual-sink trace evidence",
        "category": "operations",
        "status": "passed",
        "mttr_minutes": 9,
        "first_signal": "Trace gate appeared green without the second sink required by private networking.",
    },
    {
        "id": "drill_08_canary_regression",
        "title": "Canary quality regression",
        "category": "operations",
        "status": "passed",
        "mttr_minutes": 13,
        "first_signal": "Candidate revision F1 regressed against the protected baseline.",
    },
    {
        "id": "drill_09_rollback_pointer_loss",
        "title": "Rollback pointer missing",
        "category": "operations",
        "status": "passed",
        "mttr_minutes": 6,
        "first_signal": "Stable revision metadata was missing from the release package.",
    },
    {
        "id": "drill_10_exec_packet_refresh",
        "title": "Executive incident packet refresh",
        "category": "executive",
        "status": "passed",
        "mttr_minutes": 8,
        "first_signal": "CTO brief omitted the current blast radius and recovery status.",
    },
)


def build_chaos_capstone_artifacts(
    *,
    out_dir: str | Path | None = None,
) -> dict[str, Any]:
    target_dir = Path(out_dir) if out_dir is not None else build_root("day14")
    target_dir.mkdir(parents=True, exist_ok=True)

    drills = [dict(drill) for drill in DEFAULT_DRILLS]
    passed = sum(1 for drill in drills if drill["status"] == "passed")
    mttr_values = [int(drill["mttr_minutes"]) for drill in drills]
    aggregate = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "total": len(drills),
        "status": "passed" if passed == len(drills) else "partial",
        "mean_time_to_recovery_minutes": round(mean(mttr_values), 2),
        "max_time_to_recovery_minutes": max(mttr_values),
        "drills": drills,
    }
    summary = {
        "generated_at": aggregate["generated_at"],
        "status": aggregate["status"],
        "scorecard": {
            "passed": aggregate["passed"],
            "total": aggregate["total"],
            "mean_time_to_recovery_minutes": aggregate["mean_time_to_recovery_minutes"],
            "max_time_to_recovery_minutes": aggregate["max_time_to_recovery_minutes"],
        },
        "command_expectation": "debug from the first signal, prove the repair, then update the executive packet",
    }

    drills_path = write_json_artifact(target_dir / "breaking_changes_drills.json", aggregate)
    summary_path = write_json_artifact(target_dir / "chaos_capstone_report.json", summary)
    return {
        "artifact_path": str(drills_path),
        "payload": aggregate,
        "supporting_artifacts": {
            "chaos_capstone_report_path": str(summary_path),
            "chaos_capstone_report": summary,
        },
    }
