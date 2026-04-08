"""
Curriculum scaffold tests.

Validates structural completeness of CURRICULUM_MANIFEST.yaml and the artifact
files it references. Does not import from src/aegisap — pure curriculum validation.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from aegisap.lab.curriculum import PHASE1_GATE_MODES

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "docs" / "curriculum" / "CURRICULUM_MANIFEST.yaml"

DAYS_WITH_ZERO_TOLERANCE = {"07", "10", "11", "12", "14"}
DAYS_WITH_CAPSTONE_B = {"12", "13", "14"}


@pytest.fixture(scope="module")
def manifest() -> dict:
    with MANIFEST_PATH.open() as fh:
        return yaml.safe_load(fh)


@pytest.fixture(scope="module")
def days(manifest: dict) -> list[dict]:
    return manifest["days"]


# ---------------------------------------------------------------------------
# Top-level manifest structure
# ---------------------------------------------------------------------------


def test_manifest_has_14_days(days: list[dict]) -> None:
    assert len(days) == 14, f"Expected 14 days, got {len(days)}"


def test_day_ids_are_sequential(days: list[dict]) -> None:
    ids = [d["id"] for d in days]
    expected = [f"{n:02d}" for n in range(1, 15)]
    assert ids == expected


def test_pass_bars_defined(manifest: dict) -> None:
    assert manifest["daily_pass_bar"] == 80
    assert manifest["elite_pass_bar"] == 90


def test_customer_profile_declared(manifest: dict) -> None:
    profile = manifest["customer_profile"]
    assert profile["name"]
    assert profile["operating_context"]
    assert profile["non_negotiables"]


# ---------------------------------------------------------------------------
# Per-day rubric weights
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in
                                 yaml.safe_load(MANIFEST_PATH.open())["days"]])
def test_rubric_weights_sum_to_100(day: dict) -> None:
    weights = day["rubric_weights"]
    total = sum(weights.values())
    assert total == 100, (
        f"Day {day['id']} rubric weights sum to {total}, expected 100. "
        f"Weights: {weights}"
    )


# ---------------------------------------------------------------------------
# Artifact files exist on disk
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in
                                 yaml.safe_load(MANIFEST_PATH.open())["days"]])
def test_all_artifact_files_exist(day: dict) -> None:
    missing = []
    for rel_path in day["artifact_files"]:
        full = REPO_ROOT / rel_path
        if not full.exists():
            missing.append(rel_path)
    assert not missing, (
        f"Day {day['id']} is missing artifact files:\n"
        + "\n".join(f"  {p}" for p in missing)
    )


def test_total_artifact_count(days: list[dict]) -> None:
    total = sum(len(d["artifact_files"]) for d in days)
    assert total == 43, f"Expected 43 artifact files across all days, got {total}"


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in
                                 yaml.safe_load(MANIFEST_PATH.open())["days"]])
def test_portal_to_script_mapping_declared(day: dict) -> None:
    mapping = day.get("portal_to_script_mapping", {})
    assert mapping.get("portal_surface"), f"Day {day['id']} missing portal_surface"
    assert mapping.get("bridge_file"), f"Day {day['id']} missing bridge_file"
    assert mapping.get("production_targets"), f"Day {day['id']} missing production_targets"


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in
                                 yaml.safe_load(MANIFEST_PATH.open())["days"]])
def test_phase1_metadata_contract_declared(day: dict) -> None:
    assert day["customer_context"], f"Day {day['id']} missing customer_context"
    assert day["persistent_constraints"], f"Day {day['id']} missing persistent_constraints"
    assert day["mastery_gates"], f"Day {day['id']} missing mastery_gates"
    assert day["chaos_gate"], f"Day {day['id']} missing chaos_gate"


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in
                                 yaml.safe_load(MANIFEST_PATH.open())["days"]])
def test_mastery_gate_modes_follow_phase1_policy(day: dict) -> None:
    expected = PHASE1_GATE_MODES[day["id"]]
    assert all(gate["mode"] == expected for gate in day["mastery_gates"]), (
        f"Day {day['id']} mastery gates must all be {expected}"
    )


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in
                                 yaml.safe_load(MANIFEST_PATH.open())["days"]])
def test_infrastructure_constraints_require_cloud_probe_gate(day: dict) -> None:
    infra_ids = [
        constraint["id"]
        for constraint in day["persistent_constraints"]
        if constraint["type"] == "infrastructure" and not constraint.get("superseded_by")
    ]
    if not infra_ids:
        return
    covered = {
        constraint_id
        for gate in day["mastery_gates"]
        if gate["evidence_source"] == "cloud_probe"
        and f"uv run aegisap-lab audit-production --day {day['id']} --strict" in gate["command"]
        for constraint_id in gate["covers_constraints"]
    }
    assert set(infra_ids).issubset(covered), (
        f"Day {day['id']} infrastructure constraints missing cloud-truth audit coverage: "
        f"{sorted(set(infra_ids) - covered)}"
    )


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in
                                 yaml.safe_load(MANIFEST_PATH.open())["days"]])
def test_persistent_constraints_accumulate(day: dict, days: list[dict]) -> None:
    day_index = int(day["id"]) - 1
    if day_index == 0:
        return
    previous = days[day_index - 1]
    previous_active = {
        constraint["id"]
        for constraint in previous["persistent_constraints"]
        if not constraint.get("superseded_by")
    }
    current_active = {
        constraint["id"]
        for constraint in day["persistent_constraints"]
        if not constraint.get("superseded_by")
    }
    assert previous_active.issubset(current_active), (
        f"Day {day['id']} dropped inherited constraints: {sorted(previous_active - current_active)}"
    )


# ---------------------------------------------------------------------------
# Oral defense prompts
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in
                                 yaml.safe_load(MANIFEST_PATH.open())["days"]])
def test_oral_defense_prompts_count(day: dict) -> None:
    prompts = day["oral_defense_prompts"]
    assert len(prompts) >= 3, (
        f"Day {day['id']} has {len(prompts)} oral defense prompt(s); need >= 3"
    )


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in
                                 yaml.safe_load(MANIFEST_PATH.open())["days"]])
def test_oral_defense_prompts_non_empty(day: dict) -> None:
    for i, prompt in enumerate(day["oral_defense_prompts"]):
        assert prompt and prompt.strip(), (
            f"Day {day['id']} oral defense prompt {i} is blank"
        )


# ---------------------------------------------------------------------------
# Zero-tolerance items
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("day_id", sorted(DAYS_WITH_ZERO_TOLERANCE))
def test_zero_tolerance_non_empty_for_required_days(day_id: str, days: list[dict]) -> None:
    day = next(d for d in days if d["id"] == day_id)
    zt = day.get("zero_tolerance", [])
    assert zt, f"Day {day_id} must have at least one zero_tolerance item"


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in
                                 yaml.safe_load(MANIFEST_PATH.open())["days"]])
def test_zero_tolerance_items_have_hard_fail_consequence(day: dict) -> None:
    for item in day.get("zero_tolerance", []):
        assert item.get("consequence") == "hard_fail", (
            f"Day {day['id']} zero_tolerance item '{item.get('condition')}' "
            f"has consequence '{item.get('consequence')}', expected 'hard_fail'"
        )


# ---------------------------------------------------------------------------
# Capstone B flags
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("day_id", sorted(DAYS_WITH_CAPSTONE_B))
def test_capstone_b_flagged_on_required_days(day_id: str, days: list[dict]) -> None:
    day = next(d for d in days if d["id"] == day_id)
    assert day["capstone_flags"]["capstone_b"] is True, (
        f"Day {day_id} must have capstone_b: true"
    )


# ---------------------------------------------------------------------------
# Capstone B fixture files
# ---------------------------------------------------------------------------


def test_capstone_b_claims_intake_trainee_files() -> None:
    folder = REPO_ROOT / "fixtures" / "capstone_b" / "claims_intake"
    assert folder.exists(), f"Missing fixture folder: {folder}"
    files = list(folder.iterdir())
    assert len(files) == 6, (
        f"Expected 6 files in claims_intake (5 cases + README), found {len(files)}: "
        + ", ".join(f.name for f in files)
    )


def test_capstone_b_claims_intake_assessor_file() -> None:
    hidden = (
        REPO_ROOT / "fixtures" / "capstone_b" / "_assessor_only" / "claims_intake"
        / "claim_006_assessor_only.json"
    )
    assert hidden.exists(), f"Missing hidden assessor case: {hidden}"


def test_capstone_b_customer_onboarding_files() -> None:
    folder = REPO_ROOT / "fixtures" / "capstone_b" / "customer_onboarding"
    assert folder.exists(), f"Missing fixture folder: {folder}"
    files = list(folder.iterdir())
    assert len(files) == 3, (
        f"Expected 3 files in customer_onboarding (2 cases + README), found {len(files)}: "
        + ", ".join(f.name for f in files)
    )
