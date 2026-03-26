from __future__ import annotations

import json
from pathlib import Path

from aegisap.day6.graph.review_gate import run_day6_review
from aegisap.day6.state.models import Day6ReviewInput, ReviewOutcome
from aegisap.training.fixtures import day6_fixture_path


def _load_fixture(name: str) -> Day6ReviewInput:
    payload = json.loads(Path(day6_fixture_path(f"{name}.json")).read_text(encoding="utf-8"))
    return Day6ReviewInput.model_validate(payload["review_input"])


def test_clean_authorised_case_maps_to_approved_to_proceed() -> None:
    result = run_day6_review(_load_fixture("clean_authorised_case"))

    assert result.outcome == "approved_to_proceed"
    assert result.authorisation_check.present is True


def test_missing_approval_case_maps_to_human_review() -> None:
    result = run_day6_review(_load_fixture("missing_approval_case"))

    assert result.outcome == "needs_human_review"
    assert any(reason.code == "MISSING_AUTHORITY" for reason in result.reasons)


def test_contradictory_tax_case_never_approves() -> None:
    result = run_day6_review(_load_fixture("contradictory_tax_case"))

    assert result.outcome == "needs_human_review"
    assert result.evidence_assessment.sufficiency == "conflicting"
    assert any(reason.code == "CONTRADICTORY_EVIDENCE" for reason in result.reasons)


def test_prompt_injection_email_maps_to_terminal_refusal() -> None:
    result = run_day6_review(_load_fixture("prompt_injection_email_case"))

    assert result.outcome == "not_authorised_to_continue"
    assert any(reason.code == "PROMPT_INJECTION_ATTEMPT" for reason in result.reasons)
    assert any(reason.code == "UNTRUSTED_OVERRIDE_REQUEST" for reason in result.reasons)
    assert result.citations


def test_unsupported_approval_channel_maps_to_terminal_refusal() -> None:
    result = run_day6_review(_load_fixture("unsupported_approval_channel_case"))

    assert result.outcome == "not_authorised_to_continue"
    assert any(reason.code in {"MISSING_AUTHORITY", "UNVERIFIED_APPROVAL_CLAIM"} for reason in result.reasons)


def test_missing_po_exception_maps_to_human_review() -> None:
    result = run_day6_review(_load_fixture("missing_po_exception_case"))

    assert result.outcome == "needs_human_review"
    assert any(reason.code == "INSUFFICIENT_EVIDENCE" for reason in result.reasons)


def test_terminal_refusal_schema_requires_high_severity_reason_and_citation() -> None:
    result = run_day6_review(_load_fixture("prompt_injection_email_case"))

    revalidated = ReviewOutcome.model_validate(result.model_dump(mode="json"))

    assert revalidated.outcome == "not_authorised_to_continue"

