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
def test_bridge_targets_exist(day: dict) -> None:
    mapping = day["portal_to_script_mapping"]
    missing = []
    for rel_path in mapping["production_targets"]:
        if not (REPO_ROOT / rel_path).exists():
            missing.append(rel_path)
    assert not missing, (
        f"Day {day['id']} production_targets missing:\n"
        + "\n".join(f"  {p}" for p in missing)
    )


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
