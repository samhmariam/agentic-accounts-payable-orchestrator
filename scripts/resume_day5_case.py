#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os

from aegisap.training.artifacts import build_root, load_json, write_json_artifact
from aegisap.training.postgres import build_store_from_env
from aegisap.day5.workflow.training_runtime import resume_day5_case


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resume a Day 5 approval task from a saved token.")
    parser.add_argument(
        "--pause-artifact",
        default="build/day5/golden_thread_day5_pause.json",
        help="Path to the Day 5 pause artifact JSON file.",
    )
    parser.add_argument(
        "--status",
        choices=["approved", "rejected"],
        default="approved",
        help="Approval decision to apply.",
    )
    parser.add_argument(
        "--comment",
        default="Training approval decision recorded.",
        help="Controller comment to persist on resume.",
    )
    parser.add_argument(
        "--resumed-by",
        default="controller@example.com",
        help="Operator identity for the resume action.",
    )
    parser.add_argument(
        "--artifact-name",
        default="golden_thread_day5_resumed",
        help="Artifact file name under build/day5 without the .json suffix.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pause_payload = load_json(args.pause_artifact)
    resumed = resume_day5_case(
        store=build_store_from_env(),
        token_secret=os.getenv("AEGISAP_RESUME_TOKEN_SECRET", "dev-only-resume-secret"),
        resume_token=pause_payload["resume_token"],
        decision_payload={"status": args.status, "comment": args.comment},
        resumed_by=args.resumed_by,
    )
    artifact_path = write_json_artifact(
        build_root("day5") / f"{args.artifact_name}.json",
        resumed.model_dump(mode="json"),
    )
    print(f"Day 5 resume complete: {artifact_path}")
    print(
        f"Thread {resumed.thread_id} is now '{resumed.thread_status}' at node "
        f"'{resumed.current_node}'."
    )


if __name__ == "__main__":
    main()
