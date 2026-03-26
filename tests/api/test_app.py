from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi.testclient import TestClient

from aegisap.api.app import app
from aegisap.day5.workflow.resume_service import ResumeTokenCodec, ResumeTokenPayload
from aegisap.training.fixtures import golden_thread_path


client = TestClient(app)


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_healthz_returns_ok() -> None:
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_day1_intake_accepts_fixture_candidate() -> None:
    response = client.post(
        "/api/day1/intake",
        json={
            "package": _load(str(golden_thread_path("package.json"))),
            "candidate": _load(str(golden_thread_path("candidate.json"))),
        },
    )

    assert response.status_code == 200
    assert response.json()["canonical_invoice"]["invoice_number"] == "INV-3001"


def test_day4_case_run_returns_plan_and_recommendation() -> None:
    response = client.post(
        "/api/day4/cases/run",
        json={
            "case_facts": _load(str(golden_thread_path("day4_case.json")))["case_facts"],
            "planner_mode": "fixture",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["validated_plan"]["plan_id"] == "plan_case_golden_001"
    assert payload["recommendation"]["status"] == "recommendation_ready"
    assert payload["day6_review"]["outcome"] == "approved_to_proceed"


def test_day5_resume_rejects_path_token_mismatch(monkeypatch) -> None:
    monkeypatch.setenv("AEGISAP_RESUME_TOKEN_SECRET", "test-secret")
    token = ResumeTokenCodec(os.environ["AEGISAP_RESUME_TOKEN_SECRET"]).encode(
        ResumeTokenPayload(
            thread_id="thread-1",
            checkpoint_id="cp-1",
            checkpoint_seq=1,
            approval_task_id="task-1",
        )
    )

    response = client.post(
        "/api/day5/approvals/task-2/resume",
        json={
            "resume_token": token,
            "decision": {"status": "approved", "comment": "ok"},
            "resumed_by": "controller@example.com",
        },
    )

    assert response.status_code == 400
    assert "does not match" in response.json()["detail"]
