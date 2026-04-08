from __future__ import annotations

import json
from pathlib import Path

import pytest

from aegisap.lab import drills


@pytest.fixture()
def artifact_manifest() -> dict:
    return {
        "days": [
            {
                "id": "12",
                "title": "Private Networking",
                "persistent_constraints": [
                    {
                        "id": "no_public_endpoints",
                        "type": "infrastructure",
                        "description": "No public endpoints.",
                        "introduced_on": "04",
                        "persists": True,
                    }
                ],
                "mastery_gates": [
                    {
                        "id": "day12_cloud_truth",
                        "mode": "blocking",
                        "command": "uv run aegisap-lab audit-production --day 12 --strict",
                        "success_marker": '"all_passed": true',
                        "covers_constraints": ["no_public_endpoints"],
                        "evidence_source": "cloud_probe",
                    }
                ],
                "automation_drills": [
                    {
                        "id": "drill_03_dns_misconfiguration",
                        "default": True,
                        "mode": "artifact",
                        "name": "Private Endpoint DNS Misconfiguration",
                        "description": "Break DNS posture.",
                        "expected_signal": "DNS broke.",
                        "source_file": "evals/failure_drills/drill_03_dns_misconfiguration.json",
                        "mutation": "fake_mutation",
                    }
                ],
            }
        ]
    }


def test_list_drills_reports_default_and_active(monkeypatch, tmp_path: Path, artifact_manifest: dict) -> None:
    monkeypatch.setattr(drills, "load_manifest", lambda _root=None: artifact_manifest)
    state_path = tmp_path / ".aegisap-lab" / "drills" / "day12.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps({"drill_id": "drill_03_dns_misconfiguration"}), encoding="utf-8")

    payload = drills.list_drills(repo_root=tmp_path, day="12")

    assert len(payload["drills"]) == 1
    assert payload["drills"][0]["default"] is True
    assert payload["drills"][0]["active"] is True


def test_inject_artifact_drill_writes_state_and_reset_restores(monkeypatch, tmp_path: Path, artifact_manifest: dict) -> None:
    monkeypatch.setattr(drills, "load_manifest", lambda _root=None: artifact_manifest)
    monkeypatch.setattr(drills, "_load_drill_metadata", lambda repo_root, drill: {})

    target = tmp_path / "build" / "day12" / "private_network_posture.json"

    def fake_rebuild_day_artifact(day: str) -> dict:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({"all_passed": True}), encoding="utf-8")
        return {"day": day, "artifact_path": str(target), "supporting_artifacts": {}}

    def fake_mutation(repo_root: Path) -> list[str]:
        target.write_text(json.dumps({"all_passed": False}), encoding="utf-8")
        return [str(target)]

    monkeypatch.setattr(drills, "rebuild_day_artifact", fake_rebuild_day_artifact)
    monkeypatch.setitem(drills._ARTIFACT_MUTATORS, "fake_mutation", fake_mutation)

    injected = drills.inject_drill(day="12", repo_root=tmp_path)
    state_path = tmp_path / ".aegisap-lab" / "drills" / "day12.json"

    assert injected["drill_id"] == "drill_03_dns_misconfiguration"
    assert state_path.exists()
    assert json.loads(target.read_text(encoding="utf-8"))["all_passed"] is False

    reset = drills.reset_drill(day="12", repo_root=tmp_path)

    assert reset["drill_id"] == "drill_03_dns_misconfiguration"
    assert not state_path.exists()
    assert json.loads(target.read_text(encoding="utf-8"))["all_passed"] is True


def test_inject_incident_drill_delegates_to_incident_engine(monkeypatch, tmp_path: Path) -> None:
    manifest = {
        "days": [
            {
                "id": "01",
                "title": "Trust Boundary",
                "persistent_constraints": [
                    {
                        "id": "regulated_invoice_auditability",
                        "type": "process",
                        "description": "Audit everything.",
                        "introduced_on": "01",
                        "persists": True,
                    }
                ],
                "mastery_gates": [
                    {
                        "id": "day01_repo_evidence",
                        "mode": "blocking",
                        "command": "uv run python -m pytest",
                        "success_marker": '"day": "01"',
                        "covers_constraints": ["regulated_invoice_auditability"],
                        "evidence_source": "artifact",
                    }
                ],
                "automation_drills": [
                    {
                        "id": "day01_incident_replay",
                        "default": True,
                        "mode": "incident",
                        "name": "Day 1 incident replay",
                        "description": "Replay the scenario.",
                        "expected_signal": "Trust boundary failed.",
                    }
                ],
            }
        ]
    }
    calls: list[tuple[str, str]] = []

    monkeypatch.setattr(drills, "load_manifest", lambda _root=None: manifest)
    monkeypatch.setattr(
        drills,
        "start_incident",
        lambda *, day, repo_path: calls.append(("start", day)),
    )
    monkeypatch.setattr(
        drills,
        "reset_incident",
        lambda *, day, repo_path: calls.append(("reset", day)),
    )

    injected = drills.inject_drill(day="01", repo_root=tmp_path)
    reset = drills.reset_drill(day="01", repo_root=tmp_path)

    assert injected["mode"] == "incident"
    assert reset["mode"] == "incident"
    assert calls == [("start", "01"), ("reset", "01")]
