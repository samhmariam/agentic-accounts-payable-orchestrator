#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import yaml

from aegisap.common.paths import repo_root


DEFAULT_DAYS = ("01", "02")


class ReplayError(RuntimeError):
    """Raised when nightly incident replay fails."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay incident scenarios in isolated git worktrees.")
    parser.add_argument(
        "--days",
        nargs="+",
        default=list(DEFAULT_DAYS),
        help="Day ids to replay.",
    )
    parser.add_argument(
        "--label",
        default="wave1",
        help="Label used in the summary artifact.",
    )
    parser.add_argument(
        "--out-json",
        default="build/replay/wave1_incident_replay.json",
        help="Path to the replay summary artifact.",
    )
    return parser.parse_args()


def run_shell(*, cwd: Path, command: str, expect_success: bool = True) -> dict[str, Any]:
    result = subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        text=True,
        capture_output=True,
        check=False,
    )
    payload = {
        "command": command,
        "cwd": str(cwd),
        "returncode": result.returncode,
        "stdout_tail": "\n".join(result.stdout.strip().splitlines()[-20:]),
        "stderr_tail": "\n".join(result.stderr.strip().splitlines()[-20:]),
    }
    if expect_success and result.returncode != 0:
        raise ReplayError(
            f"Command failed in {cwd}: {command}\n{payload['stderr_tail'] or payload['stdout_tail']}"
        )
    if not expect_success and result.returncode == 0:
        raise ReplayError(f"Command unexpectedly succeeded in {cwd}: {command}")
    return payload


def run_git(*, cwd: Path, args: list[str]) -> dict[str, Any]:
    command = ["git", *args]
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    payload = {
        "command": " ".join(shlex.quote(part) for part in command),
        "cwd": str(cwd),
        "returncode": result.returncode,
        "stdout_tail": "\n".join(result.stdout.strip().splitlines()[-20:]),
        "stderr_tail": "\n".join(result.stderr.strip().splitlines()[-20:]),
    }
    if result.returncode != 0:
        raise ReplayError(
            f"Git command failed in {cwd}: {payload['command']}\n{payload['stderr_tail'] or payload['stdout_tail']}"
        )
    return payload


def load_scenario(worktree: Path, day: str) -> dict[str, Any]:
    path = worktree / "scenarios" / f"day{day}" / "scenario.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def apply_reference_fix(*, worktree: Path, day: str, scenario: dict[str, Any]) -> dict[str, Any]:
    diff_rel = scenario["setup"]["apply_diff"]
    diff_path = worktree / "scenarios" / f"day{day}" / diff_rel
    return run_git(cwd=worktree, args=["apply", "--reverse", str(diff_path)])


def assert_clean_worktree(worktree: Path) -> None:
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=worktree,
        text=True,
        capture_output=True,
        check=False,
    )
    if status.returncode != 0:
        raise ReplayError(status.stderr.strip() or status.stdout.strip() or "git status failed")
    unexpected = [
        line for line in status.stdout.splitlines()
        if line.strip() and not line.strip().endswith(".aegisap-lab/") and ".aegisap-lab/" not in line
    ]
    if unexpected:
        raise ReplayError(f"Replay left a dirty worktree:\n{chr(10).join(unexpected)}")


def assert_no_customer_artifact(worktree: Path) -> None:
    if (worktree / "customer_artifact.md").exists():
        raise ReplayError("customer_artifact.md should be removed after incident cleanup.")


def replay_day(source_repo: Path, day: str) -> dict[str, Any]:
    scenario_name = f"day{day}"
    with tempfile.TemporaryDirectory(prefix=f"aegisap-{scenario_name}-") as temp_dir:
        worktree = Path(temp_dir) / "worktree"
        run_git(cwd=source_repo, args=["worktree", "add", "--detach", str(worktree), "HEAD"])
        try:
            scenario = load_scenario(worktree, day)
            steps: list[dict[str, Any]] = []

            steps.append(run_shell(cwd=worktree, command=f"uv run aegisap-lab incident start --day {day}"))
            steps.append(apply_reference_fix(worktree=worktree, day=day, scenario=scenario))
            steps.append(run_shell(cwd=worktree, command=scenario["validation"]["ci_command"]))
            steps.append(run_shell(cwd=worktree, command=f"uv run aegisap-lab incident reset --day {day}"))
            assert_no_customer_artifact(worktree)
            assert_clean_worktree(worktree)

            steps.append(run_shell(cwd=worktree, command=f"uv run aegisap-lab incident start --day {day}"))
            steps.append(run_shell(cwd=worktree, command=f"uv run aegisap-lab incident nuke --day {day}"))
            steps.append(run_shell(cwd=worktree, command=scenario["validation"]["ci_command"]))
            assert_no_customer_artifact(worktree)
            assert_clean_worktree(worktree)

            return {
                "day": day,
                "scenario": scenario_name,
                "status": "passed",
                "steps": steps,
            }
        finally:
            run_git(cwd=source_repo, args=["worktree", "remove", "--force", str(worktree)])


def main() -> int:
    args = parse_args()
    root = repo_root(__file__)
    results = [replay_day(root, day) for day in args.days]

    summary = {
        "label": args.label,
        "status": "passed",
        "days": results,
    }
    out_path = Path(args.out_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
