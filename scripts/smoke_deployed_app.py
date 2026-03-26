#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

from aegisap.training.fixtures import golden_thread_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a deployed Container App smoke test.")
    parser.add_argument("--base-url", required=True, help="Base URL of the deployed AegisAP app.")
    parser.add_argument(
        "--case-facts",
        default=str(golden_thread_path("day4_case.json")),
        help="Path to the Day 4 case facts JSON file.",
    )
    parser.add_argument(
        "--planner-mode",
        choices=["fixture", "azure_openai"],
        default="azure_openai",
        help="Planner mode to exercise through the deployed runtime.",
    )
    return parser.parse_args()


def _request(method: str, url: str, payload: dict | None = None) -> dict:
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, method=method, data=data, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else {}


def main() -> None:
    args = parse_args()
    base_url = args.base_url.rstrip("/")
    _request("GET", f"{base_url}/healthz")

    fixture = json.loads(Path(args.case_facts).read_text(encoding="utf-8"))
    run_payload = _request(
        "POST",
        f"{base_url}/api/day4/cases/run",
        {
            "case_facts": fixture["case_facts"],
            "planner_mode": args.planner_mode,
            "persist_day5_handoff": True,
            "thread_id": "thread-deployed-smoke",
            "assigned_to": "controller@example.com",
        },
    )

    handoff = run_payload["day5_handoff"]
    resumed = _request(
        "POST",
        f"{base_url}/api/day5/approvals/{handoff['approval_task_id']}/resume",
        {
            "resume_token": handoff["resume_token"],
            "decision": {"status": "approved", "comment": "Deployed smoke test approval."},
            "resumed_by": "controller@example.com",
        },
    )
    thread_snapshot = _request(
        "GET",
        f"{base_url}/api/day5/threads/{handoff['thread_id']}",
    )
    print(
        json.dumps(
            {
                "healthz": "ok",
                "day4": run_payload,
                "resume": resumed,
                "thread_snapshot": thread_snapshot,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
