from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import tempfile
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Any

import yaml

from aegisap.common.paths import repo_root as resolve_repo_root_from_path

from .models import CommandReceipt, IncidentJournal, ScenarioContract, utc_now_iso


STATE_DIR = Path(".aegisap-lab") / "state"
CUSTOMER_ARTIFACT_NAME = "customer_artifact.md"
INCIDENT_BRANCH_PREFIX = "__incident__"


class IncidentError(RuntimeError):
    """Raised when the incident engine cannot safely continue."""


class InterruptedIncident(RuntimeError):
    """Raised when an incident operation is interrupted."""


def scenario_id(day: str) -> str:
    return f"day{int(day):02d}"


def resolve_repo_root(repo_path: str | Path | None = None) -> Path:
    if repo_path is not None:
        return Path(repo_path).resolve()
    return resolve_repo_root_from_fs()


def resolve_repo_root_from_fs() -> Path:
    env_root = os.environ.get("AEGISAP_LAB_REPO_ROOT", "").strip()
    if env_root:
        return Path(env_root).resolve()
    cwd = Path.cwd().resolve()
    if (cwd / "pyproject.toml").exists():
        return cwd
    return resolve_repo_root_from_path(__file__)


def journal_path(repo_root: Path, day: str) -> Path:
    return repo_root / STATE_DIR / f"{scenario_id(day)}.json"


def scenario_dir(repo_root: Path, day: str) -> Path:
    return repo_root / "scenarios" / scenario_id(day)


def scenario_file(repo_root: Path, day: str) -> Path:
    return scenario_dir(repo_root, day) / "scenario.yaml"


def load_scenario(repo_root: Path, day: str) -> ScenarioContract:
    path = scenario_file(repo_root, day)
    if not path.exists():
        raise IncidentError(f"Scenario file not found: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return ScenarioContract.model_validate(payload)


def load_journal(repo_root: Path, day: str) -> IncidentJournal | None:
    path = journal_path(repo_root, day)
    if not path.exists():
        return None
    return IncidentJournal.model_validate_json(path.read_text(encoding="utf-8"))


def save_journal(path: Path, journal: IncidentJournal) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    journal.updated_at = utc_now_iso()
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
        prefix=f".{path.name}.",
        suffix=".tmp",
    ) as handle:
        handle.write(journal.model_dump_json(indent=2))
        temp_path = Path(handle.name)
    os.replace(temp_path, path)


def delete_journal(repo_root: Path, day: str) -> None:
    path = journal_path(repo_root, day)
    if path.exists():
        path.unlink()


def git_output(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise IncidentError(result.stderr.strip() or result.stdout.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def git_current_branch(repo_root: Path) -> str:
    branch = git_output(repo_root, "branch", "--show-current")
    if branch:
        return branch
    return default_branch(repo_root)


def current_checkout_ref(repo_root: Path) -> str:
    branch = git_output(repo_root, "branch", "--show-current")
    if branch:
        return branch
    return git_output(repo_root, "rev-parse", "HEAD")


def default_branch(repo_root: Path) -> str:
    try:
        ref = git_output(repo_root, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    except IncidentError:
        ref = ""
    if "/" in ref:
        return ref.split("/", 1)[1]
    for candidate in ("main", "master"):
        try:
            git_output(repo_root, "rev-parse", "--verify", candidate)
            return candidate
        except IncidentError:
            continue
    return "main"


def ensure_clean_worktree(repo_root: Path) -> None:
    status = git_output(repo_root, "status", "--porcelain")
    unexpected = [
        line for line in status.splitlines()
        if line.strip() and ".aegisap-lab/" not in line
    ]
    if unexpected:
        raise IncidentError(
            "Incident start requires a clean worktree. Commit, stash, or discard local changes first."
        )


def branch_exists(repo_root: Path, branch_name: str) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", branch_name],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def checkout_ref(repo_root: Path, target_ref: str) -> None:
    try:
        git_output(repo_root, "checkout", "--force", target_ref)
    except IncidentError as exc:
        if "is already used by worktree" not in str(exc):
            raise
        resolved_ref = git_output(repo_root, "rev-parse", target_ref)
        git_output(repo_root, "checkout", "--detach", "--force", resolved_ref)


def command_receipt(
    *,
    command: str,
    cwd: Path,
    result: subprocess.CompletedProcess[str],
    started_at: str,
) -> CommandReceipt:
    return CommandReceipt(
        command=command,
        cwd=str(cwd),
        returncode=result.returncode,
        started_at=started_at,
        finished_at=utc_now_iso(),
        stdout_tail="\n".join(result.stdout.strip().splitlines()[-20:]),
        stderr_tail="\n".join(result.stderr.strip().splitlines()[-20:]),
    )


def run_command(
    *,
    repo_root: Path,
    command: str,
    expect_success: bool,
) -> CommandReceipt:
    started_at = utc_now_iso()
    result = subprocess.run(
        command,
        cwd=repo_root,
        shell=True,
        text=True,
        capture_output=True,
        check=False,
    )
    receipt = command_receipt(command=command, cwd=repo_root, result=result, started_at=started_at)
    if expect_success and receipt.returncode != 0:
        raise IncidentError(
            f"Command failed: {command}\n{receipt.stderr_tail or receipt.stdout_tail}"
        )
    if not expect_success and receipt.returncode == 0:
        raise IncidentError(
            f"Reproduce command unexpectedly passed: {command}"
        )
    return receipt


def resolve_relative_path(base_dir: Path, relative_path: str) -> Path:
    return (base_dir / relative_path).resolve()


class InterruptGuard(AbstractContextManager[None]):
    def __init__(self, *, journal: IncidentJournal, journal_file: Path) -> None:
        self.journal = journal
        self.journal_file = journal_file
        self._previous_int = None
        self._previous_term = None
        self._triggered = False

    def __enter__(self) -> None:
        self._previous_int = signal.getsignal(signal.SIGINT)
        self._previous_term = signal.getsignal(signal.SIGTERM)
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        return None

    def __exit__(self, exc_type, exc, _tb) -> bool:
        signal.signal(signal.SIGINT, self._previous_int)
        signal.signal(signal.SIGTERM, self._previous_term)
        if isinstance(exc, InterruptedIncident):
            return False
        return False

    def _handle_signal(self, signum: int, _frame: Any) -> None:
        if self._triggered:
            raise InterruptedIncident(f"Received signal {signum}.")
        self._triggered = True
        self.journal.status = "interrupted"
        self.journal.error_message = f"Interrupted by signal {signum} during step '{self.journal.current_step}'."
        save_journal(self.journal_file, self.journal)
        raise InterruptedIncident(self.journal.error_message)


def _record_step(
    *,
    journal: IncidentJournal,
    journal_file: Path,
    step_name: str,
    receipt: CommandReceipt | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    journal.current_step = step_name
    if step_name not in journal.completed_steps:
        journal.completed_steps.append(step_name)
    if receipt is not None:
        journal.command_receipts[step_name] = receipt
    if metadata:
        journal.metadata.update(metadata)
    save_journal(journal_file, journal)


def _begin_step(
    *,
    journal: IncidentJournal,
    journal_file: Path,
    step_name: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    journal.current_step = step_name
    if metadata:
        journal.metadata.update(metadata)
    save_journal(journal_file, journal)


def _copy_customer_artifact(*, repo_root: Path, scenario_root: Path, relative_source: str) -> Path:
    source = resolve_relative_path(scenario_root, relative_source)
    if not source.exists():
        raise IncidentError(f"Customer artifact not found: {source}")
    destination = repo_root / CUSTOMER_ARTIFACT_NAME
    shutil.copyfile(source, destination)
    return destination


def start_incident(*, day: str, repo_path: str | Path | None = None) -> IncidentJournal:
    root = resolve_repo_root(repo_path)
    scenario_root = scenario_dir(root, day)
    scenario = load_scenario(root, day)
    ensure_clean_worktree(root)
    state_file = journal_path(root, day)
    existing = load_journal(root, day)
    if existing is not None and existing.status not in {"reset", "nuked"}:
        raise IncidentError(f"Incident state already exists for Day {day}: {state_file}")

    original_branch = current_checkout_ref(root)
    incident_branch = f"{INCIDENT_BRANCH_PREFIX}/{scenario_id(day)}-{utc_now_iso().replace(':', '').replace('+', '-').replace('.', '-')}"
    journal = IncidentJournal(
        day=f"{int(day):02d}",
        scenario_file=str(scenario_file(root, day)),
        status="preparing",
        repo_root=str(root),
        scenario_dir=str(scenario_root),
        original_branch=original_branch,
        incident_branch=incident_branch,
    )

    with InterruptGuard(journal=journal, journal_file=state_file):
        save_journal(state_file, journal)
        _record_step(journal=journal, journal_file=state_file, step_name="validated_clean_worktree")
        _begin_step(journal=journal, journal_file=state_file, step_name="incident_branch_created")
        git_output(root, "checkout", "-b", incident_branch)
        _record_step(journal=journal, journal_file=state_file, step_name="incident_branch_created")

        if scenario.setup.apply_diff:
            diff_path = resolve_relative_path(scenario_root, scenario.setup.apply_diff)
            _begin_step(
                journal=journal,
                journal_file=state_file,
                step_name="incident_diff_applied",
                metadata={"incident_diff": str(diff_path)},
            )
            git_output(root, "apply", str(diff_path))
            _record_step(
                journal=journal,
                journal_file=state_file,
                step_name="incident_diff_applied",
                metadata={"incident_diff": str(diff_path)},
            )

        if scenario.setup.azure_script:
            _begin_step(journal=journal, journal_file=state_file, step_name="azure_break_applied")
            receipt = run_command(repo_root=root, command=scenario.setup.azure_script, expect_success=True)
            _record_step(
                journal=journal,
                journal_file=state_file,
                step_name="azure_break_applied",
                receipt=receipt,
            )

        if scenario.setup.customer_drop:
            _begin_step(journal=journal, journal_file=state_file, step_name="customer_artifact_dropped")
            dropped = _copy_customer_artifact(
                repo_root=root,
                scenario_root=scenario_root,
                relative_source=scenario.setup.customer_drop,
            )
            journal.dropped_files.append(str(dropped.relative_to(root)))
            _record_step(journal=journal, journal_file=state_file, step_name="customer_artifact_dropped")

        _begin_step(journal=journal, journal_file=state_file, step_name="failure_reproduced")
        reproduce_receipt = run_command(
            repo_root=root,
            command=scenario.validation.reproduce_command,
            expect_success=False,
        )
        _record_step(
            journal=journal,
            journal_file=state_file,
            step_name="failure_reproduced",
            receipt=reproduce_receipt,
        )
        journal.status = "ready"
        journal.current_step = ""
        save_journal(state_file, journal)
    return journal


def _restore_cleanup_paths(*, repo_root: Path, cleanup_paths: list[str]) -> None:
    for rel_path in cleanup_paths:
        candidate = (repo_root / rel_path).resolve()
        if candidate.is_file():
            candidate.unlink()
        elif candidate.is_dir():
            shutil.rmtree(candidate)


def reset_incident(*, day: str, repo_path: str | Path | None = None) -> IncidentJournal:
    root = resolve_repo_root(repo_path)
    scenario = load_scenario(root, day)
    state_file = journal_path(root, day)
    journal = load_journal(root, day)
    if journal is None:
        raise IncidentError(f"No incident state found for Day {day}.")

    with InterruptGuard(journal=journal, journal_file=state_file):
        journal.status = "preparing"
        journal.current_step = "resetting"
        save_journal(state_file, journal)

        if "azure_break_applied" in journal.completed_steps and scenario.teardown.azure_script:
            _begin_step(journal=journal, journal_file=state_file, step_name="azure_restore_applied")
            receipt = run_command(repo_root=root, command=scenario.teardown.azure_script, expect_success=True)
            _record_step(
                journal=journal,
                journal_file=state_file,
                step_name="azure_restore_applied",
                receipt=receipt,
            )

        cleanup_paths = list(dict.fromkeys(journal.dropped_files + scenario.teardown.cleanup))
        _begin_step(journal=journal, journal_file=state_file, step_name="workspace_cleanup_complete")
        _restore_cleanup_paths(repo_root=root, cleanup_paths=cleanup_paths)
        _record_step(journal=journal, journal_file=state_file, step_name="workspace_cleanup_complete")

        target_branch = journal.original_branch or default_branch(root)
        current_branch = git_current_branch(root)
        if current_branch != target_branch:
            checkout_ref(root, target_branch)
        if journal.incident_branch and branch_exists(root, journal.incident_branch):
            current_branch = git_current_branch(root)
            if current_branch == journal.incident_branch:
                checkout_ref(root, target_branch)
            git_output(root, "branch", "-D", journal.incident_branch)

        journal.status = "reset"
        journal.current_step = ""
        save_journal(state_file, journal)
    return journal


def nuke_incident(*, day: str, repo_path: str | Path | None = None) -> IncidentJournal:
    root = resolve_repo_root(repo_path)
    scenario_root = scenario_dir(root, day)
    scenario = load_scenario(root, day)
    state_file = journal_path(root, day)
    current_branch = git_current_branch(root)
    target_branch = default_branch(root)
    if current_branch != target_branch:
        try:
            checkout_ref(root, target_branch)
        except IncidentError:
            pass
    for branch in git_output(root, "branch", "--list", f"{INCIDENT_BRANCH_PREFIX}/{scenario_id(day)}-*").splitlines():
        branch_name = branch.replace("*", "").strip()
        if branch_name:
            try:
                git_output(root, "branch", "-D", branch_name)
            except IncidentError:
                continue
    run_command(
        repo_root=root,
        command=scenario.baseline_reprovision_command,
        expect_success=True,
    )
    _restore_cleanup_paths(
        repo_root=root,
        cleanup_paths=[CUSTOMER_ARTIFACT_NAME] + scenario.teardown.cleanup,
    )
    journal = IncidentJournal(
        day=f"{int(day):02d}",
        scenario_file=str(scenario_file(root, day)),
        status="nuked",
        repo_root=str(root),
        scenario_dir=str(scenario_root),
        original_branch=target_branch,
        incident_branch="",
        completed_steps=["baseline_reprovisioned", "workspace_cleanup_complete"],
    )
    save_journal(state_file, journal)
    return journal


def status_incident(*, day: str, repo_path: str | Path | None = None) -> IncidentJournal | None:
    root = resolve_repo_root(repo_path)
    return load_journal(root, day)
