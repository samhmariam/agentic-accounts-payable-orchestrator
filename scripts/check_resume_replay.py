#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from aegisap.training.fixtures import golden_thread_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate pause/resume idempotency against a deployed AegisAP app.")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--case-facts", default=str(golden_thread_path("day4_case.json")))
    parser.add_argument("--planner-mode", choices=["fixture", "azure_openai"], default="azure_openai")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_url = args.base_url.rstrip("/")
    case_facts = json.loads(Path(args.case_facts).read_text(encoding="utf-8"))["case_facts"]
    thread_id = f"thread-day10-replay-{uuid.uuid4().hex[:8]}"
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
    handoff = run_payload["day5_handoff"]
    resumed = _request(
        "POST",
        f"{base_url}/workflow/resume/{case_facts['case_id']}",
        {
            "resume_token": handoff["resume_token"],
            "decision": {"status": "approved", "comment": "Replay gate approval."},
            "resumed_by": "controller@example.com",
        },
    )
    snapshot = _request("GET", f"{base_url}/api/day5/threads/{handoff['thread_id']}")
    recommendation_hash = _stable_hash(resumed.get("payment_recommendation"))
    snapshot_hash = _stable_hash(snapshot.get("payment_recommendation"))
    if recommendation_hash != snapshot_hash:
        raise SystemExit("final recommendation hash changed between resume response and thread snapshot")

    effect_keys = [record["effect_key"] for record in snapshot.get("side_effect_records", [])]
    if len(effect_keys) != len(set(effect_keys)):
        raise SystemExit("duplicate side effect record detected")

    audit_keys = [
        (event.get("action_type"), event.get("decision_outcome"), event.get("trace_id"))
        for event in snapshot.get("audit_events", [])
    ]
    if len(audit_keys) != len(set(audit_keys)):
        raise SystemExit("duplicate audit row detected")

    second_resume_status = _try_request(
        "POST",
        f"{base_url}/workflow/resume/{case_facts['case_id']}",
        {
            "resume_token": handoff["resume_token"],
            "decision": {"status": "approved", "comment": "Second replay attempt."},
            "resumed_by": "controller@example.com",
        },
    )
    if second_resume_status == 200:
        raise SystemExit("second resume unexpectedly succeeded")
    print(
        json.dumps(
            {
                "status": "ok",
                "recommendation_hash": recommendation_hash,
                "side_effect_count": len(effect_keys),
                "audit_event_count": len(audit_keys),
                "second_resume_status": second_resume_status,
            },
            indent=2,
        )
    )


def _stable_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode("utf-8")).hexdigest()


def _request(method: str, url: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, method=method, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else {}


def _try_request(method: str, url: str, payload: dict | None = None) -> int:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, method=method, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code


if __name__ == "__main__":
    main()
