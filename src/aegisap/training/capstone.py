from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aegisap.common.paths import repo_root
from aegisap.training.artifacts import load_json, write_json_artifact


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
