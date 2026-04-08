from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .artifacts import rebuild_day_artifact
from .curriculum import (
    constraint_lineage_for_day,
    get_day,
    get_drill,
    load_manifest,
    normalize_day,
    resolve_repo_root,
)
from .engine import reset_incident, start_incident


_STATE_ROOT = Path(".aegisap-lab") / "drills"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _state_path(repo_root: Path, day: str) -> Path:
    return repo_root / _STATE_ROOT / f"day{day}.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _load_drill_metadata(repo_root: Path, drill: dict[str, Any]) -> dict[str, Any]:
    source_file = drill.get("source_file")
    if not source_file:
        return {}
    path = repo_root / source_file
    return _read_json(path)


def _prepare_artifact_day(repo_root: Path, day: str) -> None:
    rebuild_day_artifact(day)
    status = _state_path(repo_root, day)
    if status.exists():
        status.unlink()


def _mutate_json(path: Path, updater: Callable[[dict[str, Any]], dict[str, Any]]) -> str:
    payload = _read_json(path)
    updated = updater(payload)
    _write_json(path, updated)
    return str(path)


def _apply_day11_iam_drift(repo_root: Path) -> list[str]:
    path = repo_root / "build" / "day11" / "obo_contract.json"

    def updater(payload: dict[str, Any]) -> dict[str, Any]:
        payload["actor_binding_ok"] = False
        payload["gate_passed"] = False
        payload["actor_binding_check"] = {
            "passed": False,
            "detail": "Injected drill: actor binding no longer matches the required approver group.",
        }
        payload["note"] = "phase2_drill_injected"
        return payload

    return [_mutate_json(path, updater)]


def _apply_day11_obo_scope_mismatch(repo_root: Path) -> list[str]:
    path = repo_root / "build" / "day11" / "obo_contract.json"

    def updater(payload: dict[str, Any]) -> dict[str, Any]:
        payload["obo_exchange_ok"] = False
        payload["gate_passed"] = False
        payload["obo_exchange_check"] = {
            "passed": False,
            "detail": "Injected drill: OBO scope mismatch caused the delegated token exchange to fail.",
        }
        payload["note"] = "phase2_drill_injected"
        return payload

    return [_mutate_json(path, updater)]


def _apply_day12_dns_misconfiguration(repo_root: Path) -> list[str]:
    posture_path = repo_root / "build" / "day12" / "private_network_posture.json"
    sink_path = repo_root / "build" / "day12" / "external_sink_disabled.json"

    def updater(payload: dict[str, Any]) -> dict[str, Any]:
        payload["all_passed"] = False
        if payload.get("services"):
            payload["services"][0]["dns_private"] = False
            payload["services"][0]["dns_ip"] = "52.160.1.10"
            payload["services"][0]["passed"] = False
            payload["services"][0]["detail"] = (
                "Injected drill: private DNS zone link is missing and the hostname resolves publicly."
            )
        payload["note"] = "phase2_drill_injected"
        return payload

    mutated = [_mutate_json(posture_path, updater)]
    if sink_path.exists():
        sink_path.unlink()
    mutated.append(str(sink_path))
    return mutated


def _apply_day12_public_endpoint_reenabled(repo_root: Path) -> list[str]:
    static_path = repo_root / "build" / "day12" / "static_bicep_analysis.json"

    def updater(payload: dict[str, Any]) -> dict[str, Any]:
        payload["all_passed"] = False
        payload["violations"] = [
            {
                "resource": "aegisap-openai",
                "violation": "publicNetworkAccess re-enabled",
            }
        ]
        payload["compiled_at"] = _utc_now_iso()
        return payload

    return [_mutate_json(static_path, updater)]


def _apply_day13_dlq_overflow(repo_root: Path) -> list[str]:
    dlq_path = repo_root / "build" / "day13" / "dlq_drain_report.json"
    webhook_path = repo_root / "build" / "day13" / "webhook_reliability_report.json"

    def update_dlq(payload: dict[str, Any]) -> dict[str, Any]:
        payload["error_count"] = 3
        payload["errors"] = [
            "Injected drill: compensating action registration missing.",
            "Injected drill: DLQ backlog exceeded safe threshold.",
        ]
        payload["all_handled"] = False
        payload["note"] = "phase2_drill_injected"
        return payload

    def update_webhook(payload: dict[str, Any]) -> dict[str, Any]:
        payload["all_handled"] = False
        payload["unhandled_count"] = 3
        payload["note"] = "phase2_drill_injected"
        return payload

    return [
        _mutate_json(dlq_path, update_dlq),
        _mutate_json(webhook_path, update_webhook),
    ]


def _apply_day13_mcp_contract_break(repo_root: Path) -> list[str]:
    contract_path = repo_root / "build" / "day13" / "mcp_contract_report.json"

    def updater(payload: dict[str, Any]) -> dict[str, Any]:
        payload["passed"] = False
        payload["contract_valid"] = False
        payload["tools_missing"] = ["query_invoice_status"]
        payload["tools_present"] = [
            tool
            for tool in payload.get("tools_present", [])
            if tool != "query_invoice_status"
        ]
        payload["errors"] = ["Injected drill: required MCP tool query_invoice_status missing."]
        payload["note"] = "phase2_drill_injected"
        return payload

    return [_mutate_json(contract_path, updater)]


def _apply_day14_canary_regression(repo_root: Path) -> list[str]:
    path = repo_root / "build" / "day14" / "canary_regression_report.json"

    def updater(payload: dict[str, Any]) -> dict[str, Any]:
        payload["canary_f1"] = 0.84
        payload["f1_delta"] = -0.08
        payload["regressions"] = ["f1_delta", "mandatory_escalation_recall"]
        payload["passed"] = False
        payload["promotion_gate_passed"] = False
        payload["promoted"] = False
        payload["rolled_back"] = True
        payload["note"] = "phase2_drill_injected"
        return payload

    return [_mutate_json(path, updater)]


def _apply_day14_data_residency(repo_root: Path) -> list[str]:
    path = repo_root / "build" / "day14" / "data_residency_report.json"

    def updater(payload: dict[str, Any]) -> dict[str, Any]:
        payload["all_passed"] = False
        payload["violations"] = [
            {
                "resource_id": "/subscriptions/demo/resourceGroups/aegisap/providers/Microsoft.CognitiveServices/accounts/aegisap-openai",
                "location": "eastus",
            }
        ]
        return payload

    return [_mutate_json(path, updater)]


def _apply_day14_correlation_gap(repo_root: Path) -> list[str]:
    path = repo_root / "build" / "day14" / "trace_correlation_report.json"

    def updater(payload: dict[str, Any]) -> dict[str, Any]:
        payload["correlated"] = 3
        payload["uncorrelated"] = 1
        payload["passed"] = False
        payload["dual_sink_ok"] = False
        payload["dual_sink_satisfied"] = False
        payload["details"] = [
            "Injected drill: new downstream service dropped the correlation_id header."
        ]
        payload["note"] = "phase2_drill_injected"
        return payload

    return [_mutate_json(path, updater)]


def _apply_day14_rollback_failure(repo_root: Path) -> list[str]:
    rollback_path = repo_root / "build" / "day14" / "rollback_readiness_report.json"
    drill_path = repo_root / "build" / "day14" / "breaking_changes_drills.json"

    def update_rollback(payload: dict[str, Any]) -> dict[str, Any]:
        payload["stable_revision_known"] = False
        payload["stable_revision"] = "unknown"
        payload["runbook_present"] = False
        payload["recorded_at"] = _utc_now_iso()
        return payload

    def update_drills(payload: dict[str, Any]) -> dict[str, Any]:
        payload["passed"] = max(int(payload.get("passed", 0)) - 1, 0)
        payload["status"] = "partial"
        for drill in payload.get("drills", []):
            if drill.get("id") == "drill_09_rollback_pointer_loss":
                drill["status"] = "failed"
                drill["first_signal"] = "Injected drill: rollback pointer and stable revision metadata were lost."
        return payload

    return [
        _mutate_json(rollback_path, update_rollback),
        _mutate_json(drill_path, update_drills),
    ]


_ARTIFACT_MUTATORS: dict[str, Callable[[Path], list[str]]] = {
    "day11_iam_drift": _apply_day11_iam_drift,
    "day11_obo_scope_mismatch": _apply_day11_obo_scope_mismatch,
    "day12_dns_misconfiguration": _apply_day12_dns_misconfiguration,
    "day12_public_endpoint_reenabled": _apply_day12_public_endpoint_reenabled,
    "day13_dlq_overflow": _apply_day13_dlq_overflow,
    "day13_mcp_contract_break": _apply_day13_mcp_contract_break,
    "day14_canary_regression": _apply_day14_canary_regression,
    "day14_data_residency_violation": _apply_day14_data_residency,
    "day14_correlation_gap": _apply_day14_correlation_gap,
    "day14_rollback_failure": _apply_day14_rollback_failure,
}


def list_drills(
    *, repo_root: str | Path | None = None, day: str | None = None
) -> dict[str, Any]:
    root = resolve_repo_root(repo_root)
    manifest = load_manifest(root)
    days = manifest.get("days", [])
    if day is not None:
        normalized = normalize_day(day)
        days = [get_day(manifest, normalized)]

    drills = []
    for day_entry in days:
        day_id = day_entry["id"]
        active_path = _state_path(root, day_id)
        active = _read_json(active_path) if active_path.exists() else None
        for drill in day_entry.get("automation_drills", []):
            drills.append(
                {
                    "day": day_id,
                    "title": day_entry["title"],
                    "drill_id": drill["id"],
                    "default": drill.get("default", False),
                    "mode": drill["mode"],
                    "name": drill["name"],
                    "description": drill["description"],
                    "source_file": drill.get("source_file"),
                    "expected_signal": drill["expected_signal"],
                    "active": bool(active and active.get("drill_id") == drill["id"]),
                }
            )

    return {"drills": drills}


def inject_drill(
    *,
    day: str,
    repo_root: str | Path | None = None,
    drill_id: str | None = None,
) -> dict[str, Any]:
    root = resolve_repo_root(repo_root)
    manifest = load_manifest(root)
    normalized_day = normalize_day(day)
    day_entry = get_day(manifest, normalized_day)
    drill = get_drill(manifest, normalized_day, drill_id)
    state_path = _state_path(root, normalized_day)
    if state_path.exists():
        raise ValueError(
            f"Day {normalized_day} already has an active drill. Reset it before injecting another."
        )

    metadata = _load_drill_metadata(root, drill)
    mutated_files: list[str]
    if drill["mode"] == "incident":
        start_incident(day=normalized_day, repo_path=root)
        mutated_files = [str(root / ".aegisap-lab" / "state" / f"day{normalized_day}.json")]
    else:
        _prepare_artifact_day(root, normalized_day)
        mutated_files = _ARTIFACT_MUTATORS[drill["mutation"]](root)

    lineage = constraint_lineage_for_day(manifest, normalized_day)
    payload = {
        "day": normalized_day,
        "title": day_entry["title"],
        "drill_id": drill["id"],
        "name": drill["name"],
        "mode": drill["mode"],
        "expected_signal": drill["expected_signal"],
        "source_metadata": metadata,
        "mutated_files": mutated_files,
        "constraint_lineage": lineage,
        "injected_at": _utc_now_iso(),
    }
    _write_json(state_path, payload)
    return payload


def reset_drill(
    *,
    day: str,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    root = resolve_repo_root(repo_root)
    manifest = load_manifest(root)
    normalized_day = normalize_day(day)
    state_path = _state_path(root, normalized_day)
    if not state_path.exists():
        raise ValueError(f"Day {normalized_day} has no active drill to reset.")

    state = _read_json(state_path)
    if state["mode"] == "incident":
        reset_incident(day=normalized_day, repo_path=root)
        restored = [str(root / ".aegisap-lab" / "state" / f"day{normalized_day}.json")]
    else:
        rebuild = rebuild_day_artifact(normalized_day)
        restored = [rebuild["artifact_path"]]
        restored.extend(rebuild.get("supporting_artifacts", {}).values())

    state_path.unlink()
    return {
        "day": normalized_day,
        "drill_id": state["drill_id"],
        "mode": state["mode"],
        "restored": restored,
        "reset_at": _utc_now_iso(),
    }
