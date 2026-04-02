#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import re
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

REQUIRED_DOCS = (
    "docs/curriculum/README.md",
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
    "Day 8",
    "Day 11",
    "Day 12",
    "Day 13",
    "Day 14",
)

NOTEBOOK_SCAFFOLD_SNIPPETS = {
    "all": ("render_full_day_agenda(", "Summary Checklist"),
    2: (
        "Visual Guide — Architecture Lineage Map",
        "Mastery Checkpoint — Before You Leave Discovery",
        "render_unscaffolded_block(",
    ),
    8: (
        "Visual Guide — Deployment Evidence Lineage",
        "Mastery Checkpoint — Before You Trust The Pipeline",
        "render_unscaffolded_block(",
    ),
    10: ("Mastery Checkpoint — Before You Trust A Green Envelope",),
    11: (
        "Visual Guide — Identity Lineage Into OBO",
        "Mastery Checkpoint — Delegation Without Confusion",
        "render_unscaffolded_block(",
    ),
    12: ("Transfer Lens", "Mastery Checkpoint — Networking Discipline"),
    13: ("Transfer Lens", "Mastery Checkpoint — Boundary Ownership"),
    14: (
        "Transfer Lens",
        "Mastery Checkpoint — Elite Defense Readiness",
        "render_unscaffolded_block(",
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


def main() -> int:
    errors: list[str] = []

    manifest = _load_manifest(errors)

    for rel_path in REQUIRED_DOCS:
        path = ROOT / rel_path
        if not path.exists():
            errors.append(f"Missing required curriculum file: {rel_path}")

    trainee_docs = sorted((ROOT / "docs" / "curriculum" / "trainee").glob("*.md"))
    trainer_docs = sorted((ROOT / "docs" / "curriculum" / "trainer").glob("*.md"))
    if len(trainee_docs) < 11:
        errors.append("Expected trainee pre-read docs for Days 00-10.")
    if len(trainer_docs) < 11:
        errors.append("Expected trainer facilitation docs for Days 00-10.")

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

        _expect_snippets(
            errors,
            notebook_path,
            NOTEBOOK_SCAFFOLD_SNIPPETS["all"],
            f"Day {day_id} notebook is missing the standard full-day scaffold",
        )
        if day_id in NOTEBOOK_SCAFFOLD_SNIPPETS:
            _expect_snippets(
                errors,
                notebook_path,
                NOTEBOOK_SCAFFOLD_SNIPPETS[day_id],
                f"Day {day_id} notebook is missing anchor-day scaffold elements",
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
