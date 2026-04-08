from __future__ import annotations

import json
import subprocess

from aegisap.lab import mastery


def test_run_mastery_day2_advisory_failure_does_not_block(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        mastery,
        "load_manifest",
        lambda _repo_root=None: {
            "days": [
                {
                    "id": "02",
                    "title": "Advisory day",
                    "mastery_gates": [
                        {
                            "id": "day02_repo_evidence",
                            "mode": "advisory",
                            "command": "false",
                            "success_marker": "ignored",
                            "covers_constraints": ["latency_budget_guardrails"],
                            "evidence_source": "artifact",
                        }
                    ],
                }
            ]
        },
    )
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 1, "", "boom"),
    )

    payload = mastery.run_mastery(day="02", repo_root=tmp_path)

    assert payload["overall_ok"] is True
    assert payload["results"][0]["status"] == mastery.FAIL


def test_run_mastery_blocking_failure_blocks(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        mastery,
        "load_manifest",
        lambda _repo_root=None: {
            "days": [
                {
                    "id": "03",
                    "title": "Blocking day",
                    "mastery_gates": [
                        {
                            "id": "day03_repo_evidence",
                            "mode": "blocking",
                            "command": "false",
                            "success_marker": "ignored",
                            "covers_constraints": ["authoritative_retrieval_sources"],
                            "evidence_source": "artifact",
                        }
                    ],
                }
            ]
        },
    )
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 1, "", "boom"),
    )

    payload = mastery.run_mastery(day="03", repo_root=tmp_path)

    assert payload["overall_ok"] is False
    assert payload["results"][0]["status"] == mastery.FAIL


def test_run_mastery_strict_mode_fails_on_preview_skip(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        mastery,
        "load_manifest",
        lambda _repo_root=None: {
            "days": [
                {
                    "id": "08",
                    "title": "Cloud truth day",
                    "mastery_gates": [
                        {
                            "id": "day08_cloud_truth",
                            "mode": "blocking",
                            "command": "echo preview",
                            "success_marker": '"all_passed": true',
                            "covers_constraints": ["no_public_endpoints"],
                            "evidence_source": "cloud_probe",
                        }
                    ],
                }
            ]
        },
    )
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args,
            0,
            '{"training_artifact": true, "authoritative_evidence": false, "note": "Preview mode"}',
            "",
        ),
    )

    payload = mastery.run_mastery(day="08", strict=True, repo_root=tmp_path)

    assert payload["overall_ok"] is False
    assert payload["results"][0]["status"] == mastery.SKIP


def test_run_mastery_writes_constraint_lineage_artifact(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        mastery,
        "load_manifest",
        lambda _repo_root=None: {
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
                            "command": "echo ok",
                            "success_marker": "ok",
                            "covers_constraints": ["no_public_endpoints"],
                            "evidence_source": "cloud_probe",
                        }
                    ],
                }
            ]
        },
    )
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, "ok", ""),
    )

    payload = mastery.run_mastery(day="12", repo_root=tmp_path)
    lineage_path = tmp_path / "build" / "day12" / "constraint_lineage.json"

    assert payload["overall_ok"] is True
    assert lineage_path.exists()
    saved = json.loads(lineage_path.read_text(encoding="utf-8"))
    assert saved["active_constraints"][0]["id"] == "no_public_endpoints"
