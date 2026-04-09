from __future__ import annotations

import json
from pathlib import Path

from aegisap.deploy.gates import GateResult
from aegisap.common.paths import repo_root
from aegisap.lab.curriculum import get_day, load_manifest
from aegisap.training.capstone import build_capstone_final_packet, build_capstone_release_packet
from aegisap.training.checkpoints import (
    gate_day10_operator_evidence_chain,
    run_day4_policy_overlay_checkpoint,
    run_day8_trace_extension_checkpoint,
    run_day10_gate_extension_checkpoint,
)


def _passing_gate(name: str) -> GateResult:
    return GateResult(name=name, passed=True, detail="ok", evidence={"source": "test"})


_SIGNAL_FAMILY_COMMAND_FIXTURES = {
    "durable_state_or_queue_truth": [
        (
            "az postgres flexible-server show -g training-rg -n aegisap-db -o json",
            '{"name":"aegisap-db","properties":{"state":"Ready"},"countDetails":{"activeMessageCount":0}}',
        ),
        (
            "az servicebus queue show --resource-group training-rg --namespace-name aegisap-bus --name invoices -o json",
            '{"name":"invoices","properties":{"status":"Active"},"countDetails":{"activeMessageCount":0}}',
        ),
    ],
    "authority_surface_truth": [
        (
            "az cosmosdb show -g training-rg -n aegisap-cosmos -o json",
            '{"name":"aegisap-cosmos","properties":{"provisioningState":"Succeeded"},"identity":{"type":"SystemAssigned"}}',
        ),
        (
            "az ml workspace show -g training-rg -w aegisap-ml -o json",
            '{"name":"aegisap-ml","properties":{"provisioningState":"Succeeded"},"identity":{"type":"SystemAssigned"}}',
        ),
    ],
    "telemetry_guardrail_surface": [
        (
            "az monitor app-insights component show -a aegisap-ai -g training-rg -o json",
            '{"name":"aegisap-ai","kind":"web","properties":{"ApplicationType":"web","WorkspaceResourceId":"/subscriptions/test/resourceGroups/training-rg/providers/Microsoft.OperationalInsights/workspaces/training"},"label":"Application Insights"}',
        ),
        (
            "az resource show --ids /subscriptions/test/resourceGroups/training-rg/providers/microsoft.insights/components/aegisap-ai -o json",
            '{"properties":{"WorkspaceResourceId":"/subscriptions/test/resourceGroups/training-rg/providers/Microsoft.OperationalInsights/workspaces/training"},"displayName":"Application Insights"}',
        ),
    ],
    "identity_and_role_truth": [
        (
            "az role assignment list --assignee 00000000-0000-0000-0000-000000000001 --scope /subscriptions/test/resourceGroups/training-rg -o json",
            '[{"principalId":"00000000-0000-0000-0000-000000000001","roleDefinitionName":"Search Index Data Contributor"}]',
        ),
        (
            "az containerapp identity show -g training-rg -n aegisap-api -o json",
            '{"principalId":"00000000-0000-0000-0000-000000000001","tenantId":"00000000-0000-0000-0000-000000000002"}',
        ),
    ],
    "monitoring_or_cost_truth": [
        (
            "az monitor metrics list --resource /subscriptions/test/resourceGroups/training-rg/providers/Microsoft.App/containerApps/aegisap-api --metric Requests -o json",
            '{"cost":0,"timeseries":[{"data":[{"total":42}]}]}',
        ),
        (
            "az consumption usage list --top 1 -o json",
            '{"value":[{"cost":12.34,"currency":"USD"}],"total":12.34}',
        ),
    ],
}


def _write_native_and_kql_evidence(day_id: str) -> None:
    root = repo_root(__file__)
    manifest = load_manifest(root)
    day_entry = get_day(manifest, day_id)
    native_contract = day_entry["native_operator_evidence"]
    kql_contract = day_entry["kql_evidence"]
    family_name = native_contract["required_signal_families"][0]["name"]
    fixtures = _SIGNAL_FAMILY_COMMAND_FIXTURES[family_name]
    minimum_commands = int(native_contract.get("minimum_commands", 1))
    minimum_queries = int(native_contract.get("minimum_queries", 0))
    native_path = f"build/day{int(day_id)}/native_operator_evidence.json"
    kql_path = f"build/day{int(day_id)}/kql_evidence.json"
    native_payload = {
        "day": day_id,
        "commands": [
            {
                "capture_order": index + 1,
                "captured_before_patch": True,
                "machine_readable_output": True,
                "command": fixtures[index % len(fixtures)][0],
                "purpose": "prove operator state",
                "expected_signal": "expected",
                "observed_excerpt": fixtures[index % len(fixtures)][1],
            }
            for index in range(minimum_commands)
        ],
        "queries": [
            {
                "capture_order": minimum_commands + index + 1,
                "captured_before_patch": True,
                "machine_readable_output": True,
                "query": f"traces | where customDimensions['training.day'] == '{day_id}' | take {index + 1}",
                "purpose": "prove telemetry",
                "expected_signal": "expected",
                "observed_excerpt": "observed",
            }
            for index in range(minimum_queries)
        ],
        "operator_interpretation": "The operator can explain what the native proof means.",
        "limitations": ["One environment only."],
        "live_demo": {
            "required": bool(native_contract.get("live_demo_required")),
            "review_stage": native_contract["review_stage"],
            "passed": not bool(native_contract.get("live_demo_required")),
            "witnessed_by": "facilitator" if native_contract.get("live_demo_required") else "",
            "recorded_at": "2026-04-09T00:00:00Z" if native_contract.get("live_demo_required") else "",
        },
    }
    kql_payload = {
        "day": day_id,
        "queries": [
            {
                "capture_order": index + 1,
                "captured_before_patch": True,
                "query": f"traces | where customDimensions['training.day'] == '{day_id}' | take {index + 1}",
                "workspace": "training-workspace",
                "signal_found": True,
                "first_signal_or_followup": "first_signal" if index == 0 else "followup",
                "trace_reference": "trace-001" if index == 0 else "",
                "purpose": "prove the production footprint",
                "observed_excerpt": "gate_name, passed=false",
                "operator_interpretation": "This proves the failure signal showed up in Log Analytics.",
            }
            for index in range(int(kql_contract.get("minimum_queries", 1)))
        ],
    }

    Path(native_path).parent.mkdir(parents=True, exist_ok=True)
    Path(native_path).write_text(json.dumps(native_payload), encoding="utf-8")
    Path(kql_path).write_text(json.dumps(kql_payload), encoding="utf-8")


def _snapshot_paths(*paths: Path) -> dict[Path, str | None]:
    return {
        path: path.read_text(encoding="utf-8") if path.exists() else None
        for path in paths
    }


def _restore_paths(snapshot: dict[Path, str | None]) -> None:
    for path, original in snapshot.items():
        if original is None:
            if path.exists():
                path.unlink()
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(original, encoding="utf-8")


def test_day4_checkpoint_emits_blocked_artifact() -> None:
    artifact_path, payload = run_day4_policy_overlay_checkpoint()

    assert artifact_path.exists()
    assert payload["checkpoint"] == "policy_overlay_change"
    assert payload["blocked"] is True
    assert payload["recommendation_present"] is False
    assert "bank_change_authoritatively_verified" in payload["global_preconditions"]


def test_day8_checkpoint_records_trace_extension_contract() -> None:
    artifact_path, payload = run_day8_trace_extension_checkpoint()

    assert artifact_path.exists()
    assert payload["checkpoint"] == "trace_extension"
    assert payload["trace_attributes"]["aegis.checkpoint_phase"] == "day8_trace_extension"
    assert "customDimensions['aegis.checkpoint_phase']" in payload["kql_query"]


def test_day10_checkpoint_wires_training_gate_to_upstream_artifacts() -> None:
    run_day4_policy_overlay_checkpoint()
    run_day8_trace_extension_checkpoint()
    for day_id in [f"{day:02d}" for day in range(5, 10)]:
        _write_native_and_kql_evidence(day_id)

    artifact_path, payload, release_path, release_envelope = run_day10_gate_extension_checkpoint(
        base_results=[
            _passing_gate("security_posture"),
            _passing_gate("eval_regression"),
            _passing_gate("budget"),
            _passing_gate("refusal_safety"),
            _passing_gate("resume_safety"),
            _passing_gate("aca_health"),
        ]
    )

    assert artifact_path.exists()
    assert release_path.exists()
    assert release_envelope["all_passed"] is True
    assert payload["training_gate"]["passed"] is True
    assert payload["upstream_evidence_gate"]["passed"] is True
    assert payload["ready_for_capstone_review"] is True


def test_day10_operator_evidence_chain_fails_when_upstream_day_is_missing() -> None:
    root = repo_root(__file__)
    native_path = root / "build" / "day5" / "native_operator_evidence.json"
    kql_path = root / "build" / "day5" / "kql_evidence.json"
    snapshot = _snapshot_paths(native_path, kql_path)
    try:
        if native_path.exists():
            native_path.unlink()
        if kql_path.exists():
            kql_path.unlink()
        gate = gate_day10_operator_evidence_chain(required_days=["05"])

        assert gate.passed is False
        assert "day 05" in gate.detail
    finally:
        _restore_paths(snapshot)


def test_capstone_release_packet_includes_release_and_checkpoint_evidence() -> None:
    run_day4_policy_overlay_checkpoint()
    run_day8_trace_extension_checkpoint()
    for day_id in [f"{day:02d}" for day in range(5, 10)]:
        _write_native_and_kql_evidence(day_id)
    _artifact_path, _payload, release_path, _release_envelope = run_day10_gate_extension_checkpoint(
        base_results=[
            _passing_gate("security_posture"),
            _passing_gate("eval_regression"),
            _passing_gate("budget"),
            _passing_gate("refusal_safety"),
            _passing_gate("resume_safety"),
            _passing_gate("aca_health"),
        ]
    )

    packet_path, packet = build_capstone_release_packet(
        trainee_id="trainer-alice",
        enhancement_category="observability_or_policy",
        release_envelope_path=release_path,
        checkpoint_artifacts=[
            "build/day4/checkpoint_policy_overlay.json",
            "build/day8/checkpoint_trace_extension.json",
            "build/day10/checkpoint_gate_extension.json",
        ],
        rollback_command="uv run python scripts/check_all_gates.py --skip-deploy --out build/day10/release_envelope.json",
        summary="Adds a bounded training gate and release evidence.",
    )

    assert packet_path.exists()
    assert packet["trainee_id"] == "trainer-alice"
    assert packet["rubric"]["pass_bar"] == "13/16"
    assert packet["release_envelope"]["all_passed"] is True
    assert packet["upstream_evidence_gate"]["passed"] is True
    assert packet["checkpoint_artifacts"][-1] == "build/day10/checkpoint_gate_extension.json"


def test_capstone_release_packet_rejects_missing_upstream_operator_evidence() -> None:
    root = repo_root(__file__)
    native_path = root / "build" / "day5" / "native_operator_evidence.json"
    kql_path = root / "build" / "day5" / "kql_evidence.json"
    snapshot = _snapshot_paths(native_path, kql_path)
    try:
        if native_path.exists():
            native_path.unlink()
        if kql_path.exists():
            kql_path.unlink()

        run_day4_policy_overlay_checkpoint()
        run_day8_trace_extension_checkpoint()
        _artifact_path, _payload, release_path, _release_envelope = run_day10_gate_extension_checkpoint(
            base_results=[
                _passing_gate("security_posture"),
                _passing_gate("eval_regression"),
                _passing_gate("budget"),
                _passing_gate("refusal_safety"),
                _passing_gate("resume_safety"),
                _passing_gate("aca_health"),
            ]
        )

        try:
            build_capstone_release_packet(
                trainee_id="trainer-alice",
                enhancement_category="observability_or_policy",
                release_envelope_path=release_path,
                checkpoint_artifacts=[
                    "build/day4/checkpoint_policy_overlay.json",
                    "build/day8/checkpoint_trace_extension.json",
                    "build/day10/checkpoint_gate_extension.json",
                ],
                rollback_command="uv run python scripts/check_all_gates.py --skip-deploy --out build/day10/release_envelope.json",
                summary="Adds a bounded training gate and release evidence.",
            )
        except ValueError as exc:
            assert "Days 05-09 native and KQL evidence" in str(exc)
        else:  # pragma: no cover - defensive assertion
            raise AssertionError("missing upstream evidence should block the capstone release packet")
    finally:
        _restore_paths(snapshot)


def test_capstone_final_packet_includes_day11_to_day14_evidence() -> None:
    run_day4_policy_overlay_checkpoint()
    run_day8_trace_extension_checkpoint()
    for day_id in [f"{day:02d}" for day in range(5, 10)]:
        _write_native_and_kql_evidence(day_id)
    _artifact_path, _payload, release_path, _release_envelope = run_day10_gate_extension_checkpoint(
        base_results=[
            _passing_gate("security_posture"),
            _passing_gate("eval_regression"),
            _passing_gate("budget"),
            _passing_gate("refusal_safety"),
            _passing_gate("resume_safety"),
            _passing_gate("aca_health"),
        ]
    )
    build_capstone_release_packet(
        trainee_id="trainer-alice",
        enhancement_category="observability_or_policy",
        release_envelope_path=release_path,
        checkpoint_artifacts=[
            "build/day4/checkpoint_policy_overlay.json",
            "build/day8/checkpoint_trace_extension.json",
            "build/day10/checkpoint_gate_extension.json",
        ],
        rollback_command="uv run python scripts/check_all_gates.py --skip-deploy --out build/day10/release_envelope.json",
        summary="Adds a bounded training gate and release evidence.",
    )

    packet_path, packet = build_capstone_final_packet(
        trainee_id="trainer-alice",
        summary="Aggregates Day 10-14 evidence into the final CAB packet.",
    )

    assert packet_path.exists()
    assert packet["capstone_a_stage"] == "day14_final_cab_defense"
    assert packet["review_contract"]["required_evidence_days"] == ["10", "11", "12", "13", "14"]
    assert packet["supporting_artifacts"]["day11_obo_contract"]["path"].endswith("build/day11/obo_contract.json")
    assert packet["supporting_artifacts"]["day14_chaos_capstone_report"]["path"].endswith(
        "build/day14/chaos_capstone_report.json"
    )


def test_capstone_final_packet_rejects_missing_late_stage_evidence() -> None:
    root = repo_root(__file__)
    missing_path = root / "build" / "day12" / "private_network_posture.json"
    snapshot = _snapshot_paths(missing_path)
    try:
        run_day4_policy_overlay_checkpoint()
        run_day8_trace_extension_checkpoint()
        for day_id in [f"{day:02d}" for day in range(5, 10)]:
            _write_native_and_kql_evidence(day_id)
        _artifact_path, _payload, release_path, _release_envelope = run_day10_gate_extension_checkpoint(
            base_results=[
                _passing_gate("security_posture"),
                _passing_gate("eval_regression"),
                _passing_gate("budget"),
                _passing_gate("refusal_safety"),
                _passing_gate("resume_safety"),
                _passing_gate("aca_health"),
            ]
        )
        build_capstone_release_packet(
            trainee_id="trainer-alice",
            enhancement_category="observability_or_policy",
            release_envelope_path=release_path,
            checkpoint_artifacts=[
                "build/day4/checkpoint_policy_overlay.json",
                "build/day8/checkpoint_trace_extension.json",
                "build/day10/checkpoint_gate_extension.json",
            ],
            rollback_command="uv run python scripts/check_all_gates.py --skip-deploy --out build/day10/release_envelope.json",
            summary="Adds a bounded training gate and release evidence.",
        )
        if missing_path.exists():
            missing_path.unlink()
        try:
            build_capstone_final_packet(
                trainee_id="trainer-alice",
                summary="Should fail without Day 12 posture evidence.",
            )
        except ValueError as exc:
            assert "full Day 11-14 enterprise evidence set" in str(exc)
            assert "private_network_posture.json" in str(exc)
        else:  # pragma: no cover - defensive assertion
            raise AssertionError("missing late-stage evidence should block the final capstone packet")
    finally:
        _restore_paths(snapshot)
