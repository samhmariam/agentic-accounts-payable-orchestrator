#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os

from aegisap.day4.state.workflow_state import WorkflowState as Day4WorkflowState
from aegisap.training.artifacts import write_json_artifact
from aegisap.training.postgres import build_store_from_env
from aegisap.day5.workflow.training_runtime import create_day5_pause
from aegisap.training.artifacts import load_json, build_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pause a Day 4 case at the Day 5 approval boundary.")
    parser.add_argument(
        "--day4-artifact",
        default="build/day4/golden_thread_day4.json",
        help="Path to the Day 4 artifact JSON file.",
    )
    parser.add_argument(
        "--thread-id",
        default="thread-golden-001",
        help="Thread ID to use for the durable Day 5 checkpoint.",
    )
    parser.add_argument(
        "--assigned-to",
        default="controller@example.com",
        help="Finance Controller assignee for the approval task.",
    )
    parser.add_argument(
        "--artifact-name",
        default="golden_thread_day5_pause",
        help="Artifact file name under build/day5 without the .json suffix.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = load_json(args.day4_artifact)
    day4_state = Day4WorkflowState.model_validate(payload["workflow_state"])
    token_secret = os.getenv("AEGISAP_RESUME_TOKEN_SECRET", "dev-only-resume-secret")
    pause_payload = create_day5_pause(
        day4_state=day4_state,
        thread_id=args.thread_id,
        assigned_to=args.assigned_to,
        store=build_store_from_env(),
        token_secret=token_secret,
    )
    artifact_path = write_json_artifact(build_root("day5") / f"{args.artifact_name}.json", pause_payload)
    print(f"Day 5 pause complete: {artifact_path}")
    print(
        f"Thread {pause_payload['thread_id']} parked at checkpoint {pause_payload['checkpoint_id']} "
        f"for approval task {pause_payload['approval_task_id']}."
    )


if __name__ == "__main__":
    main()
