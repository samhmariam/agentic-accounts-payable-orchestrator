from __future__ import annotations

from aegisap.deploy.gates import GateResult
from aegisap.training.capstone import build_capstone_release_packet
from aegisap.training.checkpoints import (
    run_day4_policy_overlay_checkpoint,
    run_day8_trace_extension_checkpoint,
    run_day10_gate_extension_checkpoint,
)


def _passing_gate(name: str) -> GateResult:
    return GateResult(name=name, passed=True, detail="ok", evidence={"source": "test"})


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
    assert payload["ready_for_capstone_review"] is True


def test_capstone_release_packet_includes_release_and_checkpoint_evidence() -> None:
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
    assert packet["checkpoint_artifacts"][-1] == "build/day10/checkpoint_gate_extension.json"
