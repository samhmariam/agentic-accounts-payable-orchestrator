from __future__ import annotations

import subprocess

from aegisap.lab import mastery


def test_run_mastery_day2_advisory_failure_does_not_block(monkeypatch) -> None:
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

    payload = mastery.run_mastery(day="02")

    assert payload["overall_ok"] is True
    assert payload["results"][0]["status"] == mastery.FAIL


def test_run_mastery_blocking_failure_blocks(monkeypatch) -> None:
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

    payload = mastery.run_mastery(day="03")

    assert payload["overall_ok"] is False
    assert payload["results"][0]["status"] == mastery.FAIL


def test_run_mastery_strict_mode_fails_on_preview_skip(monkeypatch) -> None:
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

    payload = mastery.run_mastery(day="08", strict=True)

    assert payload["overall_ok"] is False
    assert payload["results"][0]["status"] == mastery.SKIP
