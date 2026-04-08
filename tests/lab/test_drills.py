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


def test_day7_prompt_authority_drift_writes_drift_cases_and_resets(monkeypatch, tmp_path: Path) -> None:
    manifest = {
        "days": [
            {
                "id": "07",
                "title": "Prompt authority drift",
                "persistent_constraints": [
                    {
                        "id": "authoritative_retrieval_sources",
                        "type": "business",
                        "description": "Authority must win.",
                        "introduced_on": "03",
                        "persists": True,
                    }
                ],
                "mastery_gates": [
                    {
                        "id": "day07_repo_evidence",
                        "mode": "blocking",
                        "command": "echo ok",
                        "success_marker": "ok",
                        "covers_constraints": ["authoritative_retrieval_sources"],
                        "evidence_source": "artifact",
                    }
                ],
                "automation_drills": [
                    {
                        "id": "drill_11_prompt_authority_drift",
                        "default": True,
                        "mode": "artifact",
                        "name": "Prompt authority drift",
                        "description": "Drive eval drift.",
                        "expected_signal": "authority drift",
                        "source_file": "evals/failure_drills/drill_11_prompt_authority_drift.json",
                        "mutation": "day07_prompt_authority_drift",
                        "repair_targets": [
                            "src/aegisap/day3/policies/source_authority_rules.yaml",
                            "src/aegisap/day3/retrieval/authority_policy.py",
                        ],
                    }
                ],
            }
        ]
    }
    target = tmp_path / "build" / "day7" / "synthetic_cases_drift.jsonl"

    def fake_rebuild_day_artifact(day: str) -> dict:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('{"case_name":"baseline"}\n', encoding="utf-8")
        return {
            "day": day,
            "artifact_path": str(tmp_path / "build" / "day7" / "eval_report.json"),
            "supporting_artifacts": {
                "synthetic_cases_drift_path": str(target),
                "malicious_cases_drift_path": str(tmp_path / "build" / "day7" / "malicious_cases_drift.jsonl"),
            },
        }

    monkeypatch.setattr(drills, "load_manifest", lambda _root=None: manifest)
    monkeypatch.setattr(drills, "_load_drill_metadata", lambda repo_root, drill: {})
    monkeypatch.setattr(drills, "rebuild_day_artifact", fake_rebuild_day_artifact)

    injected = drills.inject_drill(day="07", repo_root=tmp_path)

    assert injected["drill_id"] == "drill_11_prompt_authority_drift"
    assert target.exists()
    assert "authority_drift_missing_vendor_id_01" in target.read_text(encoding="utf-8")
    assert injected["repair_targets"] == [
        "src/aegisap/day3/policies/source_authority_rules.yaml",
        "src/aegisap/day3/retrieval/authority_policy.py",
    ]

    reset = drills.reset_drill(day="07", repo_root=tmp_path)

    assert reset["drill_id"] == "drill_11_prompt_authority_drift"
    assert '{"case_name":"baseline"}' in target.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "day_id,drill_id,mutation,shadow_origin_day,target_rel,baseline_payload",
    [
        (
            "07",
            "drill_12_shadow_reviewer_payload",
            "day07_shadow_reviewer_payload",
            "06",
            "build/day7/eval_report.json",
            {"gate_passed": True},
        ),
        (
            "08",
            "drill_13_shadow_resume_identity_fallback",
            "day08_shadow_resume_identity_fallback",
            "05",
            "build/day8/deployment_design.json",
            {"release_contract": {"oidc_federation": True}},
        ),
        (
            "09",
            "drill_14_shadow_resume_cost_surge",
            "day09_shadow_resume_cost_surge",
            "05",
            "build/day9/routing_report.json",
            {"budget_status": {"within_budget": True}, "sample_ledger": []},
        ),
        (
            "10",
            "drill_15_shadow_evidence_chain_gap",
            "day10_shadow_evidence_chain_gap",
            "08",
            "build/day10/release_envelope.json",
            {"all_passed": True, "gates": []},
        ),
        (
            "11",
            "drill_16_shadow_dependency_forbidden",
            "day11_shadow_dependency_forbidden",
            "10",
            "build/day11/obo_contract.json",
            {"actor_binding_ok": True, "gate_passed": True},
        ),
        (
            "12",
            "drill_17_shadow_egress_detour",
            "day12_shadow_egress_detour",
            "11",
            "build/day12/private_network_posture.json",
            {"all_passed": True, "services": [{"public_reachable": False, "passed": True}]},
        ),
        (
            "13",
            "drill_18_shadow_actor_claim_loss",
            "day13_shadow_actor_claim_loss",
            "11",
            "build/day13/mcp_contract_report.json",
            {"passed": True, "contract_valid": True, "errors": []},
        ),
        (
            "14",
            "drill_19_shadow_compensation_backlog",
            "day14_shadow_compensation_backlog",
            "13",
            "build/day14/trace_correlation_report.json",
            {"passed": True, "correlated": 4, "uncorrelated": 0, "dual_sink_ok": True, "dual_sink_satisfied": True, "details": []},
        ),
    ],
)
def test_shadow_drills_record_metadata_and_only_mutate_current_day_artifacts(
    monkeypatch,
    tmp_path: Path,
    day_id: str,
    drill_id: str,
    mutation: str,
    shadow_origin_day: str,
    target_rel: str,
    baseline_payload: dict,
) -> None:
    manifest = {
        "days": [
            {
                "id": day_id,
                "title": f"Shadow day {day_id}",
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
                        "id": f"day{day_id}_repo_evidence",
                        "mode": "blocking",
                        "command": "echo ok",
                        "success_marker": "ok",
                        "covers_constraints": ["regulated_invoice_auditability"],
                        "evidence_source": "artifact",
                    }
                ],
                "automation_drills": [
                    {
                        "id": drill_id,
                        "default": False,
                        "mode": "artifact",
                        "name": "Shadow drill",
                        "description": "Inject downstream-only shadow symptoms.",
                        "expected_signal": "A downstream symptom appears on one correlation trail.",
                        "mutation": mutation,
                        "shadow_origin_day": shadow_origin_day,
                        "secondary_failure_signal": "The symptom only appears on the same correlation trail.",
                    }
                ],
            }
        ]
    }
    target = tmp_path / target_rel

    def fake_rebuild_day_artifact(day: str) -> dict:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(baseline_payload), encoding="utf-8")
        return {
            "day": day,
            "artifact_path": str(target),
            "supporting_artifacts": {},
        }

    monkeypatch.setattr(drills, "load_manifest", lambda _root=None: manifest)
    monkeypatch.setattr(drills, "_load_drill_metadata", lambda repo_root, drill: {})
    monkeypatch.setattr(drills, "rebuild_day_artifact", fake_rebuild_day_artifact)

    injected = drills.inject_drill(day=day_id, repo_root=tmp_path, drill_id=drill_id)

    assert injected["shadow_origin_day"] == shadow_origin_day
    assert injected["secondary_failure_signal"] == "The symptom only appears on the same correlation trail."
    assert all(f"/day{int(day_id)}" in path for path in injected["mutated_files"])

    mutated = json.loads(target.read_text(encoding="utf-8"))
    mutated_text = json.dumps(mutated)
    assert f"Day {int(shadow_origin_day)}" not in mutated_text
    assert f"day {int(shadow_origin_day)}" not in mutated_text
    assert "correlation" in mutated_text.lower()

    reset = drills.reset_drill(day=day_id, repo_root=tmp_path)

    assert reset["drill_id"] == drill_id
    restored = json.loads(target.read_text(encoding="utf-8"))
    assert restored == baseline_payload
