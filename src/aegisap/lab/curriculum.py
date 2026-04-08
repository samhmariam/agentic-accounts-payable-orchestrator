from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "docs" / "curriculum" / "CURRICULUM_MANIFEST.yaml"
SCHEMA_PATH = ROOT / "docs" / "curriculum" / "curriculum.schema.json"

MODULE_SLUGS = {
    "01": "day_01_trust_boundary",
    "02": "day_02_resilience_ownership",
    "03": "day_03_retrieval_authority",
    "04": "day_04_single_agent_loops",
    "05": "day_05_durable_state",
    "06": "day_06_data_authority",
    "07": "day_07_eval_guardrails",
    "08": "day_08_iac_identity",
    "09": "day_09_observability_cost",
    "10": "day_10_production_acceptance",
    "11": "day_11_delegated_identity",
    "12": "day_12_private_networking",
    "13": "day_13_integration_boundary",
    "14": "day_14_elite_ops",
}

PHASE1_GATE_MODES = {
    "00": "blocking",
    "01": "blocking",
    "02": "advisory",
    "03": "blocking",
    "04": "blocking",
    "05": "blocking",
    "06": "blocking",
    "07": "blocking",
    "08": "blocking",
    "09": "blocking",
    "10": "blocking",
    "11": "blocking",
    "12": "blocking",
    "13": "blocking",
    "14": "blocking",
}


def resolve_repo_root(repo_root: str | Path | None = None) -> Path:
    return Path(repo_root) if repo_root is not None else ROOT


def normalize_day(day: str | int) -> str:
    return f"{int(str(day)):02d}"


def manifest_path(repo_root: str | Path | None = None) -> Path:
    root = resolve_repo_root(repo_root)
    return root / "docs" / "curriculum" / "CURRICULUM_MANIFEST.yaml"


def schema_path(repo_root: str | Path | None = None) -> Path:
    root = resolve_repo_root(repo_root)
    return root / "docs" / "curriculum" / "curriculum.schema.json"


def load_manifest(repo_root: str | Path | None = None) -> dict[str, Any]:
    return yaml.safe_load(manifest_path(repo_root).read_text(encoding="utf-8")) or {}


def day_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(day["id"]): day for day in manifest.get("days", [])}


def get_day(manifest: dict[str, Any], day: str | int) -> dict[str, Any]:
    day_id = normalize_day(day)
    try:
        return day_map(manifest)[day_id]
    except KeyError as exc:
        raise ValueError(f"Unknown curriculum day: {day_id}") from exc


def module_readme_relpath(day: str | int) -> str:
    day_id = normalize_day(day)
    return f"modules/{MODULE_SLUGS[day_id]}/README.md"


def active_constraints_for_day(
    manifest: dict[str, Any], day: str | int
) -> list[dict[str, Any]]:
    return [
        constraint
        for constraint in get_day(manifest, day).get("persistent_constraints", [])
        if not constraint.get("superseded_by")
    ]


def infrastructure_constraints_for_day(
    manifest: dict[str, Any], day: str | int
) -> list[dict[str, Any]]:
    return [
        constraint
        for constraint in active_constraints_for_day(manifest, day)
        if constraint.get("type") == "infrastructure"
    ]

