from __future__ import annotations

import json
from pathlib import Path

from aegisap.deploy.gates import GateResult
from aegisap.common.paths import repo_root
from aegisap.training.capstone import build_capstone_release_packet
from aegisap.training.checkpoints import (
    gate_day10_operator_evidence_chain,
    run_day4_policy_overlay_checkpoint,
    run_day8_trace_extension_checkpoint,
    run_day10_gate_extension_checkpoint,
)


def _passing_gate(name: str) -> GateResult:
    return GateResult(name=name, passed=True, detail="ok", evidence={"source": "test"})


def _write_native_and_kql_evidence(day_id: str) -> None:
    review_stage_by_day = {
        "05": "day05_closeout",
        "06": "day06_closeout",
        "07": "day07_closeout",
        "08": "day08_closeout",
        "09": "day10_cab_board",
    }
    native_path = f"build/day{int(day_id)}/native_operator_evidence.json"
    kql_path = f"build/day{int(day_id)}/kql_evidence.json"
    native_payload = {
        "day": day_id,
        "commands": [
            {
                "command": f"az rest --day {day_id}",
                "purpose": "prove operator state",
                "expected_signal": "expected",
                "observed_excerpt": "observed",
            },
            {
                "command": f"curl https://example.invalid/day{day_id}",
                "purpose": "prove dependent state",
                "expected_signal": "expected",
                "observed_excerpt": "observed",
            },
        ],
        "queries": [
            {
                "query": "traces | take 1",
                "purpose": "prove telemetry",
                "expected_signal": "expected",
                "observed_excerpt": "observed",
            }
        ],
        "operator_interpretation": "The operator can explain what the native proof means.",
        "limitations": ["One environment only."],
        "live_demo": {
            "required": False,
            "review_stage": review_stage_by_day[day_id],
            "passed": False,
            "witnessed_by": "",
            "recorded_at": "",
        },
    }
    kql_payload = {
        "day": day_id,
        "queries": [
            {
                "query": "traces | take 1",
                "workspace": "training-workspace",
                "signal_found": True,
                "purpose": "prove the production footprint",
                "observed_excerpt": "gate_name, passed=false",
                "operator_interpretation": "This proves the failure signal showed up in Log Analytics.",
            }
        ],
    }
    from pathlib import Path

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
