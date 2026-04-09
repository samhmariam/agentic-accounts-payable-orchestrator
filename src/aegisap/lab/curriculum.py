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

SCAFFOLD_LEVELS = {
    "01": "guided",
    "02": "guided",
    "03": "guided",
    "04": "guided",
    "05": "guided",
    "06": "guided",
    "07": "guided",
    "08": "starter_only",
    "09": "starter_only",
    "10": "starter_only",
    "11": "starter_only",
    "12": "starter_only",
    "13": "starter_only",
    "14": "starter_only",
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

INFRA_SURFACE_TYPES = {"infrastructure", "ci_cd"}
KQL_EVIDENCE_DAYS = tuple(f"{day:02d}" for day in range(5, 15))
DIAGNOSTIC_INDEPENDENCE_DAYS = tuple(f"{day:02d}" for day in range(8, 15))
RAW_SDK_NOTEBOOK_BAN_DAYS = tuple(f"{day:02d}" for day in range(5, 15))


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


def expected_scaffold_level(day: str | int) -> str:
    return SCAFFOLD_LEVELS[normalize_day(day)]


def production_targets_for_day_entry(day_entry: dict[str, Any]) -> list[dict[str, Any]]:
    return day_entry.get("portal_to_script_mapping", {}).get("repair_domains", [])


def production_target_paths(day_entry: dict[str, Any]) -> list[str]:
    return [target["name"] for target in production_targets_for_day_entry(day_entry)]


def production_target_counts(day_entries: list[dict[str, Any]]) -> tuple[int, int]:
    infra_targets = 0
    total_targets = 0
    for day_entry in day_entries:
        for target in production_targets_for_day_entry(day_entry):
            total_targets += 1
            if target.get("surface_type") in INFRA_SURFACE_TYPES:
                infra_targets += 1
    return infra_targets, total_targets


def repair_domains_for_day_entry(day_entry: dict[str, Any]) -> list[dict[str, Any]]:
    return production_targets_for_day_entry(day_entry)


def incident_asset_ref_for_day_entry(day_entry: dict[str, Any]) -> str:
    return str(day_entry.get("incident_asset_ref") or f"day{day_entry['id']}").strip()


def scenario_relpath_from_asset_ref(day_entry: dict[str, Any]) -> str:
    ref = incident_asset_ref_for_day_entry(day_entry)
    normalized = normalize_day(day_entry["id"])
    if ref in {f"day{normalized}", normalized}:
        return f"scenarios/day{normalized}"
    return ref


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


def default_drill_for_day(
    manifest: dict[str, Any], day: str | int
) -> dict[str, Any]:
    drills = get_day(manifest, day).get("automation_drills", [])
    if not drills:
        raise ValueError(f"Day {normalize_day(day)} has no automation_drills.")
    for drill in drills:
        if drill.get("default") is True:
            return drill
    return drills[0]


def drill_map_for_day(
    manifest: dict[str, Any], day: str | int
) -> dict[str, dict[str, Any]]:
    return {
        drill["id"]: drill
        for drill in get_day(manifest, day).get("automation_drills", [])
    }


def get_drill(
    manifest: dict[str, Any], day: str | int, drill_id: str | None = None
) -> dict[str, Any]:
    if drill_id is None:
        return default_drill_for_day(manifest, day)
    try:
        return drill_map_for_day(manifest, day)[drill_id]
    except KeyError as exc:
        raise ValueError(f"Unknown drill `{drill_id}` for day {normalize_day(day)}") from exc


def constraint_lineage_for_day(
    manifest: dict[str, Any], day: str | int
) -> dict[str, Any]:
    day_id = normalize_day(day)
    day_entry = get_day(manifest, day_id)
    active_constraints = active_constraints_for_day(manifest, day_id)
    gates = day_entry.get("mastery_gates", [])
    lineage = []
    for constraint in active_constraints:
        coverage = [
            {
                "gate_id": gate["id"],
                "mode": gate["mode"],
                "evidence_source": gate["evidence_source"],
                "command": gate["command"],
            }
            for gate in gates
            if constraint["id"] in gate.get("covers_constraints", [])
        ]
        lineage.append(
            {
                "id": constraint["id"],
                "type": constraint["type"],
                "introduced_on": constraint["introduced_on"],
                "description": constraint["description"],
                "covered_by": coverage,
            }
        )
    return {
        "day": day_id,
        "title": day_entry["title"],
        "active_constraints": lineage,
    }
