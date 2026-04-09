"""
Manifest document-link tests.

For every day in CURRICULUM_MANIFEST.yaml, verifies that:
  - notebook_file exists on disk
  - primary_doc_file exists on disk
  - legacy_doc_files are empty for incident-delivery days
  - every artifact_files path exists on disk
  - every portal_to_script_mapping bridge file exists on disk
  - every capstone_b-flagged day doc contains the capstone section marker

Does not import from src/aegisap — pure curriculum validation.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from aegisap.lab.curriculum import module_readme_relpath

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "docs" / "curriculum" / "CURRICULUM_MANIFEST.yaml"
CAPSTONE_MARKER = "CAPSTONE_B"


def _load_days() -> list[dict]:
    with MANIFEST_PATH.open() as fh:
        return yaml.safe_load(fh)["days"]


# Pre-load once at module level for parametrize
_DAYS = _load_days()


# ---------------------------------------------------------------------------
# Notebook files
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in _DAYS])
def test_notebook_file_exists(day: dict) -> None:
    path = REPO_ROOT / day["notebook_file"]
    assert path.exists(
    ), f"Day {day['id']} notebook not found: {day['notebook_file']}"


# ---------------------------------------------------------------------------
# Primary doc files
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in _DAYS])
def test_primary_doc_file_exists(day: dict) -> None:
    path = REPO_ROOT / day["primary_doc_file"]
    assert path.exists(), (
        f"Day {day['id']} primary_doc_file not found: {day['primary_doc_file']}"
    )


# ---------------------------------------------------------------------------
# Legacy doc files (should be empty after the incident-driven redesign)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in _DAYS])
def test_legacy_doc_files_are_empty(day: dict) -> None:
    assert day.get("legacy_doc_files", []) == [], (
        f"Day {day['id']} still declares legacy_doc_files in the manifest; "
        "the redesign should not depend on retained legacy day surfaces."
    )


# ---------------------------------------------------------------------------
# Artifact files
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in _DAYS])
def test_artifact_files_exist(day: dict) -> None:
    missing = []
    for rel_path in day["artifact_files"]:
        if not (REPO_ROOT / rel_path).exists():
            missing.append(rel_path)
    assert not missing, (
        f"Day {day['id']} artifact files missing:\n"
        + "\n".join(f"  {p}" for p in missing)
    )


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in _DAYS])
def test_bridge_file_exists(day: dict) -> None:
    mapping = day["portal_to_script_mapping"]
    path = REPO_ROOT / mapping["bridge_file"]
    assert path.exists(), (
        f"Day {day['id']} bridge_file not found: {mapping['bridge_file']}"
    )


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in _DAYS])
def test_repair_domains_exist(day: dict) -> None:
    mapping = day["portal_to_script_mapping"]
    domains = mapping["repair_domains"]
    assert domains, f"Day {day['id']} repair_domains missing"
    assert all(target["name"].strip() for target in domains)


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in _DAYS])
def test_module_readme_exists_and_has_file_manifest(day: dict) -> None:
    rel_path = module_readme_relpath(day["id"])
    path = REPO_ROOT / rel_path
    assert path.exists(), f"Day {day['id']} module README not found: {rel_path}"
    content = path.read_text(encoding="utf-8")
    assert "## Day X File Manifest" in content
    assert "Do not edit code in this module folder." in content
    assert "aegisap-lab drill inject --day" in content


@pytest.mark.parametrize("day", [pytest.param(d, id=f"day-{d['id']}") for d in _DAYS])
def test_primary_doc_points_to_module_readme(day: dict) -> None:
    rel_path = module_readme_relpath(day["id"])
    content = (REPO_ROOT / day["primary_doc_file"]).read_text(encoding="utf-8")
    assert rel_path in content
    assert "## Automated Drill" in content
    assert "## Cost of Failure" in content


def test_day04_docs_reference_pushback_artifacts() -> None:
    for rel_path in ("docs/DAY_04.md", "modules/day_04_single_agent_loops/README.md"):
        content = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
        assert "SPONSOR_PUSHBACK_EMAIL.md" in content
        assert "ADR-002_irreversible_actions_and_hitl.md" in content


@pytest.mark.parametrize(
    "rel_path",
    [
        "docs/DAY_04.md",
        "modules/day_04_single_agent_loops/README.md",
        "docs/DAY_05.md",
        "modules/day_05_durable_state/README.md",
        "docs/DAY_06.md",
        "modules/day_06_data_authority/README.md",
        "docs/DAY_07.md",
        "modules/day_07_eval_guardrails/README.md",
        "docs/DAY_08.md",
        "modules/day_08_iac_identity/README.md",
        "docs/DAY_09.md",
        "modules/day_09_observability_cost/README.md",
        "docs/DAY_10.md",
        "modules/day_10_production_acceptance/README.md",
        "docs/DAY_11.md",
        "modules/day_11_delegated_identity/README.md",
        "docs/DAY_12.md",
        "modules/day_12_private_networking/README.md",
        "docs/DAY_13.md",
        "modules/day_13_integration_boundary/README.md",
        "docs/DAY_14.md",
        "modules/day_14_elite_ops/README.md",
    ],
)
def test_native_tooling_gate_docs_exist(rel_path: str) -> None:
    content = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
    assert "## Native Tooling Gate" in content
    assert "native_operator_evidence.json" in content
    assert "NATIVE_TOOLING_POLICY.md" in content


@pytest.mark.parametrize(
    "rel_path,day_id",
    [
        ("docs/DAY_05.md", "05"),
        ("modules/day_05_durable_state/README.md", "05"),
        ("docs/DAY_06.md", "06"),
        ("modules/day_06_data_authority/README.md", "06"),
        ("docs/DAY_07.md", "07"),
        ("modules/day_07_eval_guardrails/README.md", "07"),
        ("docs/DAY_08.md", "08"),
        ("modules/day_08_iac_identity/README.md", "08"),
        ("docs/DAY_09.md", "09"),
        ("modules/day_09_observability_cost/README.md", "09"),
        ("docs/DAY_10.md", "10"),
        ("modules/day_10_production_acceptance/README.md", "10"),
        ("docs/DAY_11.md", "11"),
        ("modules/day_11_delegated_identity/README.md", "11"),
        ("docs/DAY_12.md", "12"),
        ("modules/day_12_private_networking/README.md", "12"),
        ("docs/DAY_13.md", "13"),
        ("modules/day_13_integration_boundary/README.md", "13"),
        ("docs/DAY_14.md", "14"),
        ("modules/day_14_elite_ops/README.md", "14"),
    ],
)
def test_kql_evidence_docs_exist(rel_path: str, day_id: str) -> None:
    content = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
    assert "## KQL Evidence" in content
    assert f"build/day{int(day_id)}/kql_evidence.json" in content


@pytest.mark.parametrize(
    "rel_path,checklist_rel",
    [
        ("docs/DAY_10.md", "docs/curriculum/checklists/day10_peer_red_team.md"),
        ("modules/day_10_production_acceptance/README.md", "docs/curriculum/checklists/day10_peer_red_team.md"),
        ("docs/DAY_14.md", "docs/curriculum/checklists/day14_peer_red_team.md"),
        ("modules/day_14_elite_ops/README.md", "docs/curriculum/checklists/day14_peer_red_team.md"),
    ],
)
def test_cab_docs_reference_revert_proof_and_peer_checklist(rel_path: str, checklist_rel: str) -> None:
    content = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
    assert "Revert Proof" in content
    assert checklist_rel in content


@pytest.mark.parametrize(
    "rel_path",
    [
        "docs/DAY_04.md",
        "modules/day_04_single_agent_loops/README.md",
        "docs/DAY_10.md",
        "modules/day_10_production_acceptance/README.md",
    ],
)
def test_machine_readable_native_hygiene_is_documented(rel_path: str) -> None:
    content = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
    assert "-o json" in content


# ---------------------------------------------------------------------------
# Capstone B section marker in flagged day docs
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "day",
    [pytest.param(d, id=f"day-{d['id']}") for d in _DAYS
     if d["capstone_flags"].get("capstone_b")],
)
def test_capstone_b_docs_contain_section_marker(day: dict) -> None:
    doc_path = REPO_ROOT / day["primary_doc_file"]
    if not doc_path.exists():
        pytest.skip(
            f"primary_doc_file not yet created: {day['primary_doc_file']}")
    content = doc_path.read_text(encoding="utf-8")
    assert CAPSTONE_MARKER in content, (
        f"Day {day['id']} primary doc '{day['primary_doc_file']}' "
        f"does not contain the capstone marker '{CAPSTONE_MARKER}'"
    )
