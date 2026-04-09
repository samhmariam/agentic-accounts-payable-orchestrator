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
CAPSTONE_FINAL_REQUIRED_ARTIFACTS = {
    "foundation_packet": "build/capstone/{trainee_id}/release_packet.json",
    "day11_obo_contract": "build/day11/obo_contract.json",
    "day12_private_network_posture": "build/day12/private_network_posture.json",
    "day13_mcp_contract_report": "build/day13/mcp_contract_report.json",
    "day14_cto_trace_report": "build/day14/cto_trace_report.json",
    "day14_chaos_capstone_report": "build/day14/chaos_capstone_report.json",
}
CAPSTONE_FINAL_REVERT_PROOF = "docs/curriculum/artifacts/day14/REVERT_PROOF.md"


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


def _resolve_required_path(
    *,
    root: Path,
    path_like: str | Path,
) -> Path:
    path = Path(path_like)
    if not path.is_absolute():
        path = root / path
    return path


def build_capstone_final_packet(
    *,
    trainee_id: str,
    summary: str,
    foundation_packet_path: str | Path | None = None,
    out_path: str | Path | None = None,
    revert_proof_path: str | Path = CAPSTONE_FINAL_REVERT_PROOF,
) -> tuple[Path, dict[str, Any]]:
    root = repo_root(__file__)
    foundation_rel = foundation_packet_path or CAPSTONE_FINAL_REQUIRED_ARTIFACTS["foundation_packet"].format(
        trainee_id=trainee_id
    )
    foundation_path = _resolve_required_path(root=root, path_like=foundation_rel)
    if not foundation_path.exists():
        raise ValueError(
            "Capstone A final packet requires the Day 10 foundation release packet first: "
            f"{foundation_path}"
        )

    foundation_payload = load_json(foundation_path)
    if not foundation_payload.get("release_envelope", {}).get("all_passed", False):
        raise ValueError(
            "Capstone A final packet requires a passing Day 10 foundation packet with green release evidence."
        )

    supporting_artifacts: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for key, template in CAPSTONE_FINAL_REQUIRED_ARTIFACTS.items():
        if key == "foundation_packet":
            continue
        artifact_rel = template.format(trainee_id=trainee_id)
        artifact_path = _resolve_required_path(root=root, path_like=artifact_rel)
        if not artifact_path.exists():
            missing.append(str(artifact_path))
            continue
        supporting_artifacts[key] = {
            "path": str(artifact_path),
            "payload": load_json(artifact_path),
        }

    revert_path = _resolve_required_path(root=root, path_like=revert_proof_path)
    if not revert_path.exists():
        missing.append(str(revert_path))

    if missing:
        raise ValueError(
            "Capstone A final packet requires the full Day 11-14 enterprise evidence set: "
            + ", ".join(missing)
        )

    payload = {
        "trainee_id": trainee_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "capstone_a_stage": "day14_final_cab_defense",
        "final_review_packet": True,
        "foundation_packet_path": str(foundation_path),
        "foundation_packet": foundation_payload,
        "required_artifacts": {
            key: template.format(trainee_id=trainee_id)
            for key, template in CAPSTONE_FINAL_REQUIRED_ARTIFACTS.items()
        },
        "supporting_artifacts": supporting_artifacts,
        "revert_proof_path": str(revert_path),
        "review_contract": {
            "kickoff_checkpoint_day": "10",
            "final_defense_day": "14",
            "required_evidence_days": ["10", "11", "12", "13", "14"],
            "capstone_b_days": ["12", "13", "14"],
        },
    }
    target = Path(out_path) if out_path is not None else (
        root / "build" / "capstone" / trainee_id / "final_packet.json"
    )
    if not target.is_absolute():
        target = root / target
    return write_json_artifact(target, payload), payload
