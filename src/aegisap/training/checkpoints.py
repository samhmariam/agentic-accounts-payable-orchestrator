from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aegisap.common.paths import repo_root
from aegisap.deploy.gates import GateResult, build_release_envelope
from aegisap.lab.curriculum import get_day, load_manifest
from aegisap.lab.mastery import (
    PASS as MASTERY_PASS,
    validate_kql_evidence_artifact,
    validate_native_operator_evidence_artifact,
)
from aegisap.day4.planning.policy_overlay import derive_policy_overlay
from aegisap.observability.context import make_workflow_observability_context
from aegisap.observability.tracing import root_span_attributes
from aegisap.training.artifacts import build_root, write_json_artifact
from aegisap.training.labs import load_case_facts, run_day4_case_artifact


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_day4_policy_overlay_checkpoint(
    *,
    fixture_path: str | Path | None = None,
    artifact_name: str = "checkpoint_policy_overlay",
) -> tuple[Path, dict[str, Any]]:
    source_fixture = Path(fixture_path) if fixture_path is not None else (
        repo_root(__file__) / "fixtures" / "day4" / "high_value_missing_po_bank_change.json"
    )
    case_facts = load_case_facts(source_fixture)
    overlay = derive_policy_overlay(case_facts)
    source_artifact, day4_payload, state = asyncio.run(
        run_day4_case_artifact(
            case_facts=case_facts,
            planner_mode="fixture",
            artifact_name="golden_thread_day4",
        )
    )
    blocked = state.recommendation is None and state.escalation_package is not None
    payload = {
        "day": 4,
        "checkpoint": "policy_overlay_change",
        "created_at": _timestamp(),
        "policy_rule_id": "require_authoritative_evidence_before_recommendation",
        "source_fixture": str(source_fixture),
        "source_artifact": str(source_artifact),
        "blocked": blocked,
        "risk_flags": list(overlay.risk_flags),
        "global_preconditions": list(overlay.global_preconditions),
        "global_stop_conditions": list(overlay.global_stop_conditions),
        "required_approvals": list(overlay.required_approvals),
        "recommendation_present": state.recommendation is not None,
        "escalation_package": state.escalation_package,
        "validated_plan_id": (day4_payload.get("validated_plan") or {}).get("plan_id"),
    }
    artifact_path = build_root("day4") / f"{artifact_name}.json"
    return write_json_artifact(artifact_path, payload), payload


def run_day8_trace_extension_checkpoint(
    *,
    artifact_name: str = "checkpoint_trace_extension",
) -> tuple[Path, dict[str, Any]]:
    context = make_workflow_observability_context(
        request_id="checkpoint-day8",
        workflow_run_id="wf-checkpoint-day8",
        case_id="case-checkpoint-day8",
        thread_id="thread-checkpoint-day8",
    )
    context.plan_version = "day4"
    context.policy_version = "day6"
    context.outcome_type = "checkpoint_ready"
    context.metadata["checkpoint_phase"] = "day8_trace_extension"
    context.metadata["checkpoint_span"] = "day8.eval_guardrail"
    attributes = root_span_attributes(context)

    payload = {
        "day": 8,
        "checkpoint": "trace_extension",
        "created_at": _timestamp(),
        "span_name": "day8.eval_guardrail",
        "required_attribute": "aegis.checkpoint_phase",
        "trace_attributes": {
            key: value
            for key, value in attributes.items()
            if key in {
                "aegis.workflow_run_id",
                "aegis.plan_version",
                "aegis.policy_version",
                "aegis.outcome_type",
                "aegis.checkpoint_phase",
                "aegis.checkpoint_span",
            }
        },
        "regression_assertion": {
            "metric": "test_pass_rate",
            "rule": "Release is blocked if the checkpoint span cannot be correlated to a passing baseline.",
        },
        "kql_query": (
            "traces\n"
            "| where customDimensions['aegis.checkpoint_phase'] == 'day8_trace_extension'\n"
            "| project timestamp, operation_Id, name, customDimensions['aegis.checkpoint_span']\n"
            "| order by timestamp desc"
        ),
    }
    artifact_path = build_root("day8") / f"{artifact_name}.json"
    return write_json_artifact(artifact_path, payload), payload


def gate_checkpoint_extension_contract() -> GateResult:
    root = repo_root(__file__)
    required = [
        root / "build" / "day4" / "checkpoint_policy_overlay.json",
        root / "build" / "day8" / "checkpoint_trace_extension.json",
    ]
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    if missing:
        return GateResult(
            name="checkpoint_extension_contract",
            passed=False,
            detail=f"Missing checkpoint artifact(s): {', '.join(missing)}",
            evidence={"required_artifacts": [str(path.relative_to(root)) for path in required]},
        )
    return GateResult(
        name="checkpoint_extension_contract",
        passed=True,
        detail="Checkpoint artifacts are present and wired to the release rehearsal.",
        evidence={"required_artifacts": [str(path.relative_to(root)) for path in required]},
    )


def gate_day10_operator_evidence_chain(
    *,
    required_days: list[str] | None = None,
) -> GateResult:
    root = repo_root(__file__)
    manifest = load_manifest(root)
    days = required_days or [f"{day:02d}" for day in range(5, 10)]
    problems: list[str] = []
    validation_results: list[dict[str, Any]] = []

    for day_id in days:
        day_entry = get_day(manifest, day_id)
        native_contract = day_entry.get("native_operator_evidence")
        kql_contract = day_entry.get("kql_evidence")
        if native_contract is None or kql_contract is None:
            missing_parts = []
            if native_contract is None:
                missing_parts.append("native_operator_evidence")
            if kql_contract is None:
                missing_parts.append("kql_evidence")
            problems.append(f"day {day_id} missing manifest contract(s): {', '.join(missing_parts)}")
            continue

        native_result = validate_native_operator_evidence_artifact(
            day_id=day_id,
            contract=native_contract,
            repo_root=root,
        )
        kql_result = validate_kql_evidence_artifact(
            day_id=day_id,
            contract=kql_contract,
            repo_root=root,
        )
        validation_results.extend(
            [
                {
                    "day": day_id,
                    "gate_id": native_result.gate_id,
                    "status": native_result.status,
                    "detail": native_result.detail,
                },
                {
                    "day": day_id,
                    "gate_id": kql_result.gate_id,
                    "status": kql_result.status,
                    "detail": kql_result.detail,
                },
            ]
        )
        if native_result.status != MASTERY_PASS:
            problems.append(f"day {day_id} native proof: {native_result.detail}")
        if kql_result.status != MASTERY_PASS:
            problems.append(f"day {day_id} KQL proof: {kql_result.detail}")

    passed = not problems
    detail = (
        "Days 05-09 native and KQL evidence chains are structurally valid for CAB review."
        if passed
        else " ; ".join(problems)
    )
    return GateResult(
        name="operator_evidence_chain",
        passed=passed,
        detail=detail,
        evidence={
            "required_days": days,
            "validation_results": validation_results,
        },
    )


def run_day10_gate_extension_checkpoint(
    *,
    base_results: list[GateResult],
    artifact_name: str = "checkpoint_gate_extension",
) -> tuple[Path, dict[str, Any], Path, dict[str, Any]]:
    extra_gate = gate_checkpoint_extension_contract()
    operator_evidence_gate = gate_day10_operator_evidence_chain()
    release_results = [*base_results, operator_evidence_gate]
    release_envelope = build_release_envelope(release_results)
    release_path = build_root("day10") / "release_envelope.json"
    write_json_artifact(release_path, release_envelope)

    payload = {
        "day": 10,
        "checkpoint": "gate_extension_and_recovery",
        "created_at": _timestamp(),
        "training_gate": {
            "name": extra_gate.name,
            "passed": extra_gate.passed,
            "detail": extra_gate.detail,
            "evidence": extra_gate.evidence,
        },
        "upstream_evidence_gate": {
            "name": operator_evidence_gate.name,
            "passed": operator_evidence_gate.passed,
            "detail": operator_evidence_gate.detail,
            "evidence": operator_evidence_gate.evidence,
        },
        "base_release_all_passed": release_envelope["all_passed"],
        "base_gates": [result.name for result in release_results],
        "release_envelope_path": str(release_path),
        "ready_for_capstone_review": release_envelope["all_passed"] and extra_gate.passed,
    }
    artifact_path = build_root("day10") / f"{artifact_name}.json"
    return (
        write_json_artifact(artifact_path, payload),
        payload,
        release_path,
        release_envelope,
    )


def build_day10_rollback_rehearsal(
    *,
    artifact_name: str = "rollback_rehearsal",
) -> tuple[Path, dict[str, Any]]:
    payload = {
        "day": "10",
        "rollback_unit": "aca_revision",
        "traffic_restored_before_git": True,
        "stable_revision": "aegisap-worker--stable",
        "failing_revision": "aegisap-worker--canary",
        "traffic_shift": {
            "command": (
                "az containerapp ingress traffic set --name aegisap-worker "
                "--resource-group $AZURE_RESOURCE_GROUP "
                "--revision-weight aegisap-worker--stable=100 -o json"
            ),
            "observed_excerpt": '{"revisionName":"aegisap-worker--stable","weight":100}',
            "verification_command": (
                "az containerapp ingress traffic show --name aegisap-worker "
                "--resource-group $AZURE_RESOURCE_GROUP -o json"
            ),
            "verification_excerpt": '{"traffic":[{"revisionName":"aegisap-worker--stable","weight":100}]}',
        },
        "readiness_retry_policy": {
            "initial_delay_seconds": 5,
            "max_attempts": 5,
            "backoff_multiplier": 2,
        },
        "health_checks": [
            {
                "name": "health_ready",
                "command": "curl -sf https://aegisap.example/health/ready",
                "attempts": 2,
                "passed": True,
                "observed_excerpt": "HTTP 200 /health/ready on attempt 2 after replica warm-up.",
            },
            {
                "name": "version_probe",
                "command": "curl -sf https://aegisap.example/version",
                "attempts": 1,
                "passed": True,
                "observed_excerpt": '{"revision":"aegisap-worker--stable","sha":"abc1234"}',
            },
        ],
        "notes": [
            "Traffic was restored to the immutable stable ACA revision before any Git history discussion.",
            "Readiness checks used retry/backoff to distinguish routing changes from replica warm-up.",
        ],
        "created_at": _timestamp(),
    }
    artifact_path = build_root("day10") / f"{artifact_name}.json"
    return write_json_artifact(artifact_path, payload), payload
