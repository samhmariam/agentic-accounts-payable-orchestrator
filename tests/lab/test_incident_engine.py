from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import yaml

from aegisap.lab.engine import load_journal, nuke_incident, reset_incident, start_incident


REPO_ROOT = Path(__file__).resolve().parents[2]


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _build_repo(tmp_path: Path, *, start_sleep: float = 0.0, reset_sleep: float = 0.0) -> Path:
    repo = tmp_path / "lab-repo"
    repo.mkdir()

    _write(
        repo / "pyproject.toml",
        textwrap.dedent(
            """
            [project]
            name = "mini-lab"
            version = "0.0.1"
            """
        ).strip()
        + "\n",
    )
    _write(repo / "app.txt", "healthy\n")
    _write(repo / "scenarios" / "day01" / "customer_artifact.md", "# Test Incident\n")
    _write(
        repo / "scenarios" / "day01" / "seed" / "incident.patch",
        textwrap.dedent(
            """
            diff --git a/app.txt b/app.txt
            --- a/app.txt
            +++ b/app.txt
            @@ -1 +1 @@
            -healthy
            +broken
            """
        ).strip()
        + "\n",
    )
    _write(
        repo / "scripts" / "check_failure.py",
        textwrap.dedent(
            """
            from pathlib import Path
            import sys

            text = Path("app.txt").read_text(encoding="utf-8").strip()
            raise SystemExit(1 if text == "broken" else 0)
            """
        ).strip()
        + "\n",
    )
    _write(
        repo / "scripts" / "check_success.py",
        textwrap.dedent(
            """
            from pathlib import Path
            import sys

            text = Path("app.txt").read_text(encoding="utf-8").strip()
            raise SystemExit(0 if text == "healthy" else 1)
            """
        ).strip()
        + "\n",
    )
    _write(
        repo / "scripts" / "mark_azure.py",
        textwrap.dedent(
            """
            import json
            import sys
            import time
            from pathlib import Path

            action = sys.argv[1]
            sleep_seconds = float(sys.argv[2])
            if sleep_seconds:
                time.sleep(sleep_seconds)

            receipt_dir = Path(".aegisap-lab") / "receipts"
            receipt_dir.mkdir(parents=True, exist_ok=True)
            (receipt_dir / f"{action}.json").write_text(json.dumps({"action": action}), encoding="utf-8")
            """
        ).strip()
        + "\n",
    )
    _write(
        repo / "scripts" / "baseline.py",
        textwrap.dedent(
            """
            import json
            from pathlib import Path

            Path("app.txt").write_text("healthy\\n", encoding="utf-8")
            receipt_dir = Path(".aegisap-lab") / "baseline"
            receipt_dir.mkdir(parents=True, exist_ok=True)
            (receipt_dir / "baseline.json").write_text(json.dumps({"status": "rebuilt"}), encoding="utf-8")
            """
        ).strip()
        + "\n",
    )

    scenario = {
        "day": "01",
        "title": "Mini incident",
        "phase": "phase_1_trust_boundary",
        "baseline_track": "core",
        "baseline_reprovision_command": f"{sys.executable} scripts/baseline.py",
        "setup": {
            "apply_diff": "seed/incident.patch",
            "azure_script": f"{sys.executable} scripts/mark_azure.py break {start_sleep}",
            "customer_drop": "customer_artifact.md",
        },
        "validation": {
            "reproduce_command": f"{sys.executable} scripts/check_failure.py",
            "ci_command": f"{sys.executable} scripts/check_success.py",
        },
        "teardown": {
            "revert_diff": "seed/incident.patch",
            "azure_script": f"{sys.executable} scripts/mark_azure.py restore {reset_sleep}",
            "cleanup": ["customer_artifact.md"],
        },
        "review": {
            "evaluator_profile": "test-profile",
            "human_required": True,
        },
    }
    _write(repo / "scenarios" / "day01" / "scenario.yaml", yaml.safe_dump(scenario, sort_keys=False))

    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial state")
    _git(repo, "branch", "-M", "main")
    return repo


def _cli_env() -> dict[str, str]:
    env = os.environ.copy()
    workspace_src = str(REPO_ROOT / "src")
    current = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = workspace_src if not current else f"{workspace_src}:{current}"
    return env


def _wait_for(predicate, *, timeout: float = 5.0, interval: float = 0.05) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return
        time.sleep(interval)
    raise AssertionError("Timed out waiting for incident checkpoint.")


def test_incident_start_and_reset_round_trip(tmp_path: Path) -> None:
    repo = _build_repo(tmp_path)

    journal = start_incident(day="01", repo_path=repo)

    assert journal.status == "ready"
    assert (repo / "customer_artifact.md").exists()
    assert (repo / "app.txt").read_text(encoding="utf-8").strip() == "broken"
    assert load_journal(repo, "01") is not None

    reset = reset_incident(day="01", repo_path=repo)

    assert reset.status == "reset"
    assert not (repo / "customer_artifact.md").exists()
    assert (repo / "app.txt").read_text(encoding="utf-8").strip() == "healthy"
    current_branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert current_branch == "main"


def test_incident_can_restart_after_reset_with_lab_state_present(tmp_path: Path) -> None:
    repo = _build_repo(tmp_path)

    start_incident(day="01", repo_path=repo)
    reset_incident(day="01", repo_path=repo)
    restarted = start_incident(day="01", repo_path=repo)

    assert restarted.status == "ready"


def test_incident_reset_restores_detached_worktree_checkout(tmp_path: Path) -> None:
    repo = _build_repo(tmp_path)
    worktree = tmp_path / "detached-worktree"
    _git(repo, "worktree", "add", "--detach", str(worktree), "HEAD")

    try:
        original_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=worktree,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        start_incident(day="01", repo_path=worktree)
        reset_incident(day="01", repo_path=worktree)

        restored_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=worktree,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        current_branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=worktree,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        assert restored_head == original_head
        assert current_branch == ""
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree)],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        )


def test_incident_start_records_interrupted_state(tmp_path: Path) -> None:
    repo = _build_repo(tmp_path, start_sleep=5.0)
    process = subprocess.Popen(
        [sys.executable, "-m", "aegisap.lab.cli", "--repo-root", str(repo), "incident", "start", "--day", "01"],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=_cli_env(),
    )

    _wait_for(
        lambda: (journal := load_journal(repo, "01")) is not None
        and journal.current_step == "azure_break_applied"
    )
    process.send_signal(signal.SIGTERM)
    process.wait(timeout=10)

    journal = load_journal(repo, "01")
    assert journal is not None
    assert journal.status == "interrupted"


def test_incident_reset_records_interrupted_state(tmp_path: Path) -> None:
    repo = _build_repo(tmp_path, reset_sleep=5.0)
    start_incident(day="01", repo_path=repo)

    process = subprocess.Popen(
        [sys.executable, "-m", "aegisap.lab.cli", "--repo-root", str(repo), "incident", "reset", "--day", "01"],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=_cli_env(),
    )

    _wait_for(
        lambda: (journal := load_journal(repo, "01")) is not None
        and journal.current_step == "azure_restore_applied"
    )
    process.send_signal(signal.SIGTERM)
    process.wait(timeout=10)

    journal = load_journal(repo, "01")
    assert journal is not None
    assert journal.status == "interrupted"


def test_incident_nuke_restores_baseline_without_journal_replay(tmp_path: Path) -> None:
    repo = _build_repo(tmp_path)
    start_incident(day="01", repo_path=repo)
    (repo / "app.txt").write_text("custom user changes\n", encoding="utf-8")

    journal = nuke_incident(day="01", repo_path=repo)

    assert journal.status == "nuked"
    assert (repo / "app.txt").read_text(encoding="utf-8").strip() == "healthy"
    baseline_receipt = repo / ".aegisap-lab" / "baseline" / "baseline.json"
    assert baseline_receipt.exists()
