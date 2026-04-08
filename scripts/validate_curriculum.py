#!/usr/bin/env python3
from __future__ import annotations

import json
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

try:
    import yaml
except ImportError:  # pragma: no cover - depends on local env
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "docs" / "curriculum" / "CURRICULUM_MANIFEST.yaml"

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "notebooks"))

from aegisap.lab.curriculum import PHASE1_GATE_MODES, module_readme_relpath

PATH_PREFIXES = (
    "docs/",
    "modules/",
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
    "docs/curriculum/FDE_DEBUGGING_FRAMEWORK.md",
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
    "docs/curriculum/curriculum.schema.json",
    "docs/curriculum/templates/DAILY_ARTIFACT_PACK.md",
    "docs/curriculum/templates/DAILY_SCORECARD.md",
    "docs/curriculum/templates/NATIVE_OPERATOR_EVIDENCE_TEMPLATE.json",
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
    "FDE_DEBUGGING_FRAMEWORK.md",
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
    "FDE_DEBUGGING_FRAMEWORK.md",
    "Daily Operating Rhythm",
    "Learner Status Model",
    "trainer may not touch the learner's keyboard",
    "expected topology",
    "## Naked Drill Protocol",
    "helper CLI commands",
)

PREFLIGHT_REQUIRED_SNIPPETS = (
    "uv sync --extra dev --extra day9",
    "az login",
    "scripts/verify_env.py",
    "scripts/setup-env.sh",
    "This is not a tutorial",
    "Native Azure and Git fluency is assessed by Week 2",
)

FACILITATOR_REQUIRED_SNIPPETS = (
    "uv run python scripts/validate_curriculum.py",
    "CURRICULUM_MANIFEST.yaml",
    "FDE_DEBUGGING_FRAMEWORK.md",
    "docs/curriculum/portal/DAY_00_PORTAL.md",
    "uv run aegisap-lab incident start --day",
    "audit-production",
    "aegisap-lab mastery --day",
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
    "## Why This Fails In Prod",
    "## Codification Bridge",
    "## Production Patch",
    "## Verification",
    "## Chaos Gate",
    "## Map the Gap",
    "## PR Defense",
)

MODULE_REQUIRED_HEADINGS = (
    "## Why This Matters to an FDE",
    "## Customer Context",
    "## Persistent Constraints",
    "## FDE Implementation Cycle",
    "## Mastery Gate",
    "## Chaos Gate",
    "## Day X File Manifest",
)

WHY_FAILS_PROMPT = (
    "List three specific ways this notebook logic fails in an Azure Container App. "
    "You must reference at least one Azure limit (memory, timeout, or ephemeral storage) "
    "and one concurrency issue."
)

NATIVE_OPERATOR_EVIDENCE_DAYS = {
    "09": {
        "mode": "advisory",
        "review_stage": "day10_cab_board",
        "minimum_commands": 1,
        "minimum_queries": 1,
        "live_demo_required": False,
    },
    "12": {
        "mode": "blocking",
        "review_stage": "day12_closeout",
        "minimum_commands": 2,
        "minimum_queries": 0,
        "live_demo_required": True,
    },
    "14": {
        "mode": "blocking",
        "review_stage": "capstone_cab_board",
        "minimum_commands": 2,
        "minimum_queries": 1,
        "live_demo_required": True,
    },
}

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

BRIDGE_README = "notebooks/bridges/README.md"


def main() -> int:
    errors: list[str] = []

    manifest = _load_manifest(errors)

    for rel_path in REQUIRED_DOCS:
        path = ROOT / rel_path
        if not path.exists():
            errors.append(f"Missing required curriculum file: {rel_path}")
    if not (ROOT / BRIDGE_README).exists():
        errors.append(f"Missing required curriculum file: {BRIDGE_README}")

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
    _expect_snippets(
        errors,
        ROOT / "docs" / "curriculum" / "CAPSTONE_PR_REVIEW.md",
        (
            "peer_reviewer_challenge_quality",
            "skeptical questions",
            "concrete evidence artifact",
            "rerun the selected native proof live",
        ),
        "Capstone PR review guide is missing the adversarial CAB contract",
    )
    _expect_snippets(
        errors,
        ROOT / "docs" / "curriculum" / "CAPSTONE_REVIEW.md",
        (
            "cab_board",
            "peer_reviewer_challenge_quality",
            "rerun the selected native proof live",
        ),
        "Capstone review guide is missing the live CAB review contract",
    )
    _expect_snippets(
        errors,
        ROOT / "docs" / "curriculum" / "ASSESSOR_CALIBRATION.md",
        (
            "peer_reviewer_challenge_quality",
            "Rubber-stamping",
            "Top Talent",
        ),
        "Assessor calibration guide is missing reviewer-accountability language",
    )
    _expect_snippets(
        errors,
        ROOT / "docs" / "curriculum" / "GRADUATION_RUBRIC.md",
        (
            "peer_reviewer_challenge_quality",
            "Top Talent",
            "remediation",
        ),
        "Graduation rubric is missing reviewer-accountability criteria",
    )

    if manifest is not None:
        _validate_manifest_schema(errors, manifest)
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


def _load_schema(errors: list[str]) -> dict | None:
    schema_path = ROOT / "docs" / "curriculum" / "curriculum.schema.json"
    if not schema_path.exists():
        errors.append(f"Missing required curriculum file: {schema_path.relative_to(ROOT)}")
        return None
    try:
        return json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"Could not parse {schema_path.relative_to(ROOT)}: {exc}")
        return None


def _validate_manifest_schema(errors: list[str], manifest: dict) -> None:
    schema = _load_schema(errors)
    if schema is None:
        return
    validator = Draft202012Validator(schema)
    for issue in sorted(validator.iter_errors(manifest), key=lambda err: list(err.path)):
        path = ".".join(str(part) for part in issue.path) or "<root>"
        errors.append(f"Manifest schema violation at {path}: {issue.message}")


def _validate_manifest(errors: list[str], manifest: dict) -> None:
    days = manifest.get("days", [])
    if len(days) != 14:
        errors.append("Curriculum manifest should declare exactly 14 days.")
        return

    customer_profile = manifest.get("customer_profile", {})
    if not customer_profile:
        errors.append("Curriculum manifest must declare customer_profile.")

    expected_ids = [f"{i:02d}" for i in range(1, 15)]
    ids = [str(day.get("id", "")) for day in days]
    if ids != expected_ids:
        errors.append(
            f"Curriculum manifest day ids should be {expected_ids}, found {ids}"
        )

    previous_active_constraints: dict[str, dict] = {}

    for day in days:
        day_id = int(day["id"])
        day_id_str = day["id"]
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

        if not day.get("customer_context"):
            errors.append(f"Manifest day {day['id']} must declare customer_context.")
        drills = day.get("automation_drills", [])
        if not drills:
            errors.append(f"Manifest day {day['id']} must declare automation_drills.")
        else:
            defaults = [drill["id"] for drill in drills if drill.get("default")]
            if len(defaults) != 1:
                errors.append(
                    f"Manifest day {day['id']} must declare exactly one default automation drill."
                )
            for drill in drills:
                if drill.get("mode") == "artifact":
                    if not drill.get("source_file"):
                        errors.append(
                            f"Manifest day {day['id']} artifact drill `{drill['id']}` must declare source_file."
                        )
                    elif not (ROOT / drill["source_file"]).exists():
                        errors.append(
                            f"Manifest day {day['id']} drill source missing: {drill['source_file']}"
                        )
                    if not drill.get("mutation"):
                        errors.append(
                            f"Manifest day {day['id']} artifact drill `{drill['id']}` must declare mutation."
                        )
                    for repair_target in drill.get("repair_targets", []):
                        if not (ROOT / repair_target).exists():
                            errors.append(
                                f"Manifest day {day['id']} drill `{drill['id']}` repair target missing: {repair_target}"
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
                f"Day {day_id} notebook is missing the incident-driven translation scaffold",
            )
            _expect_snippets(
                errors,
                notebook_path,
                (
                    "markdown-only",
                    "Do not edit repo files from this notebook",
                    "## Why This Fails In Prod",
                    WHY_FAILS_PROMPT,
                    "### Export to Production",
                    "STOP. Close this notebook.",
                    "cohort/<",
                    "What trade-off did I make today to satisfy the customer constraint?",
                    "What is the blast radius if my code fails?",
                    "How will I know it failed in production?",
                ),
                f"Day {day_id} notebook is missing the markdown-only production patch boundary",
            )
            if day_id_str in NATIVE_OPERATOR_EVIDENCE_DAYS:
                _expect_snippets(
                    errors,
                    notebook_path,
                    ("## Native Tooling Gate", "native_operator_evidence.json"),
                    f"Day {day_id} notebook is missing the native-tooling evidence gate",
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
        mapping = day.get("portal_to_script_mapping", {})
        if not mapping:
            errors.append(f"Manifest day {day['id']} must declare portal_to_script_mapping.")
        else:
            if not mapping.get("portal_surface"):
                errors.append(f"Manifest day {day['id']} portal_to_script_mapping must declare portal_surface.")
            bridge_rel = mapping.get("bridge_file", "")
            if not bridge_rel:
                errors.append(f"Manifest day {day['id']} portal_to_script_mapping must declare bridge_file.")
            elif not (ROOT / bridge_rel).exists():
                errors.append(
                    f"Manifest day {day['id']} portal_to_script_mapping bridge missing: {bridge_rel}"
                )
            targets = mapping.get("production_targets", [])
            if not targets:
                errors.append(f"Manifest day {day['id']} portal_to_script_mapping must declare production_targets.")
            else:
                for target in targets:
                    if not (ROOT / target).exists():
                        errors.append(
                            f"Manifest day {day['id']} portal_to_script_mapping target missing: {target}"
                        )
        constraints = day.get("persistent_constraints", [])
        if not constraints:
            errors.append(f"Manifest day {day['id']} must declare persistent_constraints.")
        listed_constraints = {constraint["id"]: constraint for constraint in constraints}
        active_constraints = {
            constraint_id: constraint
            for constraint_id, constraint in listed_constraints.items()
            if not constraint.get("superseded_by")
        }
        for constraint in constraints:
            if constraint.get("superseded_by") and (
                not constraint.get("supersession_reason") or not constraint.get("approver_role")
            ):
                errors.append(
                    f"Manifest day {day['id']} superseded constraint `{constraint['id']}` must declare supersession_reason and approver_role."
                )
        for constraint_id, prior_constraint in previous_active_constraints.items():
            if constraint_id in active_constraints:
                continue
            current_version = listed_constraints.get(constraint_id)
            if current_version and current_version.get("superseded_by"):
                continue
            errors.append(
                f"Manifest day {day['id']} drops persistent constraint `{constraint_id}` introduced on day {prior_constraint['introduced_on']} without explicit supersession."
            )
        previous_active_constraints = active_constraints

        mastery_gates = day.get("mastery_gates", [])
        if not mastery_gates:
            errors.append(f"Manifest day {day['id']} must declare mastery_gates.")
        expected_gate_mode = PHASE1_GATE_MODES.get(day_id_str)
        if expected_gate_mode:
            invalid_modes = [
                gate["id"]
                for gate in mastery_gates
                if gate.get("mode") != expected_gate_mode
            ]
            if invalid_modes:
                errors.append(
                    f"Manifest day {day['id']} mastery gates must all be `{expected_gate_mode}` in Phase 1: {', '.join(invalid_modes)}"
                )
        for gate in mastery_gates:
            gate_constraints = set(gate.get("covers_constraints", []))
            unknown_constraints = sorted(gate_constraints - set(listed_constraints))
            if unknown_constraints:
                errors.append(
                    f"Manifest day {day['id']} mastery gate `{gate['id']}` references unknown constraints: {', '.join(unknown_constraints)}"
                )
        infrastructure_constraints = [
            constraint
            for constraint in active_constraints.values()
            if constraint.get("type") == "infrastructure"
        ]
        for constraint in infrastructure_constraints:
            matching_gate = next(
                (
                    gate
                    for gate in mastery_gates
                    if constraint["id"] in gate.get("covers_constraints", [])
                    and gate.get("evidence_source") == "cloud_probe"
                    and f"uv run aegisap-lab audit-production --day {day_id_str} --strict" in gate.get("command", "")
                ),
                None,
            )
            if matching_gate is None:
                errors.append(
                    f"Manifest day {day['id']} infrastructure constraint `{constraint['id']}` must be covered by a cloud_probe mastery gate invoking `uv run aegisap-lab audit-production --day {day_id_str} --strict`."
                )
        chaos_gate = day.get("chaos_gate", {})
        if not chaos_gate:
            errors.append(f"Manifest day {day['id']} must declare chaos_gate.")
        if not day.get("injection_command"):
            errors.append(f"Manifest day {day['id']} must declare an injection_command.")
        if not day.get("revert_state"):
            errors.append(f"Manifest day {day['id']} must declare a revert_state path.")
        if "verification_commands" not in day:
            errors.append(f"Manifest day {day['id']} must declare verification_commands.")
        if "review_contract" not in day:
            errors.append(f"Manifest day {day['id']} must declare review_contract.")
        else:
            review_contract = day["review_contract"]
            if day_id_str == "10":
                if review_contract.get("review_mode") != "cab_board":
                    errors.append("Manifest day 10 review_contract must declare `review_mode: cab_board`.")
                if review_contract.get("required_review_roles") != ["cab_chair", "client_ciso_or_infra_lead"]:
                    errors.append(
                        "Manifest day 10 review_contract must declare CAB roles `cab_chair` and `client_ciso_or_infra_lead`."
                    )
            if day_id_str == "14":
                if review_contract.get("review_mode") != "cab_board":
                    errors.append("Manifest day 14 review_contract must declare `review_mode: cab_board`.")
                if review_contract.get("required_review_roles") != ["cab_chair", "client_ciso", "infra_lead"]:
                    errors.append(
                        "Manifest day 14 review_contract must declare CAB roles `cab_chair`, `client_ciso`, and `infra_lead`."
                    )
        stakeholder_inject = day.get("stakeholder_inject")
        if day_id_str == "04" and not stakeholder_inject:
            errors.append("Manifest day 04 must declare stakeholder_inject.")
        if stakeholder_inject:
            for artifact_rel in stakeholder_inject.get("required_artifacts", []):
                if not (ROOT / artifact_rel).exists():
                    errors.append(
                        f"Manifest day {day['id']} stakeholder inject artifact missing: {artifact_rel}"
                    )
        native_operator = day.get("native_operator_evidence")
        expected_native = NATIVE_OPERATOR_EVIDENCE_DAYS.get(day_id_str)
        if expected_native is None:
            if native_operator is not None:
                errors.append(
                    f"Manifest day {day['id']} should not declare native_operator_evidence."
                )
        else:
            if native_operator is None:
                errors.append(f"Manifest day {day['id']} must declare native_operator_evidence.")
            else:
                for key, expected_value in expected_native.items():
                    if native_operator.get(key) != expected_value:
                        errors.append(
                            f"Manifest day {day['id']} native_operator_evidence `{key}` must be `{expected_value}`."
                        )
                expected_artifact = f"build/day{int(day_id_str)}/native_operator_evidence.json"
                if native_operator.get("artifact_path") != expected_artifact:
                    errors.append(
                        f"Manifest day {day['id']} native_operator_evidence artifact_path must be `{expected_artifact}`."
                    )
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

        module_rel = module_readme_relpath(day_id_str)
        module_path = ROOT / module_rel
        if not module_path.exists():
            errors.append(f"Manifest day {day['id']} module README missing: {module_rel}")
        else:
            _expect_headings(
                errors,
                module_path,
                MODULE_REQUIRED_HEADINGS,
                "Module README is missing the learner-entry wormhole contract",
            )
            _expect_snippets(
                errors,
                module_path,
                ("Do not edit code in this module folder.", "## Day X File Manifest", "aegisap-lab drill inject --day"),
                "Module README is missing file-manifest or edit-boundary guidance",
            )
            if day_id_str in NATIVE_OPERATOR_EVIDENCE_DAYS:
                _expect_snippets(
                    errors,
                    module_path,
                    ("## Native Tooling Gate", "native_operator_evidence.json", "banned"),
                    "Module README is missing the native-tooling gate contract",
                )
            if day_id_str == "04":
                _expect_snippets(
                    errors,
                    module_path,
                    ("SPONSOR_PUSHBACK_EMAIL.md", "ADR-002_irreversible_actions_and_hitl.md"),
                    "Day 4 module README is missing the executive-pushback artifacts",
                )
            module_text = module_path.read_text(encoding="utf-8")
            errors.extend(_validate_path_tokens(module_path, module_text))
            errors.extend(_validate_module_commands(module_path, module_text))

        primary_doc_path = ROOT / day.get("primary_doc_file", "")
        if primary_doc_path.exists():
            _expect_headings(
                errors,
                primary_doc_path,
                ("## Why This Matters to an FDE", "## Customer Context"),
                "Primary day doc is missing the FDE business framing",
            )
            _expect_snippets(
                errors,
                primary_doc_path,
                (module_rel,),
                "Primary day doc must point the learner to the module README first",
            )
            if day_id_str in NATIVE_OPERATOR_EVIDENCE_DAYS:
                _expect_snippets(
                    errors,
                    primary_doc_path,
                    ("## Native Tooling Gate", "native_operator_evidence.json"),
                    "Primary day doc is missing the native-tooling gate contract",
                )
            if day_id_str == "04":
                _expect_snippets(
                    errors,
                    primary_doc_path,
                    ("SPONSOR_PUSHBACK_EMAIL.md", "ADR-002_irreversible_actions_and_hitl.md"),
                    "Day 4 primary doc is missing the executive-pushback artifacts",
                )
        if day_id_str == "07":
            matching_gate = next(
                (
                    gate
                    for gate in mastery_gates
                    if "evals/run_eval_suite.py" in gate.get("command", "")
                    and "build/day7/prompt_drift_report.json" in gate.get("command", "")
                    and "--enforce-thresholds" in gate.get("command", "")
                ),
                None,
            )
            if matching_gate is None:
                errors.append(
                    "Manifest day 07 must declare the enforced prompt-drift eval mastery gate."
                )
            default_drill = next((drill for drill in drills if drill.get("default")), None)
            if not default_drill or default_drill.get("id") != "drill_11_prompt_authority_drift":
                errors.append(
                    "Manifest day 07 must use `drill_11_prompt_authority_drift` as the default automation drill."
                )


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
