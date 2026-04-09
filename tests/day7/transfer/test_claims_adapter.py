from __future__ import annotations

from pathlib import Path

from aegisap.training import transfer as transfer_module
from aegisap.training.transfer import build_day7_claims_transfer_report
from aegisap.transfer import adapt_claim_to_control_signals, evaluate_control_signals, load_claim_payload


REPO_ROOT = Path(__file__).resolve().parents[3]
TRAINEE_FIXTURES = REPO_ROOT / "fixtures" / "capstone_b" / "claims_intake"
ASSESSOR_FIXTURE = (
    REPO_ROOT
    / "fixtures"
    / "capstone_b"
    / "_assessor_only"
    / "claims_intake"
    / "claim_006_assessor_only.json"
)


def _load(name: str) -> dict:
    return load_claim_payload(TRAINEE_FIXTURES / name)


def test_routine_claim_maps_to_auto_approved() -> None:
    signals = adapt_claim_to_control_signals(_load("claim_001_routine.json"))
    decision = evaluate_control_signals(signals)

    assert signals.claim_number == "CL-100001"
    assert signals.procedure_codes == ["E0601"]
    assert signals.diagnosis_codes == ["G47.33"]
    assert decision.outcome == "auto_approved"
    assert decision.reason_codes == []


def test_high_value_claim_requires_manual_review() -> None:
    signals = adapt_claim_to_control_signals(_load("claim_002_high_value.json"))
    decision = evaluate_control_signals(signals)

    assert signals.high_value is True
    assert signals.manual_review_reasons == ["HIGH_VALUE_CLAIM"]
    assert decision.outcome == "pending_adjudicator_review"
    assert decision.manual_review_required is True


def test_missing_auth_claim_refuses_fail_closed() -> None:
    signals = adapt_claim_to_control_signals(_load("claim_003_missing_auth.json"))
    decision = evaluate_control_signals(signals)

    assert signals.authorisation_present is False
    assert "MISSING_AUTH" in decision.reason_codes
    assert decision.outcome == "refused"


def test_code_mismatch_claim_refuses_fail_closed() -> None:
    signals = adapt_claim_to_control_signals(_load("claim_004_code_mismatch.json"))
    decision = evaluate_control_signals(signals)

    assert signals.code_mismatch is True
    assert "CODE_MISMATCH" in decision.reason_codes
    assert decision.outcome == "refused"


def test_duplicate_claim_refuses_from_related_claim_reference() -> None:
    signals = adapt_claim_to_control_signals(_load("claim_005_duplicate.json"))
    decision = evaluate_control_signals(signals)

    assert signals.duplicate_detected is True
    assert "DUPLICATE_DETECTED" in decision.reason_codes
    assert any("related-claim reference" in note for note in signals.raw_shape_notes)


def test_assessor_only_claim_refuses_malformed_amount_field() -> None:
    signals = adapt_claim_to_control_signals(load_claim_payload(ASSESSOR_FIXTURE))
    decision = evaluate_control_signals(signals)

    assert signals.malformed_amount is True
    assert "MALFORMED_AMOUNT_FIELD" in decision.reason_codes
    assert decision.outcome == "refused"


def test_day7_claims_transfer_report_captures_adapter_boundary(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(transfer_module, "build_root", lambda _day: tmp_path)

    artifact_path, payload = build_day7_claims_transfer_report(fixtures_dir=TRAINEE_FIXTURES)

    outcomes = {case["case_id"]: case["decision"]["outcome"] for case in payload["cases"]}

    assert artifact_path == tmp_path / "claims_transfer_report.json"
    assert artifact_path.exists()
    assert payload["adapter_boundary"] == "claims_payload -> ControlSignals -> fail_closed_decision"
    assert payload["total_cases"] == 5
    assert outcomes["claim_001_routine"] == "auto_approved"
    assert outcomes["claim_002_high_value"] == "pending_adjudicator_review"
    assert outcomes["claim_003_missing_auth"] == "refused"
    assert outcomes["claim_004_code_mismatch"] == "refused"
    assert outcomes["claim_005_duplicate"] == "refused"
