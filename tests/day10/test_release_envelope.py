from __future__ import annotations

from aegisap.deploy.gates import GateResult, build_release_envelope


def test_release_envelope_requires_every_gate_to_pass() -> None:
    envelope = build_release_envelope(
        [
            GateResult(name="security_posture", passed=False, detail="forbidden runtime secret detected"),
            GateResult(name="resume_safety", passed=True, detail="No duplicate side effects."),
        ]
    )

    assert envelope["all_passed"] is False
    assert [gate["passed"] for gate in envelope["gates"]] == [False, True]


def test_release_envelope_is_green_only_when_all_gates_pass() -> None:
    envelope = build_release_envelope(
        [
            GateResult(name="security_posture", passed=True, detail="All checks passed."),
            GateResult(name="resume_safety", passed=True, detail="No duplicate side effects."),
        ]
    )

    assert envelope["all_passed"] is True
