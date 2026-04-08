from __future__ import annotations

from pathlib import Path
import subprocess

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "docs" / "curriculum" / "CURRICULUM_MANIFEST.yaml"
INCIDENT_SECTIONS = (
    "## Incident",
    "## Portal Investigation",
    "## Lab Repair",
    "## Why This Fails In Prod",
    "## Codification Bridge",
    "## Production Patch",
    "## Verification",
    "## Chaos Gate",
    "## Map the Gap",
    "## PR Defense",
)
INCIDENT_NOTEBOOKS = {
    "01": "day_1_agentic_fundamentals.py",
    "02": "day_2_requirements_architecture.py",
    "03": "day_3_azure_ai_services.py",
    "04": "day_4_single_agent_loops.py",
    "05": "day_5_multi_agent_orchestration.py",
    "06": "day_6_data_ml_integration.py",
    "07": "day_7_testing_eval_guardrails.py",
    "08": "day_8_cicd_iac_deployment.py",
    "09": "day_9_scaling_monitoring_cost.py",
    "10": "day_10_production_operations.py",
    "11": "day_11_delegated_identity_obo.py",
    "12": "day_12_private_networking_constraints.py",
    "13": "day_13_integration_boundary_and_mcp.py",
    "14": "day_14_breaking_changes_elite_ops.py",
}
RETIRED_LITERALS_BY_DAY = {
    "01": (
        "docs/curriculum/portal/DAY_01_PORTAL.md",
        "docs/curriculum/trainee/DAY_01_TRAINEE.md",
        "scripts/run_day1_intake.py",
    ),
    "02": (
        "docs/curriculum/portal/DAY_02_PORTAL.md",
        "docs/curriculum/trainee/DAY_02_TRAINEE.md",
        "scripts/run_day2_workflow.py",
    ),
    "03": (
        "docs/curriculum/portal/DAY_03_PORTAL.md",
        "docs/curriculum/trainee/DAY_03_TRAINEE.md",
        "scripts/run_day3_case.py",
    ),
    "04": (
        "docs/curriculum/portal/DAY_04_PORTAL.md",
        "docs/curriculum/trainee/DAY_04_TRAINEE.md",
        "scripts/run_day4_case.py",
    ),
    "05": (
        "docs/curriculum/portal/DAY_05_PORTAL.md",
        "docs/curriculum/trainee/DAY_05_TRAINEE.md",
        "scripts/run_day5_pause_resume.py",
        "scripts/resume_day5_case.py",
    ),
    "06": (
        "docs/curriculum/portal/DAY_06_PORTAL.md",
        "docs/curriculum/trainee/DAY_06_TRAINEE.md",
        "scripts/run_day6_case.py",
    ),
    "07": (
        "docs/curriculum/portal/DAY_07_PORTAL.md",
        "docs/curriculum/trainee/DAY_07_TRAINEE.md",
    ),
    "08": (
        "docs/curriculum/portal/DAY_08_PORTAL.md",
        "docs/curriculum/trainee/DAY_08_TRAINEE.md",
        "docs/DAY_08_IAC_IDENTITY_RELEASE_OWNERSHIP.md",
    ),
    "09": (
        "docs/curriculum/portal/DAY_09_PORTAL.md",
        "docs/curriculum/trainee/DAY_09_TRAINEE.md",
        "docs/day9/DAY_09_COST_SPEED_ROUTING_CACHING_AND_OPTIMISATION.md",
    ),
    "10": (
        "docs/curriculum/portal/DAY_10_PORTAL.md",
        "docs/curriculum/trainee/DAY_10_TRAINEE.md",
        "docs/DAY_10_DEPLOYMENT_AND_ACCEPTANCE.md",
    ),
    "11": (
        "docs/curriculum/portal/DAY_11_PORTAL.md",
        "docs/DAY_11_DELEGATED_IDENTITY.md",
    ),
    "12": (
        "docs/curriculum/portal/DAY_12_PORTAL.md",
        "docs/DAY_12_PRIVATE_NETWORKING.md",
    ),
    "13": (
        "docs/curriculum/portal/DAY_13_PORTAL.md",
        "docs/DAY_13_INTEGRATION_AND_MCP.md",
    ),
    "14": (
        "docs/curriculum/portal/DAY_14_PORTAL.md",
        "docs/DAY_14_BREAKING_CHANGES.md",
    ),
}


def _load_manifest() -> dict:
    return yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_manifest_wave4_days_include_incident_contract_fields() -> None:
    manifest = _load_manifest()
    days = {day["id"]: day for day in manifest["days"]}

    for day_id in INCIDENT_NOTEBOOKS:
        day = days[day_id]
        assert day["phase"]
        assert day["scenario_dir"]
        assert day["injection_command"] == f"uv run aegisap-lab incident start --day {day_id}"
        assert day["revert_state"] == f".aegisap-lab/state/day{day_id}.json"
        assert day["verification_commands"]
        assert day["portal_to_script_mapping"]["bridge_file"]
        assert day["portal_to_script_mapping"]["production_targets"]
        assert day["review_contract"]["human_required"] is True


def test_wave4_scenarios_expose_required_lifecycle_hooks() -> None:
    for day_id in INCIDENT_NOTEBOOKS:
        scenario_path = REPO_ROOT / "scenarios" / f"day{day_id}" / "scenario.yaml"
        payload = yaml.safe_load(scenario_path.read_text(encoding="utf-8"))

        assert payload["setup"]["apply_diff"]
        assert payload["setup"]["azure_script"]
        assert payload["setup"]["customer_drop"]
        assert payload["validation"]["reproduce_command"]
        assert payload["validation"]["ci_command"]
        assert "revert_diff" in payload["teardown"]
        assert "azure_script" in payload["teardown"]
        assert "cleanup" in payload["teardown"]
        assert payload["review"]["evaluator_profile"]
        assert payload["baseline_track"]
        assert payload["baseline_reprovision_command"]


def test_wave4_scenario_patches_apply_cleanly_against_repo_index() -> None:
    for day_id in INCIDENT_NOTEBOOKS:
        scenario_path = REPO_ROOT / "scenarios" / f"day{day_id}" / "scenario.yaml"
        payload = yaml.safe_load(scenario_path.read_text(encoding="utf-8"))
        patch_rel = payload["setup"]["apply_diff"]
        patch_path = scenario_path.parent / patch_rel

        assert patch_path.exists(), f"Missing scenario patch for day {day_id}: {patch_rel}"
        patch_text = patch_path.read_text(encoding="utf-8")
        for sentinel in (
            "*** Begin Patch",
            "*** End Patch",
            "*** Add File:",
            "*** Update File:",
            "*** Delete File:",
        ):
            assert sentinel not in patch_text, (
                f"Scenario patch for day {day_id} contains apply_patch sentinel text: {sentinel}"
            )
        result = subprocess.run(
            ["git", "apply", "--check", "--cached", str(patch_path.relative_to(REPO_ROOT))],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, (
            f"Scenario patch for day {day_id} does not apply cleanly: "
            f"{(result.stderr or result.stdout).strip()}"
        )


def test_wave4_notebooks_use_incident_scaffold_and_markdown_only_patch_boundary() -> None:
    for day_id, notebook_name in INCIDENT_NOTEBOOKS.items():
        path = REPO_ROOT / "notebooks" / notebook_name
        text = path.read_text(encoding="utf-8")
        for section in INCIDENT_SECTIONS:
            assert section in text, f"Notebook {day_id} is missing {section}"
        assert "markdown-only" in text
        assert "Do not edit repo files from this notebook" in text
        assert "List three specific ways this notebook logic fails in an Azure Container App." in text
        assert "STOP. Close this notebook." in text
        assert "### Export to Production" in text
        assert "What trade-off did I make today to satisfy the customer constraint?" in text
        assert "What is the blast radius if my code fails?" in text
        assert "How will I know it failed in production?" in text
        assert "cohort/<" in text


def test_wave4_notebooks_do_not_reference_retired_learner_entry_surfaces() -> None:
    for day_id, notebook_name in INCIDENT_NOTEBOOKS.items():
        path = REPO_ROOT / "notebooks" / notebook_name
        text = path.read_text(encoding="utf-8")
        for literal in RETIRED_LITERALS_BY_DAY[day_id]:
            assert literal not in text, f"{path.name} still references {literal}"


def test_learner_notebooks_do_not_mutate_repo_tracked_paths() -> None:
    forbidden_literals = (
        "apply_patch(",
        "git apply",
        "git checkout",
    )
    forbidden_targets = ("src/", "infra/", "tests/")

    for notebook_name in INCIDENT_NOTEBOOKS.values():
        path = REPO_ROOT / "notebooks" / notebook_name
        text = path.read_text(encoding="utf-8")
        for literal in forbidden_literals:
            assert literal not in text, f"{path.name} contains forbidden mutation literal {literal}"
        if "write_text(" in text:
            assert not any(target in text for target in forbidden_targets), (
                f"{path.name} appears to write to a repo-tracked path"
            )
