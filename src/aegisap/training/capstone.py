from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aegisap.common.paths import repo_root
from aegisap.training.artifacts import load_json, write_json_artifact
from aegisap.training.checkpoints import gate_day10_operator_evidence_chain


CAPSTONE_PASS_BAR = 13
CAPSTONE_MAX_SCORE = 16
CAPSTONE_MINIMUM_DIMENSION_SCORES = {
    "Technical Correctness": 3,
    "Security Reasoning": 3,
}


def build_capstone_release_packet(
    *,
    trainee_id: str,
    enhancement_category: str,
    release_envelope_path: str | Path,
    checkpoint_artifacts: list[str | Path],
    rollback_command: str,
    summary: str,
    out_path: str | Path | None = None,
) -> tuple[Path, dict[str, Any]]:
    root = repo_root(__file__)
    evidence_gate = gate_day10_operator_evidence_chain()
    if not evidence_gate.passed:
        raise ValueError(
            "Day 10 release packet cannot be built until Days 05-09 native and KQL evidence are valid: "
            f"{evidence_gate.detail}"
        )
    release_path = Path(release_envelope_path)
    if not release_path.is_absolute():
        release_path = root / release_path
    payload = {
        "trainee_id": trainee_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "enhancement_category": enhancement_category,
        "release_envelope_path": str(release_path),
        "release_envelope": load_json(release_path),
        "checkpoint_artifacts": [str(Path(path)) for path in checkpoint_artifacts],
        "rollback_command": rollback_command,
        "summary": summary,
        "upstream_evidence_gate": {
            "name": evidence_gate.name,
            "passed": evidence_gate.passed,
            "detail": evidence_gate.detail,
            "evidence": evidence_gate.evidence,
        },
        "rubric": {
            "pass_bar": f"{CAPSTONE_PASS_BAR}/{CAPSTONE_MAX_SCORE}",
            "minimum_dimension_scores": dict(CAPSTONE_MINIMUM_DIMENSION_SCORES),
            "required_green_checks": [
                "tests",
                "release_gates",
            ],
        },
    }
    target = Path(out_path) if out_path is not None else (
        root / "build" / "capstone" / trainee_id / "release_packet.json"
    )
    if not target.is_absolute():
        target = root / target
    return write_json_artifact(target, payload), payload
