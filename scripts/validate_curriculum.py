#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "notebooks"))

DAY_METADATA = {
    0: {
        "notebook": "notebooks/day0_azure_bootstrap.py",
        "trainee": "docs/curriculum/trainee/DAY_00_TRAINEE.md",
        "trainer": "docs/curriculum/trainer/DAY_00_TRAINER.md",
        "artifact": "build/day0/env_report.json",
        "prereq": None,
    },
    1: {
        "notebook": "notebooks/day1_intake_canonicalization.py",
        "trainee": "docs/curriculum/trainee/DAY_01_TRAINEE.md",
        "trainer": "docs/curriculum/trainer/DAY_01_TRAINER.md",
        "artifact": "build/day1/golden_thread_day1.json",
        "prereq": "build/day0/env_report.json",
    },
    2: {
        "notebook": "notebooks/day2_stateful_workflow.py",
        "trainee": "docs/curriculum/trainee/DAY_02_TRAINEE.md",
        "trainer": "docs/curriculum/trainer/DAY_02_TRAINER.md",
        "artifact": "build/day2/golden_thread_day2.json",
        "prereq": "build/day1/golden_thread_day1.json",
    },
    3: {
        "notebook": "notebooks/day3_retrieval_authority.py",
        "trainee": "docs/curriculum/trainee/DAY_03_TRAINEE.md",
        "trainer": "docs/curriculum/trainer/DAY_03_TRAINER.md",
        "artifact": "build/day3/golden_thread_day3.json",
        "prereq": "build/day2/golden_thread_day2.json",
    },
    4: {
        "notebook": "notebooks/day4_explicit_planning.py",
        "trainee": "docs/curriculum/trainee/DAY_04_TRAINEE.md",
        "trainer": "docs/curriculum/trainer/DAY_04_TRAINER.md",
        "artifact": "build/day4/golden_thread_day4.json",
        "prereq": "build/day3/golden_thread_day3.json",
    },
    5: {
        "notebook": "notebooks/day5_durable_state.py",
        "trainee": "docs/curriculum/trainee/DAY_05_TRAINEE.md",
        "trainer": "docs/curriculum/trainer/DAY_05_TRAINER.md",
        "artifact": "build/day5/golden_thread_day5_resumed.json",
        "prereq": "build/day4/golden_thread_day4.json",
    },
    6: {
        "notebook": "notebooks/day6_policy_review.py",
        "trainee": "docs/curriculum/trainee/DAY_06_TRAINEE.md",
        "trainer": "docs/curriculum/trainer/DAY_06_TRAINER.md",
        "artifact": "build/day6/golden_thread_day6.json",
        "prereq": "build/day5/golden_thread_day5_resumed.json",
    },
    7: {
        "notebook": "notebooks/day7_security_identity.py",
        "trainee": "docs/curriculum/trainee/DAY_07_TRAINEE.md",
        "trainer": "docs/curriculum/trainer/DAY_07_TRAINER.md",
        "artifact": "build/day7/security_posture.json",
        "prereq": "build/day6/golden_thread_day6.json",
    },
    8: {
        "notebook": "notebooks/day8_observability.py",
        "trainee": "docs/curriculum/trainee/DAY_08_TRAINEE.md",
        "trainer": "docs/curriculum/trainer/DAY_08_TRAINER.md",
        "artifact": "build/day8/regression_baseline.json",
        "prereq": "build/day7/security_posture.json",
    },
    9: {
        "notebook": "notebooks/day9_cost_routing.py",
        "trainee": "docs/curriculum/trainee/DAY_09_TRAINEE.md",
        "trainer": "docs/curriculum/trainer/DAY_09_TRAINER.md",
        "artifact": "build/day9/routing_report.json",
        "prereq": "build/day8/regression_baseline.json",
    },
    10: {
        "notebook": "notebooks/day10_deployment_gates.py",
        "trainee": "docs/curriculum/trainee/DAY_10_TRAINEE.md",
        "trainer": "docs/curriculum/trainer/DAY_10_TRAINER.md",
        "artifact": "build/day10/release_envelope.json",
        "prereq": "build/day9/routing_report.json",
    },
}

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

README_REQUIRED_SNIPPETS = (
    "## Mandatory Checkpoints",
    "build/day4/checkpoint_policy_overlay.json",
    "build/day8/checkpoint_trace_extension.json",
    "build/day10/checkpoint_gate_extension.json",
    "## Capstone Review Flow",
    "build/capstone/<trainee_id>/release_packet.json",
    "TRAINER_OPERATIONS.md",
    "CAPSTONE_PR_REVIEW.md",
    "INCIDENT_DRILL_RUNBOOK.md",
    "PILOT_MEASUREMENT_PLAN.md",
    "GRADUATE_PROFILE.md",
)

CAPSTONE_REQUIRED_SNIPPETS = (
    "13/16",
    "build/capstone/<trainee_id>/release_packet.json",
    "release-style defense",
    "scripts/build_capstone_release_packet.py",
    "CAPSTONE_PR_REVIEW.md",
    "chosen assumption",
    "rejected alternative",
    "review-response quality",
)


def main() -> int:
    errors: list[str] = []

    curriculum_files = [
        ROOT / "docs" / "curriculum" / "README.md",
        ROOT / "docs" / "curriculum" / "CAPSTONE_REVIEW.md",
        ROOT / "docs" / "curriculum" / "CAPSTONE_PR_REVIEW.md",
        ROOT / "docs" / "curriculum" / "TRAINER_OPERATIONS.md",
        ROOT / "docs" / "curriculum" / "INCIDENT_DRILL_RUNBOOK.md",
        ROOT / "docs" / "curriculum" / "PILOT_MEASUREMENT_PLAN.md",
        ROOT / "docs" / "curriculum" / "GRADUATE_PROFILE.md",
        ROOT / "docs" / "curriculum" / "templates" / "DAILY_SCORECARD.md",
        ROOT / "docs" / "curriculum" / "templates" / "PILOT_RETRO.md",
    ]
    curriculum_files.extend(sorted((ROOT / "docs" / "curriculum" / "trainee").glob("*.md")))
    curriculum_files.extend(sorted((ROOT / "docs" / "curriculum" / "trainer").glob("*.md")))

    for day, meta in DAY_METADATA.items():
        notebook_path = ROOT / meta["notebook"]
        trainee_path = ROOT / meta["trainee"]
        trainer_path = ROOT / meta["trainer"]
        for path in [notebook_path, trainee_path, trainer_path]:
            if not path.exists():
                errors.append(f"Missing required curriculum file: {path.relative_to(ROOT)}")
        if trainee_path.exists():
            _expect_contains(
                errors,
                trainee_path,
                f"`{meta['notebook']}`",
                f"Day {day} trainee file should reference the correct notebook",
            )
            _expect_headings(
                errors,
                trainee_path,
                TRAINEE_REQUIRED_HEADINGS,
                f"Day {day} trainee file is missing required assessment section",
            )
        if trainer_path.exists():
            _expect_contains(
                errors,
                trainer_path,
                meta["artifact"],
                f"Day {day} trainer file should name its expected artifact",
            )
            _expect_headings(
                errors,
                trainer_path,
                TRAINER_REQUIRED_HEADINGS,
                f"Day {day} trainer file is missing required facilitation section",
            )
        if notebook_path.exists():
            _expect_contains(
                errors,
                notebook_path,
                meta["artifact"],
                f"Day {day} notebook should reference its output artifact",
            )
            if meta["prereq"] is not None:
                _expect_contains(
                    errors,
                    notebook_path,
                    meta["prereq"],
                    f"Day {day} notebook should reference its upstream artifact prerequisite",
                )
            _expect_contains(
                errors,
                notebook_path,
                "implementation_exercise=",
                f"Day {day} notebook should declare an implementation exercise",
            )

    _expect_snippets(
        errors,
        ROOT / "docs" / "curriculum" / "README.md",
        README_REQUIRED_SNIPPETS,
        "Curriculum README is missing required checkpoint or capstone contract",
    )
    _expect_snippets(
        errors,
        ROOT / "docs" / "curriculum" / "CAPSTONE_REVIEW.md",
        CAPSTONE_REQUIRED_SNIPPETS,
        "Capstone guide is missing required scoring or packet contract",
    )
    _expect_snippets(
        errors,
        ROOT / "docs" / "curriculum" / "CAPSTONE_PR_REVIEW.md",
        (
            "build/capstone/<trainee_id>/release_packet.json",
            "review_response_quality",
            "substantive finding",
        ),
        "Capstone PR review guide is missing required review contract",
    )
    for trainer_day in (8, 9, 10):
        trainer_path = ROOT / DAY_METADATA[trainer_day]["trainer"]
        _expect_snippets(
            errors,
            trainer_path,
            ("INCIDENT_DRILL_RUNBOOK.md",),
            f"Day {trainer_day} trainer file is missing incident drill guidance",
        )

    for path in curriculum_files:
        if not path.exists():
            errors.append(f"Missing required curriculum file: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"(?<!AEGISAP_)POSTGRES_DSN\b", text):
            errors.append(
                f"{path.relative_to(ROOT)} uses non-canonical PostgreSQL env var `POSTGRES_DSN`."
            )
        errors.extend(_validate_path_tokens(path, text))
        errors.extend(_validate_module_commands(path, text))

    if errors:
        print("Curriculum validation failed:\n")
        for error in sorted(set(errors)):
            print(f"- {error}")
        return 1

    print("Curriculum validation passed.")
    return 0


def _expect_contains(errors: list[str], path: Path, needle: str, message: str) -> None:
    text = path.read_text(encoding="utf-8")
    if needle not in text:
        errors.append(f"{message}: {path.relative_to(ROOT)} is missing `{needle}`")


def _expect_headings(
    errors: list[str],
    path: Path,
    headings: tuple[str, ...],
    message: str,
) -> None:
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
    text = path.read_text(encoding="utf-8")
    for snippet in snippets:
        if snippet not in text:
            errors.append(f"{message}: {path.relative_to(ROOT)} is missing `{snippet}`")


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
