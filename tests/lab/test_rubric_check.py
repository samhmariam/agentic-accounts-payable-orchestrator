from __future__ import annotations

import json
from pathlib import Path

from aegisap.lab.rubric_check import (
    build_rubric_check_path,
    copy_tracked_rubric_check_to_build,
    render_rubric_check_markdown,
    run_rubric_check,
    tracked_rubric_check_path,
)


def test_run_rubric_check_writes_build_and_tracked_artifacts(tmp_path: Path) -> None:
    payload = run_rubric_check(
        day="10",
        repo_root=tmp_path,
        learner_name="Taylor",
        confidence="medium",
        weakness="Needs tighter rollback proof.",
        remediation="Rehearse the rollback path before CAB.",
        scores={
            "technical_correctness": 28,
            "trade_off_reasoning": 16,
            "process_fluency": 12,
            "artifact_quality": 11,
            "oral_defense": 10,
        },
        rationales={
            "technical_correctness": "All tests green after the fix.",
            "trade_off_reasoning": "Named the rejected alternative.",
            "process_fluency": "Approval chain is explicit.",
            "artifact_quality": "All headings filled.",
            "oral_defense": "Needs cleaner board-level phrasing.",
        },
        prompt_for_missing=False,
    )

    build_path = build_rubric_check_path(repo_root=tmp_path, day="10")
    tracked_path = tracked_rubric_check_path(repo_root=tmp_path, day="10")

    assert build_path.exists()
    assert tracked_path.exists()
    assert payload["payload"]["self_score_total"] == 77


def test_copy_tracked_rubric_check_to_build_round_trips(tmp_path: Path) -> None:
    tracked_path = tracked_rubric_check_path(repo_root=tmp_path, day="09")
    tracked_path.parent.mkdir(parents=True, exist_ok=True)
    tracked_path.write_text(
        json.dumps(
            {
                "day": "09",
                "learner_name": "Sam",
                "generated_at": "2026-04-08T00:00:00Z",
                "confidence": "high",
                "declared_weakness": "None yet.",
                "remediation_action": "Keep validating live telemetry.",
                "self_score_total": 88,
                "dimensions": [],
            }
        ),
        encoding="utf-8",
    )

    result = copy_tracked_rubric_check_to_build(repo_root=tmp_path, day="09")
    build_path = Path(result["build_path"])

    assert build_path.exists()
    assert json.loads(build_path.read_text(encoding="utf-8"))["day"] == "09"


def test_render_rubric_check_markdown_contains_declared_weakness() -> None:
    markdown = render_rubric_check_markdown(
        {
            "day": "14",
            "learner_name": "Jordan",
            "confidence": "low",
            "declared_weakness": "Rollback proof is still thin.",
            "remediation_action": "Exercise the rollback path before review.",
            "self_score_total": 70,
            "dimensions": [
                {
                    "label": "Technical Correctness",
                    "score": 25,
                    "max_points": 35,
                    "rationale": "Repair is correct but evidence is incomplete.",
                }
            ],
        }
    )

    assert "## Rubric Check" in markdown
    assert "Rollback proof is still thin." in markdown


def test_run_rubric_check_uses_manifest_defined_dimensions_when_available(tmp_path: Path) -> None:
    manifest_path = tmp_path / "docs" / "curriculum" / "CURRICULUM_MANIFEST.yaml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        """
days:
  - id: "10"
    rubric_weights:
      technical_release_readiness: 20
      evidence_pack_quality: 20
      gate_exception_handling: 15
      executive_communication: 15
      oral_defense: 15
      diagnostic_independence: 15
""".strip(),
        encoding="utf-8",
    )

    payload = run_rubric_check(
        day="10",
        repo_root=tmp_path,
        learner_name="Taylor",
        confidence="medium",
        weakness="Needs tighter rollback proof.",
        remediation="Rehearse the rollback path before CAB.",
        scores={
            "technical_release_readiness": 18,
            "evidence_pack_quality": 17,
            "gate_exception_handling": 12,
            "executive_communication": 11,
            "oral_defense": 10,
            "diagnostic_independence": 0,
        },
        rationales={
            "technical_release_readiness": "Release gate is accurate after the fix.",
            "evidence_pack_quality": "CAB packet is complete.",
            "gate_exception_handling": "Exception path is explicit.",
            "executive_communication": "Brief is clear enough.",
            "oral_defense": "Needs cleaner board-level phrasing.",
            "diagnostic_independence": "Hint ladder was required.",
        },
        prompt_for_missing=False,
    )

    keys = [item["key"] for item in payload["payload"]["dimensions"]]
    assert "diagnostic_independence" in keys
