from __future__ import annotations

import asyncio

from aegisap.training.fixtures import golden_thread_path
from aegisap.training.labs import (
    load_day6_review_input,
    load_case_facts,
    run_day1_fixture,
    run_day2_from_day1_artifact,
    run_day3_case_artifact,
    run_day4_case_artifact,
    run_day6_review_artifact_from_input,
)


def test_day1_fixture_lab_writes_canonical_artifact() -> None:
    artifact_path, payload = run_day1_fixture(
        package_path=golden_thread_path("package.json"),
        candidate_path=golden_thread_path("candidate.json"),
        artifact_name="test_day1_lab",
    )

    assert artifact_path.exists()
    assert payload["canonical_invoice"]["invoice_number"] == "INV-3001"
    assert payload["canonical_invoice"]["supplier_name"] == "Acme Office Supplies"


def test_day2_lab_consumes_day1_artifact() -> None:
    day1_path, _ = run_day1_fixture(
        package_path=golden_thread_path("package.json"),
        candidate_path=golden_thread_path("candidate.json"),
        artifact_name="test_day2_source",
    )

    artifact_path, payload = run_day2_from_day1_artifact(
        artifact_path=day1_path,
        known_vendor=True,
        artifact_name="test_day2_lab",
    )

    assert artifact_path.exists()
    assert payload["workflow_state"]["invoice_id"] == "INV-3001"
    assert payload["workflow_state"]["route"] == "high_value"


def test_day3_lab_writes_evidence_bundle() -> None:
    invoice = {
        "case_id": "case_golden_001",
        "invoice_id": "INV-3001",
        "invoice_date": "2026-03-01",
        "vendor_id": "VEND-001",
        "vendor_name": "Acme Office Supplies",
        "po_number": "PO-9001",
        "amount": 12500.0,
        "currency": "GBP",
        "bank_account_last4": "4421",
    }

    artifact_path, payload = run_day3_case_artifact(
        invoice=invoice,
        retrieval_mode="fixture",
        artifact_name="test_day3_lab",
    )

    assert artifact_path.exists()
    assert payload["workflow_state"]["agent_findings"]["decision"]["recommendation"] == "approve"


def test_day4_fixture_lab_emits_validated_plan() -> None:
    artifact_path, payload, state = asyncio.run(
        run_day4_case_artifact(
            case_facts=load_case_facts(golden_thread_path("day4_case.json")),
            planner_mode="fixture",
            artifact_name="test_day4_lab",
        )
    )

    assert artifact_path.exists()
    assert payload["validated_plan"]["plan_id"] == "plan_case_golden_001"
    assert state.recommendation is not None


def test_day6_lab_writes_review_outcome() -> None:
    artifact_path, payload, review_outcome = run_day6_review_artifact_from_input(
        review_input=load_day6_review_input("fixtures/day06/prompt_injection_email_case.json"),
        artifact_name="test_day6_lab",
    )

    assert artifact_path.exists()
    assert payload["review_outcome"]["outcome"] == "not_authorised_to_continue"
    assert review_outcome.citations
