from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from aegisap.api.app import app
from aegisap.api.release import decision_envelope
from aegisap.day6.graph.review_gate import run_day6_review
from aegisap.day6.state.models import Day6ReviewInput
from aegisap.training.fixtures import day6_fixture_path, golden_thread_path


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_health_and_version_endpoints_include_release_metadata(monkeypatch) -> None:
    monkeypatch.setenv("AEGISAP_SERVICE_NAME", "aegisap-api")
    monkeypatch.setenv("AEGISAP_GIT_SHA", "abc123def456")
    monkeypatch.setenv("AEGISAP_IMAGE_TAG", "abc123def456")
    monkeypatch.setenv("AEGISAP_DEPLOYMENT_REVISION", "staging-abc123def456")
    monkeypatch.setenv("AEGISAP_TRACING_ENABLED", "false")
    monkeypatch.setenv("AEGISAP_RESUME_TOKEN_SECRET", "test-secret")
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)

    with TestClient(app) as client:
        live = client.get("/health/live")
        ready = client.get("/health/ready")
        version = client.get("/version")

    assert live.status_code == 200
    assert ready.status_code == 200
    assert version.status_code == 200
    assert live.json()["git_sha"] == "abc123def456"
    assert ready.json()["deployment_revision"] == "staging-abc123def456"
    assert version.json()["image_tag"] == "abc123def456"


def test_workflow_alias_returns_release_and_decision_metadata() -> None:
    case_payload = _load_json(golden_thread_path("day4_case.json"))

    with TestClient(app) as client:
        response = client.post(
            "/workflow/run",
            json={
                "case_facts": case_payload["case_facts"],
                "planner_mode": "fixture",
                "enable_day6_review": True,
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["decision"]["decision_class"] == "approved"
    assert payload["release"]["git_sha"]
    assert payload["correlation"]["revision"]


def test_structured_refusal_envelope_is_machine_readable() -> None:
    fixture = _load_json(day6_fixture_path("prompt_injection_email_case.json"))
    outcome = run_day6_review(Day6ReviewInput.model_validate(fixture["review_input"]))
    envelope = decision_envelope(outcome.model_dump(mode="json"))

    assert envelope.decision_class == "structured_refusal"
    assert envelope.blocking is True
    assert envelope.structured_refusal is not None
    assert envelope.structured_refusal.primary_reason_code in {
        "PROMPT_INJECTION_ATTEMPT",
        "UNTRUSTED_OVERRIDE_REQUEST",
    }
    assert "PROMPT_INJECTION_ATTEMPT" in envelope.structured_refusal.reason_codes


def test_day10_eval_assets_have_expected_case_counts() -> None:
    synthetic_count = len(Path("evals/synthetic_cases.jsonl").read_text(encoding="utf-8").splitlines())
    malicious_count = len(Path("evals/malicious_cases.jsonl").read_text(encoding="utf-8").splitlines())

    assert synthetic_count == 50
    assert malicious_count == 20
