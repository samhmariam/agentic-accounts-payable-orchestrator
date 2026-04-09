from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

from jsonschema import Draft202012Validator
import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "docs" / "curriculum" / "CURRICULUM_MANIFEST.yaml"
SCHEMA_PATH = REPO_ROOT / "docs" / "curriculum" / "curriculum.schema.json"


def _load_validator_module():
    spec = importlib.util.spec_from_file_location(
        "validate_curriculum", REPO_ROOT / "scripts" / "validate_curriculum.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_manifest_validates_against_schema() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(manifest))
    assert not errors, [error.message for error in errors]


def test_invalid_mastery_gate_mode_fails_schema() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    broken = copy.deepcopy(manifest)
    broken["days"][0]["mastery_gates"][0]["mode"] = "maybe"
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(broken))
    assert any("maybe" in error.message for error in errors)


def test_superseded_constraint_requires_reason_and_approver() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    broken = copy.deepcopy(manifest)
    broken["days"][3]["persistent_constraints"][0]["superseded_by"] = "replacement_rule"
    broken["days"][3]["persistent_constraints"][0].pop("supersession_reason", None)
    broken["days"][3]["persistent_constraints"][0].pop("approver_role", None)

    module = _load_validator_module()
    errors: list[str] = []
    module._validate_manifest(errors, broken)

    assert any("superseded constraint" in error for error in errors)


@pytest.mark.parametrize("day_index", [1, 3])
def test_triads_days_stakeholder_inject_declared(day_index: int) -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    day_entry = manifest["days"][day_index]

    inject = day_entry["stakeholder_inject"]

    assert inject["requester_role"]
    assert inject["channel"]
    assert inject["unsafe_request"]
    assert inject["delivery_mode"] == "triad_roleplay"
    assert inject["script_path"]
    assert inject["capture_artifact"]
    assert inject["observer_scorecard"]


def test_native_operator_evidence_contracts_exist_on_days_04_to_14() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    days = {day["id"]: day for day in manifest["days"]}

    for day_id in [f"{i:02d}" for i in range(4, 15)]:
        assert days[day_id]["native_operator_evidence"]["mode"] == "blocking"
        assert days[day_id]["native_operator_evidence"]["artifact_path"] == f"build/day{int(day_id)}/native_operator_evidence.json"
        assert days[day_id]["native_operator_evidence"]["must_use_json_output"] is True
        assert days[day_id]["native_operator_evidence"]["required_signal_families"]

    assert days["09"]["native_operator_evidence"]["review_stage"] == "day10_cab_board"
    assert days["12"]["native_operator_evidence"]["mode"] == "blocking"
    assert days["12"]["native_operator_evidence"]["live_demo_required"] is True
    assert days["14"]["native_operator_evidence"]["mode"] == "blocking"
    assert days["14"]["native_operator_evidence"]["review_stage"] == "capstone_cab_board"


def test_day10_rollback_rehearsal_contract_declared() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    days = {day["id"]: day for day in manifest["days"]}
    contract = days["10"]["rollback_rehearsal"]
    assert contract["artifact_path"] == "build/day10/rollback_rehearsal.json"
    assert contract["traffic_shift_required"] is True
    assert contract["command_patterns"]
    assert contract["verification_patterns"]


def test_kql_evidence_contracts_exist_on_days_5_to_14() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    days = {day["id"]: day for day in manifest["days"]}

    for day_id in [f"{i:02d}" for i in range(5, 15)]:
        contract = days[day_id]["kql_evidence"]
        assert contract["artifact_path"] == f"build/day{int(day_id)}/kql_evidence.json"
        assert contract["minimum_queries"] >= 1
        if day_id >= "08":
            assert contract["minimum_pre_patch_queries"] >= 1


def test_diagnostic_independence_contracts_exist_on_days_8_to_14() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    days = {day["id"]: day for day in manifest["days"]}

    for day_id in [f"{i:02d}" for i in range(8, 15)]:
        contract = days[day_id]["diagnostic_independence"]
        assert contract["mode"] == "advisory"
        assert contract["timeline_artifact_path"] == f"build/day{int(day_id)}/diagnostic_timeline.md"
        assert contract["hint_state_path"] == f".aegisap-lab/cache/instructor/interventions/day{day_id}.json"


def test_scaffold_levels_follow_day_band() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    days = {day["id"]: day for day in manifest["days"]}

    for day_id in [f"{i:02d}" for i in range(1, 8)]:
        assert days[day_id]["scaffold_level"] == "guided"
    for day_id in [f"{i:02d}" for i in range(7, 15)]:
        expected = "guided" if day_id == "07" else "starter_only"
        assert days[day_id]["scaffold_level"] == expected
