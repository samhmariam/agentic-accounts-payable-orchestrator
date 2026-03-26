#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.request
import uuid
from pathlib import Path

from aegisap.training.fixtures import golden_thread_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Day 10 smoke tests against a deployed AegisAP service.")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--case-facts", default=str(golden_thread_path("day4_case.json")))
    parser.add_argument("--planner-mode", choices=["fixture", "azure_openai"], default="azure_openai")
    parser.add_argument("--expected-sha", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_url = args.base_url.rstrip("/")
    live = _request("GET", f"{base_url}/health/live")
    ready = _request("GET", f"{base_url}/health/ready")
    version = _request("GET", f"{base_url}/version")
    if args.expected_sha and version.get("git_sha") != args.expected_sha:
        raise SystemExit(f"version SHA mismatch: expected {args.expected_sha}, got {version.get('git_sha')}")

    case_facts = json.loads(Path(args.case_facts).read_text(encoding="utf-8"))["case_facts"]
    thread_id = f"thread-day10-smoke-{uuid.uuid4().hex[:8]}"
    run_payload = _request(
        "POST",
        f"{base_url}/workflow/run",
        {
            "case_facts": case_facts,
            "planner_mode": args.planner_mode,
            "enable_day6_review": True,
            "persist_day5_handoff": True,
            "thread_id": thread_id,
            "assigned_to": "controller@example.com",
        },
    )
    handoff = run_payload.get("day5_handoff") or {}
    resume_payload = _request(
        "POST",
        f"{base_url}/workflow/resume/{case_facts['case_id']}",
        {
            "resume_token": handoff["resume_token"],
            "decision": {"status": "approved", "comment": "Day 10 smoke approval."},
            "resumed_by": "controller@example.com",
        },
    )
    thread_snapshot = _request("GET", f"{base_url}/api/day5/threads/{handoff['thread_id']}")

    summary = {
        "live": live,
        "ready": ready,
        "version": version,
        "workflow_run": run_payload,
        "resume": resume_payload,
        "thread_snapshot": thread_snapshot,
    }
    print(json.dumps(summary, indent=2))


def _request(method: str, url: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, method=method, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else {}


if __name__ == "__main__":
    main()
