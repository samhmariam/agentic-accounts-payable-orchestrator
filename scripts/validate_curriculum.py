#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - depends on local env
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "docs" / "curriculum" / "CURRICULUM_MANIFEST.yaml"

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "notebooks"))

PATH_PREFIXES = (
    "docs/",
    "notebooks/",
    "scripts/",
    "src/",
    "infra/",
    "evals/",
    ".github/workflows/",
)

TRAINEE_REQUIRED_HEADINGS = (
    "## Lab Readiness",
    "### Pass Criteria",
    "### Common Failure Signals",
    "### Exit Ticket",
    "### Remediation Task",
    "### Stretch Task",
)

TRAINER_REQUIRED_HEADINGS = (
    "## Facilitation Addendum",
    "### Observable Mastery Signals",
    "### Intervention Cues",
    "### Fallback Path",
    "### Exit Ticket Answer Key",
    "### Time-box Guidance",
)

PORTAL_REQUIRED_HEADINGS = (
    "## Portal-First Outcome",
    "## Portal Mode",
    "## Azure Portal Path",
    "## What To Capture",
    "## Handoff To Notebook",
    "## Handoff To Automation",
)

REQUIRED_DOCS = (
    "docs/curriculum/README.md",
    "docs/curriculum/DELIVERY_MAP.md",
    "docs/curriculum/portal/README.md",
    "docs/curriculum/TRAINER_OPERATIONS.md",
    "docs/curriculum/TRAINEE_PREFLIGHT_CHECKLIST.md",
    "docs/curriculum/FACILITATOR_DAY_START_CHECKLIST.md",
    "docs/curriculum/ASSESSMENT_RUBRIC.md",
    "docs/curriculum/GRADUATION_RUBRIC.md",
    "docs/curriculum/ASSESSOR_CALIBRATION.md",
    "docs/curriculum/CAPSTONE_REVIEW.md",
    "docs/curriculum/CAPSTONE_PR_REVIEW.md",
    "docs/curriculum/CAPSTONE_B_TRANSFER.md",
    "docs/curriculum/INCIDENT_DRILL_RUNBOOK.md",
    "docs/curriculum/PILOT_MEASUREMENT_PLAN.md",
    "docs/curriculum/GRADUATE_PROFILE.md",
    "docs/curriculum/CURRICULUM_MANIFEST.yaml",
    "docs/curriculum/templates/DAILY_ARTIFACT_PACK.md",
    "docs/curriculum/templates/DAILY_SCORECARD.md",
    "docs/curriculum/templates/ORAL_DEFENSE_SCORECARD.md",
    "docs/curriculum/templates/PILOT_RETRO.md",
)

STRICT_VALIDATION_DOCS = (
    "docs/curriculum/README.md",
    "docs/curriculum/DELIVERY_MAP.md",
    "docs/curriculum/portal/README.md",
    "docs/curriculum/TRAINER_OPERATIONS.md",
    "docs/curriculum/TRAINEE_PREFLIGHT_CHECKLIST.md",
    "docs/curriculum/FACILITATOR_DAY_START_CHECKLIST.md",
    "docs/curriculum/CAPSTONE_REVIEW.md",
    "docs/curriculum/CAPSTONE_PR_REVIEW.md",
    "docs/curriculum/CAPSTONE_B_TRANSFER.md",
    "docs/curriculum/INCIDENT_DRILL_RUNBOOK.md",
    "docs/curriculum/PILOT_MEASUREMENT_PLAN.md",
    "docs/curriculum/GRADUATE_PROFILE.md",
    "docs/curriculum/templates/DAILY_ARTIFACT_PACK.md",
    "docs/curriculum/templates/DAILY_SCORECARD.md",
    "docs/curriculum/templates/ORAL_DEFENSE_SCORECARD.md",
    "docs/curriculum/templates/PILOT_RETRO.md",
)

README_REQUIRED_SNIPPETS = (
    "DELIVERY_MAP.md",
    "portal/README.md",
    "TRAINEE_PREFLIGHT_CHECKLIST.md",
    "FACILITATOR_DAY_START_CHECKLIST.md",
    "## Mandatory Checkpoints",
    "build/day4/checkpoint_policy_overlay.json",
    "build/day8/checkpoint_trace_extension.json",
    "build/day10/checkpoint_gate_extension.json",
    "## Capstone Review Flow",
    "build/capstone/<trainee_id>/release_packet.json",
    "CURRICULUM_MANIFEST.yaml",
)

TRAINER_OPS_REQUIRED_SNIPPETS = (
    "FACILITATOR_DAY_START_CHECKLIST.md",
    "portal/README.md",
    "TRAINEE_PREFLIGHT_CHECKLIST.md",
    "Daily Operating Rhythm",
    "Learner Status Model",
)

PREFLIGHT_REQUIRED_SNIPPETS = (
    "uv sync --extra dev --extra day9",
    "az login",
    "scripts/verify_env.py",
    "scripts/setup-env.sh",
)

FACILITATOR_REQUIRED_SNIPPETS = (
    "uv run python scripts/validate_curriculum.py",
    "CURRICULUM_MANIFEST.yaml",
    "docs/curriculum/portal/DAY_00_PORTAL.md",
    "uv run aegisap-lab incident start --day",
    "Day 8",
    "Day 11",
    "Day 12",
    "Day 13",
    "Day 14",
)

INCIDENT_NOTEBOOK_SECTIONS = (
    "## Incident",
    "## Portal Investigation",
    "## Lab Repair",
    "## Production Patch",
    "## Verification",
    "## PR Defense",
)

INCIDENT_NOTEBOOKS = {
    1: "notebooks/day_1_agentic_fundamentals.py",
    2: "notebooks/day_2_requirements_architecture.py",
    3: "notebooks/day_3_azure_ai_services.py",
    4: "notebooks/day_4_single_agent_loops.py",
    5: "notebooks/day_5_multi_agent_orchestration.py",
    6: "notebooks/day_6_data_ml_integration.py",
    7: "notebooks/day_7_testing_eval_guardrails.py",
    8: "notebooks/day_8_cicd_iac_deployment.py",
    9: "notebooks/day_9_scaling_monitoring_cost.py",
    10: "notebooks/day_10_production_operations.py",
    11: "notebooks/day_11_delegated_identity_obo.py",
    12: "notebooks/day_12_private_networking_constraints.py",
    13: "notebooks/day_13_integration_boundary_and_mcp.py",
    14: "notebooks/day_14_breaking_changes_elite_ops.py",
}

INCIDENT_RETIRED_REFERENCES = {
    1: (
        "docs/curriculum/portal/DAY_01_PORTAL.md",
        "docs/curriculum/trainee/DAY_01_TRAINEE.md",
        "scripts/run_day1_intake.py",
    ),
    2: (
        "docs/curriculum/portal/DAY_02_PORTAL.md",
        "docs/curriculum/trainee/DAY_02_TRAINEE.md",
        "scripts/run_day2_workflow.py",
    ),
    3: (
        "docs/curriculum/portal/DAY_03_PORTAL.md",
        "docs/curriculum/trainee/DAY_03_TRAINEE.md",
        "scripts/run_day3_case.py",
    ),
    4: (
        "docs/curriculum/portal/DAY_04_PORTAL.md",
        "docs/curriculum/trainee/DAY_04_TRAINEE.md",
        "scripts/run_day4_case.py",
    ),
    5: (
        "docs/curriculum/portal/DAY_05_PORTAL.md",
        "docs/curriculum/trainee/DAY_05_TRAINEE.md",
        "scripts/run_day5_pause_resume.py",
        "scripts/resume_day5_case.py",
    ),
    6: (
        "docs/curriculum/portal/DAY_06_PORTAL.md",
        "docs/curriculum/trainee/DAY_06_TRAINEE.md",
        "scripts/run_day6_case.py",
    ),
    7: (
        "docs/curriculum/portal/DAY_07_PORTAL.md",
        "docs/curriculum/trainee/DAY_07_TRAINEE.md",
    ),
    8: (
        "docs/curriculum/portal/DAY_08_PORTAL.md",
        "docs/curriculum/trainee/DAY_08_TRAINEE.md",
        "docs/DAY_08_IAC_IDENTITY_RELEASE_OWNERSHIP.md",
    ),
    9: (
        "docs/curriculum/portal/DAY_09_PORTAL.md",
        "docs/curriculum/trainee/DAY_09_TRAINEE.md",
        "docs/day9/DAY_09_COST_SPEED_ROUTING_CACHING_AND_OPTIMISATION.md",
    ),
    10: (
        "docs/curriculum/portal/DAY_10_PORTAL.md",
        "docs/curriculum/trainee/DAY_10_TRAINEE.md",
        "docs/DAY_10_DEPLOYMENT_AND_ACCEPTANCE.md",
    ),
    11: (
        "docs/curriculum/portal/DAY_11_PORTAL.md",
        "docs/DAY_11_DELEGATED_IDENTITY.md",
    ),
    12: (
        "docs/curriculum/portal/DAY_12_PORTAL.md",
        "docs/DAY_12_PRIVATE_NETWORKING.md",
    ),
    13: (
        "docs/curriculum/portal/DAY_13_PORTAL.md",
        "docs/DAY_13_INTEGRATION_AND_MCP.md",
    ),
    14: (
        "docs/curriculum/portal/DAY_14_PORTAL.md",
        "docs/DAY_14_BREAKING_CHANGES.md",
    ),
}

CORE_TEMPLATE_REQUIREMENTS = (
    "docs/curriculum/artifacts/day02/ADR_001_SCOPE_AND_BOUNDARIES.md",
    "docs/curriculum/artifacts/day02/RACI_MATRIX.md",
    "docs/curriculum/artifacts/day08/SECURITY_REVIEW_PACKET.md",
    "docs/curriculum/artifacts/day08/RELEASE_OWNERSHIP_MAP.md",
    "docs/curriculum/artifacts/day10/EXECUTIVE_RELEASE_BRIEF.md",
    "docs/curriculum/artifacts/day11/OBO_THREAT_MODEL.md",
)

THREE_SURFACE_PORTAL_DOCS = (
    "docs/curriculum/portal/DAY_00_PORTAL.md",
)

THREE_SURFACE_NOTEBOOKS = (
    "notebooks/day_1_agentic_fundamentals.py",
    "notebooks/day_3_azure_ai_services.py",
    "notebooks/day_8_cicd_iac_deployment.py",
    "notebooks/day_10_production_operations.py",
    "notebooks/day_11_delegated_identity_obo.py",
    "notebooks/day_12_private_networking_constraints.py",
    "notebooks/day_13_integration_boundary_and_mcp.py",
    "notebooks/day_14_breaking_changes_elite_ops.py",
)


def main() -> int:
    errors: list[str] = []

    manifest = _load_manifest(errors)

    for rel_path in REQUIRED_DOCS:
        path = ROOT / rel_path
        if not path.exists():
            errors.append(f"Missing required curriculum file: {rel_path}")

    trainee_docs = sorted((ROOT / "docs" / "curriculum" / "trainee").glob("*.md"))
    trainer_docs = sorted((ROOT / "docs" / "curriculum" / "trainer").glob("*.md"))
    portal_docs = sorted((ROOT / "docs" / "curriculum" / "portal").glob("DAY_*_PORTAL.md"))
    expected_trainee_docs = ["DAY_00_TRAINEE.md"]
    actual_trainee_docs = [path.name for path in trainee_docs]
    if actual_trainee_docs != expected_trainee_docs:
        errors.append(
            "Expected only the Day 0 trainee bootstrap doc in docs/curriculum/trainee/."
        )
    expected_trainer_docs = ["DAY_00_TRAINER.md"]
    actual_trainer_docs = [path.name for path in trainer_docs]
    if actual_trainer_docs != expected_trainer_docs:
        errors.append(
            "Expected only the Day 0 trainer bootstrap doc in docs/curriculum/trainer/."
        )
    expected_portal_docs = ["DAY_00_PORTAL.md"]
    actual_portal_docs = [path.name for path in portal_docs]
    if actual_portal_docs != expected_portal_docs:
        errors.append(
            "Expected only the Day 0 portal bootstrap guide in docs/curriculum/portal/."
        )

    for path in trainee_docs:
        _expect_headings(
            errors,
            path,
            TRAINEE_REQUIRED_HEADINGS,
            "Trainee day doc is missing required assessment section",
        )
    for path in trainer_docs:
        _expect_headings(
            errors,
            path,
            TRAINER_REQUIRED_HEADINGS,
            "Trainer day doc is missing required facilitation section",
        )
    for path in portal_docs:
        _expect_headings(
            errors,
            path,
            PORTAL_REQUIRED_HEADINGS,
            "Portal day doc is missing the required portal-first structure",
        )
    for rel_path in THREE_SURFACE_PORTAL_DOCS:
        _expect_headings(
            errors,
            ROOT / rel_path,
            ("## Three-Surface Linkage",),
            "Critical portal guide is missing the explicit portal-notebook-automation linkage",
        )
    _expect_headings(
        errors,
        ROOT / "docs" / "DAY_00_AZURE_BOOTSTRAP.md",
        ("## Three-Surface Linkage",),
        "Day 0 bootstrap doc is missing the explicit portal-to-automation linkage",
    )
    _expect_snippets(
        errors,
        ROOT / "docs" / "curriculum" / "README.md",
        README_REQUIRED_SNIPPETS,
        "Curriculum README is missing launch-readiness or checkpoint guidance",
    )
    _expect_snippets(
        errors,
        ROOT / "docs" / "curriculum" / "TRAINER_OPERATIONS.md",
        TRAINER_OPS_REQUIRED_SNIPPETS,
        "Trainer operations guide is missing launch-readiness guidance",
    )
    _expect_snippets(
        errors,
        ROOT / "docs" / "curriculum" / "TRAINEE_PREFLIGHT_CHECKLIST.md",
        PREFLIGHT_REQUIRED_SNIPPETS,
        "Trainee preflight checklist is missing required readiness commands",
    )
    _expect_snippets(
        errors,
        ROOT / "docs" / "curriculum" / "FACILITATOR_DAY_START_CHECKLIST.md",
        FACILITATOR_REQUIRED_SNIPPETS,
        "Facilitator day-start checklist is missing required delivery controls",
    )

    if manifest is not None:
        _validate_manifest(errors, manifest)

    for rel_path in STRICT_VALIDATION_DOCS:
        path = ROOT / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"(?<!AEGISAP_)POSTGRES_DSN\b", text):
            errors.append(
                f"{path.relative_to(ROOT)} uses non-canonical PostgreSQL env var `POSTGRES_DSN`."
            )
        errors.extend(_validate_path_tokens(path, text))
        errors.extend(_validate_module_commands(path, text))

    for template_rel in CORE_TEMPLATE_REQUIREMENTS:
        template_path = ROOT / template_rel
        if not template_path.exists():
            errors.append(f"Missing core artifact template: {template_rel}")
            continue
        _expect_any_snippet(
            errors,
            template_path,
            ("Structural Example", "Anti-Pattern", "Anti-Patterns"),
            "Core artifact template is missing exemplar or anti-pattern guidance",
        )

    if errors:
        print("Curriculum validation failed:\n")
        for error in sorted(set(errors)):
            print(f"- {error}")
        return 1

    print("Curriculum validation passed.")
    return 0


def _load_manifest(errors: list[str]) -> dict | None:
    if not MANIFEST_PATH.exists():
        errors.append(f"Missing required curriculum file: {MANIFEST_PATH.relative_to(ROOT)}")
        return None
    if yaml is None:
        errors.append("PyYAML is required to validate CURRICULUM_MANIFEST.yaml.")
        return None
    try:
        payload = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # pragma: no cover - depends on malformed yaml
        errors.append(f"Could not parse {MANIFEST_PATH.relative_to(ROOT)}: {exc}")
        return None
    return payload


def _validate_manifest(errors: list[str], manifest: dict) -> None:
    days = manifest.get("days", [])
    if len(days) != 14:
        errors.append("Curriculum manifest should declare exactly 14 days.")
        return

    expected_ids = [f"{i:02d}" for i in range(1, 15)]
    ids = [str(day.get("id", "")) for day in days]
    if ids != expected_ids:
        errors.append(
            f"Curriculum manifest day ids should be {expected_ids}, found {ids}"
        )

    for day in days:
        day_id = int(day["id"])
        notebook_rel = day.get("notebook_file", "")
        notebook_path = ROOT / notebook_rel
        if not notebook_rel or not notebook_path.exists():
            errors.append(f"Manifest day {day['id']} notebook missing: {notebook_rel}")
            continue

        rubric_weights = day.get("rubric_weights", {})
        if sum(int(v) for v in rubric_weights.values()) != 100:
            errors.append(
                f"Manifest day {day['id']} rubric weights must sum to 100."
            )

        prompts = day.get("oral_defense_prompts", [])
        if len(prompts) != 3:
            errors.append(
                f"Manifest day {day['id']} must declare exactly 3 oral defense prompts."
            )

        artifact_files = day.get("artifact_files", [])
        if not artifact_files:
            errors.append(f"Manifest day {day['id']} must declare artifact files.")
        for artifact_rel in artifact_files:
            artifact_path = ROOT / artifact_rel
            if not artifact_path.exists():
                errors.append(
                    f"Manifest day {day['id']} artifact missing: {artifact_rel}"
                )

        if day_id in INCIDENT_NOTEBOOKS:
            _expect_snippets(
                errors,
                notebook_path,
                INCIDENT_NOTEBOOK_SECTIONS,
                f"Day {day_id} notebook is missing the incident-driven six-section scaffold",
            )
            _expect_snippets(
                errors,
                notebook_path,
                ("markdown-only", "Do not edit repo files from this notebook"),
                f"Day {day_id} notebook is missing the markdown-only production patch boundary",
            )
            _expect_absent_snippets(
                errors,
                notebook_path,
                INCIDENT_RETIRED_REFERENCES[day_id],
                f"Day {day_id} notebook still references retired learner-entry docs",
            )
            _validate_notebook_boundaries(errors, notebook_path)

        if not day.get("phase"):
            errors.append(f"Manifest day {day['id']} must declare a phase.")
        if not day.get("injection_command"):
            errors.append(f"Manifest day {day['id']} must declare an injection_command.")
        if not day.get("revert_state"):
            errors.append(f"Manifest day {day['id']} must declare a revert_state path.")
        if "verification_commands" not in day:
            errors.append(f"Manifest day {day['id']} must declare verification_commands.")
        if "review_contract" not in day:
            errors.append(f"Manifest day {day['id']} must declare review_contract.")
        if day.get("legacy_doc_files"):
            errors.append(
                f"Manifest day {day['id']} should not declare legacy_doc_files after the incident-driven redesign."
            )

        scenario_rel = day.get("scenario_dir", "")
        if day["id"] in {f"{i:02d}" for i in range(1, 15)} and not scenario_rel:
            errors.append(f"Manifest day {day['id']} must declare a scenario_dir during incident-delivery waves.")
        if scenario_rel:
            scenario_path = ROOT / scenario_rel / "scenario.yaml"
            if not scenario_path.exists():
                errors.append(f"Manifest day {day['id']} scenario file missing: {scenario_path.relative_to(ROOT)}")
            else:
                _validate_scenario_file(errors, scenario_path)


def _expect_headings(
    errors: list[str],
    path: Path,
    headings: tuple[str, ...],
    message: str,
) -> None:
    if not path.exists():
        errors.append(f"Missing required curriculum file: {path.relative_to(ROOT)}")
        return
    text = path.read_text(encoding="utf-8")
    for heading in headings:
        if heading not in text:
            errors.append(f"{message}: {path.relative_to(ROOT)} is missing `{heading}`")


def _expect_snippets(
    errors: list[str],
    path: Path,
    snippets: tuple[str, ...],
    message: str,
) -> None:
    if not path.exists():
        errors.append(f"Missing required curriculum file: {path.relative_to(ROOT)}")
        return
    text = path.read_text(encoding="utf-8")
    for snippet in snippets:
        if snippet not in text:
            errors.append(f"{message}: {path.relative_to(ROOT)} is missing `{snippet}`")


def _expect_any_snippet(
    errors: list[str],
    path: Path,
    snippets: tuple[str, ...],
    message: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if not any(snippet in text for snippet in snippets):
        joined = " or ".join(f"`{snippet}`" for snippet in snippets)
        errors.append(f"{message}: {path.relative_to(ROOT)} is missing one of {joined}")


def _expect_absent_snippets(
    errors: list[str],
    path: Path,
    snippets: tuple[str, ...],
    message: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    for snippet in snippets:
        if snippet in text:
            errors.append(f"{message}: {path.relative_to(ROOT)} still contains `{snippet}`")


def _validate_scenario_file(errors: list[str], path: Path) -> None:
    if yaml is None:
        return
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    scenario_root = path.parent
    required_top_level = {
        "setup",
        "validation",
        "teardown",
        "review",
        "baseline_track",
        "baseline_reprovision_command",
    }
    missing_top_level = sorted(required_top_level - set(payload))
    if missing_top_level:
        errors.append(
            f"{path.relative_to(ROOT)} is missing top-level scenario keys: {', '.join(missing_top_level)}"
        )
        return
    for key in ("apply_diff", "azure_script", "customer_drop"):
        if key not in payload["setup"]:
            errors.append(f"{path.relative_to(ROOT)} is missing setup.{key}")
    apply_diff = payload["setup"].get("apply_diff")
    if apply_diff:
        apply_diff_path = scenario_root / apply_diff
        if not apply_diff_path.exists():
            errors.append(f"{path.relative_to(ROOT)} references missing setup.apply_diff `{apply_diff}`")
        else:
            _validate_scenario_patch(errors, apply_diff_path)
    customer_drop = payload["setup"].get("customer_drop")
    if customer_drop and not (scenario_root / customer_drop).exists():
        errors.append(
            f"{path.relative_to(ROOT)} references missing setup.customer_drop `{customer_drop}`"
        )
    for key in ("reproduce_command", "ci_command"):
        if key not in payload["validation"]:
            errors.append(f"{path.relative_to(ROOT)} is missing validation.{key}")
    for key in ("revert_diff", "azure_script", "cleanup"):
        if key not in payload["teardown"]:
            errors.append(f"{path.relative_to(ROOT)} is missing teardown.{key}")
    revert_diff = payload["teardown"].get("revert_diff")
    if revert_diff:
        revert_diff_path = scenario_root / revert_diff
        if not revert_diff_path.exists():
            errors.append(f"{path.relative_to(ROOT)} references missing teardown.revert_diff `{revert_diff}`")
        elif revert_diff != apply_diff:
            _validate_scenario_patch(errors, revert_diff_path)
    for key in ("evaluator_profile", "human_required"):
        if key not in payload["review"]:
            errors.append(f"{path.relative_to(ROOT)} is missing review.{key}")


def _validate_scenario_patch(errors: list[str], patch_path: Path) -> None:
    if patch_path.suffix != ".patch":
        return
    patch_text = patch_path.read_text(encoding="utf-8")
    for sentinel in (
        "*** Begin Patch",
        "*** End Patch",
        "*** Add File:",
        "*** Update File:",
        "*** Delete File:",
    ):
        if sentinel in patch_text:
            errors.append(
                f"Scenario patch contains apply_patch sentinel text: {patch_path.relative_to(ROOT)} includes `{sentinel}`"
            )
    result = subprocess.run(
        ["git", "apply", "--check", "--cached", str(patch_path.relative_to(ROOT))],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip().splitlines()
        suffix = f": {detail[0]}" if detail else ""
        errors.append(f"Scenario patch does not apply cleanly: {patch_path.relative_to(ROOT)}{suffix}")


def _validate_notebook_boundaries(errors: list[str], path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    forbidden_literals = (
        "apply_patch(",
        "git apply",
        "git checkout",
    )
    for literal in forbidden_literals:
        if literal in text:
            errors.append(f"{path.relative_to(ROOT)} contains forbidden notebook mutation literal `{literal}`")

    forbidden_write_targets = (
        "src/",
        "infra/",
        "tests/",
    )
    for target in forbidden_write_targets:
        if f"write_text(" in text and target in text:
            errors.append(
                f"{path.relative_to(ROOT)} appears to write into repo-tracked path `{target}` from a notebook cell"
            )


def _validate_path_tokens(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    for token in re.findall(r"`([^`]+)`", text):
        candidate = token.strip().split()[0]
        if not candidate.startswith(PATH_PREFIXES):
            continue
        file_path = ROOT / candidate
        if not file_path.exists():
            errors.append(
                f"{path.relative_to(ROOT)} references missing path `{candidate}`"
            )
    return errors


def _validate_module_commands(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    modules = re.findall(r"(?:uv run )?python -m ([A-Za-z0-9_\.]+)", text)
    for module_name in modules:
        if importlib.util.find_spec(module_name) is None:
            errors.append(
                f"{path.relative_to(ROOT)} references missing Python module `{module_name}`"
            )
    return errors


if __name__ == "__main__":
    raise SystemExit(main())
