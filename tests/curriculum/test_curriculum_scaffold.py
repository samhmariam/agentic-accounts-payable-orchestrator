"""
Curriculum scaffold tests.

Validates structural completeness of CURRICULUM_MANIFEST.yaml and the artifact
files it references. Does not import from src/aegisap — pure curriculum validation.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from aegisap.lab.curriculum import INFRA_SURFACE_TYPES, KQL_EVIDENCE_DAYS, PHASE1_GATE_MODES, expected_scaffold_level

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
    assert total == 47, f"Expected 47 artifact files across all days, got {total}"


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in
                                 yaml.safe_load(MANIFEST_PATH.open())["days"]])
def test_portal_to_script_mapping_declared(day: dict) -> None:
    mapping = day.get("portal_to_script_mapping", {})
    assert mapping.get("portal_surface"), f"Day {day['id']} missing portal_surface"
    assert mapping.get("bridge_file"), f"Day {day['id']} missing bridge_file"
    assert mapping.get("production_targets"), f"Day {day['id']} missing production_targets"
    for target in mapping["production_targets"]:
        assert target["path"], f"Day {day['id']} production target missing path"
        assert target["surface_type"] in {"application", "infrastructure", "ci_cd", "policy", "eval"}


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in
                                 yaml.safe_load(MANIFEST_PATH.open())["days"]])
def test_phase1_metadata_contract_declared(day: dict) -> None:
    assert day["customer_context"], f"Day {day['id']} missing customer_context"
    assert day["cost_of_failure"], f"Day {day['id']} missing cost_of_failure"
    assert day["scaffold_level"] == expected_scaffold_level(day["id"])
    assert day["automation_drills"], f"Day {day['id']} missing automation_drills"
    assert day["persistent_constraints"], f"Day {day['id']} missing persistent_constraints"
    assert day["mastery_gates"], f"Day {day['id']} missing mastery_gates"
    assert day["chaos_gate"], f"Day {day['id']} missing chaos_gate"


def test_day4_declares_stakeholder_inject(days: list[dict]) -> None:
    day = next(item for item in days if item["id"] == "04")
    assert day["stakeholder_inject"]["required_artifacts"]


@pytest.mark.parametrize(
    "day_id,mode",
    [
        ("05", "blocking"),
        ("06", "blocking"),
        ("07", "blocking"),
        ("08", "blocking"),
        ("09", "blocking"),
        ("10", "blocking"),
        ("11", "blocking"),
        ("12", "blocking"),
        ("13", "blocking"),
        ("14", "blocking"),
    ],
)
def test_native_operator_evidence_contract_declared(day_id: str, mode: str, days: list[dict]) -> None:
    day = next(item for item in days if item["id"] == day_id)
    contract = day.get("native_operator_evidence")
    assert contract, f"Day {day_id} missing native_operator_evidence"
    assert contract["mode"] == mode


@pytest.mark.parametrize("day_id", KQL_EVIDENCE_DAYS)
def test_kql_evidence_contract_declared(day_id: str, days: list[dict]) -> None:
    day = next(item for item in days if item["id"] == day_id)
    contract = day.get("kql_evidence")
    assert contract, f"Day {day_id} missing kql_evidence"
    assert contract["artifact_path"] == f"build/day{int(day_id)}/kql_evidence.json"
    assert contract["minimum_queries"] >= 1


def test_day7_default_drill_targets_authority_drift(days: list[dict]) -> None:
    day = next(item for item in days if item["id"] == "07")
    default = next(drill for drill in day["automation_drills"] if drill.get("default"))
    assert default["id"] == "drill_11_prompt_authority_drift"
    assert default["repair_targets"] == [
        "src/aegisap/day3/policies/source_authority_rules.yaml",
        "src/aegisap/day3/retrieval/authority_policy.py",
    ]


def test_days_07_to_14_declare_one_shadow_drift_alternate(days: list[dict]) -> None:
    for day_id in [f"{i:02d}" for i in range(7, 15)]:
        day = next(item for item in days if item["id"] == day_id)
        shadow_drills = [
            drill for drill in day["automation_drills"] if drill.get("shadow_origin_day")
        ]
        assert len(shadow_drills) == 1, f"Day {day_id} expected exactly one shadow drift drill"
        shadow = shadow_drills[0]
        assert shadow["default"] is False
        assert shadow["secondary_failure_signal"]


def test_day10_and_day14_use_cab_board_review_mode(days: list[dict]) -> None:
    day10 = next(item for item in days if item["id"] == "10")
    day14 = next(item for item in days if item["id"] == "14")

    assert day10["review_contract"]["review_mode"] == "cab_board"
    assert day10["review_contract"]["required_review_roles"] == [
        "cab_chair",
        "client_ciso_or_infra_lead",
    ]
    assert day10["review_contract"]["requires_kql_replay"] is True
    assert day10["review_contract"]["requires_revert_proof"] is True
    assert day10["review_contract"]["peer_checklist_file"] == "docs/curriculum/checklists/day10_peer_red_team.md"
    assert day14["review_contract"]["review_mode"] == "cab_board"
    assert day14["review_contract"]["required_review_roles"] == [
        "cab_chair",
        "client_ciso",
        "infra_lead",
    ]
    assert day14["review_contract"]["requires_kql_replay"] is True
    assert day14["review_contract"]["requires_revert_proof"] is True
    assert day14["review_contract"]["peer_checklist_file"] == "docs/curriculum/checklists/day14_peer_red_team.md"


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in
                                 yaml.safe_load(MANIFEST_PATH.open())["days"]])
def test_mastery_gate_modes_follow_phase1_policy(day: dict) -> None:
    expected = PHASE1_GATE_MODES[day["id"]]
    assert all(gate["mode"] == expected for gate in day["mastery_gates"]), (
        f"Day {day['id']} mastery gates must all be {expected}"
    )


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in
                                 yaml.safe_load(MANIFEST_PATH.open())["days"]])
def test_automation_drills_have_one_default(day: dict) -> None:
    defaults = [drill["id"] for drill in day["automation_drills"] if drill.get("default")]
    assert len(defaults) == 1, f"Day {day['id']} expected one default drill, found {defaults}"


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in yaml.safe_load(MANIFEST_PATH.open())["days"]])
def test_drift_layers_declared(day: dict) -> None:
    for drill in day["automation_drills"]:
        assert drill["drift_layers"], f"Day {day['id']} drill {drill['id']} missing drift_layers"


def test_default_drills_use_platform_drift_in_days_4_to_14(days: list[dict]) -> None:
    for day in [item for item in days if item["id"] >= "04"]:
        default = next(drill for drill in day["automation_drills"] if drill.get("default"))
        assert any(layer != "application" for layer in default["drift_layers"])


def test_final_week_default_drills_include_two_non_application_layers(days: list[dict]) -> None:
    for day in [item for item in days if item["id"] >= "10"]:
        default = next(drill for drill in day["automation_drills"] if drill.get("default"))
        non_application = {
            layer for layer in default["drift_layers"] if layer in {"identity", "networking", "iac", "ci_cd"}
        }
        assert len(non_application) >= 2, f"Day {day['id']} default drill drift layers too thin: {default['drift_layers']}"


def test_program_and_final_week_infra_target_ratios(days: list[dict]) -> None:
    targets = [target for day in days for target in day["portal_to_script_mapping"]["production_targets"]]
    infra = [target for target in targets if target["surface_type"] in INFRA_SURFACE_TYPES]
    assert len(infra) / len(targets) >= 0.30

    final_targets = [
        target
        for day in days
        if day["id"] >= "10"
        for target in day["portal_to_script_mapping"]["production_targets"]
    ]
    final_infra = [target for target in final_targets if target["surface_type"] in INFRA_SURFACE_TYPES]
    assert len(final_infra) / len(final_targets) >= 0.50


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
