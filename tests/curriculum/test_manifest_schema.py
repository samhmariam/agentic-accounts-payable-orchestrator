from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

from jsonschema import Draft202012Validator
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
