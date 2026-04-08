from __future__ import annotations

import json
from pathlib import Path
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


def _write_native_operator_evidence(
    path: Path,
    *,
    day: str,
    passed: bool,
    review_stage: str,
    minimum_commands: int = 1,
    minimum_queries: int = 0,
    required: bool = False,
) -> None:
    payload = {
        "day": day,
        "commands": [
            {
                "command": f"az command {index}",
                "purpose": "prove state",
                "expected_signal": "expected",
                "observed_excerpt": "observed",
            }
            for index in range(minimum_commands)
        ],
        "queries": [
            {
                "query": f"traces | take {index + 1}",
                "purpose": "prove telemetry",
                "expected_signal": "expected",
                "observed_excerpt": "observed",
            }
            for index in range(minimum_queries)
        ],
        "operator_interpretation": "The operator can explain what the native proof means.",
        "limitations": ["One environment only."],
        "live_demo": {
            "required": required,
            "review_stage": review_stage,
            "passed": passed,
            "witnessed_by": "facilitator" if passed else "",
            "recorded_at": "2026-04-08T00:00:00Z" if passed else "",
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_run_mastery_day9_native_evidence_is_advisory(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        mastery,
        "load_manifest",
        lambda _repo_root=None: {
            "days": [
                {
                    "id": "09",
                    "title": "Native advisory day",
                    "mastery_gates": [
                        {
                            "id": "day09_repo_evidence",
                            "mode": "blocking",
                            "command": "echo ok",
                            "success_marker": "ok",
                            "covers_constraints": ["cost_ceiling_enforced"],
                            "evidence_source": "artifact",
                        }
                    ],
                    "native_operator_evidence": {
                        "artifact_path": "build/day9/native_operator_evidence.json",
                        "mode": "advisory",
                        "review_stage": "day10_cab_board",
                        "live_demo_required": False,
                        "minimum_commands": 1,
                        "minimum_queries": 1,
                    },
                }
            ]
        },
    )
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, "ok", ""),
    )

    payload = mastery.run_mastery(day="09", repo_root=tmp_path)

    assert payload["overall_ok"] is True
    assert payload["results"][-1]["status"] == mastery.FAIL


def test_run_mastery_day9_native_evidence_passes_when_structurally_valid(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        mastery,
        "load_manifest",
        lambda _repo_root=None: {
            "days": [
                {
                    "id": "09",
                    "title": "Native advisory day",
                    "mastery_gates": [
                        {
                            "id": "day09_repo_evidence",
                            "mode": "blocking",
                            "command": "echo ok",
                            "success_marker": "ok",
                            "covers_constraints": ["cost_ceiling_enforced"],
                            "evidence_source": "artifact",
                        }
                    ],
                    "native_operator_evidence": {
                        "artifact_path": "build/day9/native_operator_evidence.json",
                        "mode": "advisory",
                        "review_stage": "day10_cab_board",
                        "live_demo_required": False,
                        "minimum_commands": 1,
                        "minimum_queries": 1,
                    },
                }
            ]
        },
    )
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, "ok", ""),
    )
    _write_native_operator_evidence(
        tmp_path / "build" / "day9" / "native_operator_evidence.json",
        day="09",
        passed=False,
        review_stage="day10_cab_board",
        minimum_commands=1,
        minimum_queries=1,
        required=False,
    )

    payload = mastery.run_mastery(day="09", repo_root=tmp_path)

    assert payload["overall_ok"] is True
    assert payload["results"][-1]["status"] == mastery.PASS


def test_run_mastery_blocking_native_evidence_requires_live_demo_pass(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        mastery,
        "load_manifest",
        lambda _repo_root=None: {
            "days": [
                {
                    "id": "12",
                    "title": "Native blocking day",
                    "mastery_gates": [
                        {
                            "id": "day12_repo_evidence",
                            "mode": "blocking",
                            "command": "echo ok",
                            "success_marker": "ok",
                            "covers_constraints": ["private_dns_resolution"],
                            "evidence_source": "artifact",
                        }
                    ],
                    "native_operator_evidence": {
                        "artifact_path": "build/day12/native_operator_evidence.json",
                        "mode": "blocking",
                        "review_stage": "day12_closeout",
                        "live_demo_required": True,
                        "minimum_commands": 2,
                        "minimum_queries": 0,
                    },
                }
            ]
        },
    )
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, "ok", ""),
    )
    _write_native_operator_evidence(
        tmp_path / "build" / "day12" / "native_operator_evidence.json",
        day="12",
        passed=False,
        review_stage="day12_closeout",
        minimum_commands=2,
        minimum_queries=0,
        required=True,
    )

    payload = mastery.run_mastery(day="12", repo_root=tmp_path)

    assert payload["overall_ok"] is False
    assert payload["results"][-1]["status"] == mastery.FAIL
