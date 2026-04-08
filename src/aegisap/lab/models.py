from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SetupContract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    apply_diff: str = ""
    azure_script: str = ""
    customer_drop: str = ""


class ValidationContract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reproduce_command: str
    ci_command: str


class TeardownContract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    revert_diff: str = ""
    azure_script: str = ""
    cleanup: list[str] = Field(default_factory=list)


class ReviewContract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evaluator_profile: str
    human_required: bool = True


class ScenarioContract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day: str
    title: str
    phase: str
    baseline_track: str
    baseline_reprovision_command: str
    setup: SetupContract
    validation: ValidationContract
    teardown: TeardownContract
    review: ReviewContract


class CommandReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command: str
    cwd: str
    returncode: int
    started_at: str
    finished_at: str
    stdout_tail: str = ""
    stderr_tail: str = ""


class IncidentJournal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day: str
    scenario_file: str
    status: Literal["preparing", "ready", "interrupted", "error", "reset", "nuked"]
    repo_root: str
    scenario_dir: str
    original_branch: str = ""
    incident_branch: str = ""
    current_step: str = ""
    completed_steps: list[str] = Field(default_factory=list)
    dropped_files: list[str] = Field(default_factory=list)
    command_receipts: dict[str, CommandReceipt] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    updated_at: str = Field(default_factory=utc_now_iso)
    error_message: str = ""

    @property
    def repo_path(self) -> Path:
        return Path(self.repo_root)
