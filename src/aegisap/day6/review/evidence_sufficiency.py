from __future__ import annotations

from collections.abc import Iterable

from aegisap.day6.state.models import (
    Day6ReviewInput,
    EvidenceAssessment,
    MandatoryCheckResult,
)


def evaluate_evidence_sufficiency(
    review_input: Day6ReviewInput,
    *,
    injection_detected: bool,
    conflicting_claims: list[str],
) -> EvidenceAssessment:
    checks: list[MandatoryCheckResult] = [
        _invoice_identity_check(review_input),
        _supplier_identity_check(review_input),
        _po_requirement_check(review_input),
        _bank_change_check(review_input),
        _approval_route_check(review_input),
        _tax_support_check(review_input),
        _action_scope_check(review_input),
    ]

    if injection_detected:
        checks.append(
            MandatoryCheckResult(
                check_id="case_material_override_attempt",
                status="fail",
                reason_code="PROMPT_INJECTION_ATTEMPT",
                evidence_ids=_evidence_ids_by_source_type(review_input, {"email"}),
                missing_evidence=[],
                policy_ids=["POL-CTRL-001"],
            )
        )
    else:
        checks.append(
            MandatoryCheckResult(
                check_id="case_material_override_attempt",
                status="pass",
                reason_code="none",
                evidence_ids=[],
                missing_evidence=[],
                policy_ids=["POL-CTRL-001"],
            )
        )

    if conflicting_claims or review_input.conflict_flags:
        checks.append(
            MandatoryCheckResult(
                check_id="contradiction_detection",
                status="fail",
                reason_code="CONTRADICTORY_EVIDENCE",
                evidence_ids=_collect_conflict_evidence(review_input),
                missing_evidence=[],
                policy_ids=["POL-EVID-002"],
            )
        )
    else:
        checks.append(
            MandatoryCheckResult(
                check_id="contradiction_detection",
                status="pass",
                reason_code="none",
                evidence_ids=[],
                missing_evidence=[],
                policy_ids=["POL-EVID-002"],
            )
        )

    failing_codes = {
        check.reason_code
        for check in checks
        if check.status == "fail" and check.reason_code != "none"
    }
    if "CONTRADICTORY_EVIDENCE" in failing_codes:
        sufficiency = "conflicting"
    elif any(check.status == "fail" for check in checks):
        sufficiency = "insufficient"
    else:
        sufficiency = "sufficient"

    return EvidenceAssessment(sufficiency=sufficiency, mandatory_checks=checks)


def _invoice_identity_check(review_input: Day6ReviewInput) -> MandatoryCheckResult:
    case_fact_evidence = [item.evidence_id for item in review_input.evidence_ledger if item.source_type == "case_summary"]
    return MandatoryCheckResult(
        check_id="invoice_identity_verified",
        status="pass" if case_fact_evidence else "fail",
        reason_code="none" if case_fact_evidence else "INSUFFICIENT_EVIDENCE",
        evidence_ids=case_fact_evidence,
        missing_evidence=[] if case_fact_evidence else ["case_summary"],
        policy_ids=["POL-EVID-002"],
    )


def _supplier_identity_check(review_input: Day6ReviewInput) -> MandatoryCheckResult:
    evidence_ids = _evidence_ids_by_source_type(review_input, {"vendor_master", "case_summary"})
    return MandatoryCheckResult(
        check_id="supplier_identity_verified",
        status="pass" if evidence_ids else "fail",
        reason_code="none" if evidence_ids else "INSUFFICIENT_EVIDENCE",
        evidence_ids=evidence_ids,
        missing_evidence=[] if evidence_ids else ["vendor_master_record"],
        policy_ids=["POL-EVID-002"],
    )


def _po_requirement_check(review_input: Day6ReviewInput) -> MandatoryCheckResult:
    if any("po_" in claim.claim_type for claim in review_input.claim_ledger):
        po_ok = _claim_has_value(review_input, "po_match_verification", "po_match_status", "pass")
        waiver_ok = _claim_has_value(review_input, "po_waiver_check", "waiver_present", True)
        if po_ok or waiver_ok:
            return MandatoryCheckResult(
                check_id="po_requirement_satisfied",
                status="pass",
                reason_code="none",
                evidence_ids=_find_supporting_evidence(review_input, {"po_match_verification", "po_waiver_check"}),
                missing_evidence=[],
                policy_ids=["POL-EVID-002"],
            )
        return MandatoryCheckResult(
            check_id="po_requirement_satisfied",
            status="fail",
            reason_code="INSUFFICIENT_EVIDENCE",
            evidence_ids=_find_supporting_evidence(review_input, {"po_match_verification", "po_waiver_check"}),
            missing_evidence=["approved_po_evidence_or_waiver"],
            policy_ids=["POL-EVID-002"],
        )

    return MandatoryCheckResult(
        check_id="po_requirement_satisfied",
        status="not_applicable",
        reason_code="none",
        evidence_ids=[],
        missing_evidence=[],
        policy_ids=["POL-EVID-002"],
    )


def _bank_change_check(review_input: Day6ReviewInput) -> MandatoryCheckResult:
    claim = next((item for item in review_input.claim_ledger if item.claim_type == "vendor_bank_verification"), None)
    if claim is None:
        return MandatoryCheckResult(
            check_id="bank_change_verified_if_changed",
            status="not_applicable",
            reason_code="none",
            evidence_ids=[],
            missing_evidence=[],
            policy_ids=["POL-EVID-002"],
        )

    verified = bool(claim.metadata.get("bank_change_verified"))
    return MandatoryCheckResult(
        check_id="bank_change_verified_if_changed",
        status="pass" if verified else "fail",
        reason_code="none" if verified else "INSUFFICIENT_EVIDENCE",
        evidence_ids=claim.supporting_evidence_ids,
        missing_evidence=[] if verified else ["approved_bank_change_record"],
        policy_ids=["POL-EVID-002"],
    )


def _approval_route_check(review_input: Day6ReviewInput) -> MandatoryCheckResult:
    claim = next((item for item in review_input.claim_ledger if item.claim_type == "threshold_approval_check"), None)
    required_approvals = review_input.authority_context.required_approvals
    if not required_approvals:
        return MandatoryCheckResult(
            check_id="approval_route_defined",
            status="pass",
            reason_code="none",
            evidence_ids=[],
            missing_evidence=[],
            policy_ids=["POL-AUTH-004"],
        )
    if claim and bool(claim.metadata.get("approval_path_defined")):
        return MandatoryCheckResult(
            check_id="approval_route_defined",
            status="pass",
            reason_code="none",
            evidence_ids=claim.supporting_evidence_ids,
            missing_evidence=[],
            policy_ids=["POL-AUTH-004"],
        )
    return MandatoryCheckResult(
        check_id="approval_route_defined",
        status="fail",
        reason_code="MISSING_AUTHORITY",
        evidence_ids=claim.supporting_evidence_ids if claim else [],
        missing_evidence=["registered_approval_route"],
        policy_ids=["POL-AUTH-004"],
    )


def _tax_support_check(review_input: Day6ReviewInput) -> MandatoryCheckResult:
    if "tax_treatment_supported" not in review_input.policy_context.mandatory_checks:
        return MandatoryCheckResult(
            check_id="tax_treatment_supported",
            status="not_applicable",
            reason_code="none",
            evidence_ids=[],
            missing_evidence=[],
            policy_ids=["POL-EVID-002"],
        )

    tax_conflict = "tax_conflict_detected" in review_input.conflict_flags
    tax_missing = "tax_evidence_missing" in review_input.missing_requirements
    if tax_conflict:
        return MandatoryCheckResult(
            check_id="tax_treatment_supported",
            status="fail",
            reason_code="CONTRADICTORY_EVIDENCE",
            evidence_ids=_find_supporting_evidence(review_input, {"tax_treatment"}),
            missing_evidence=[],
            policy_ids=["POL-EVID-002"],
        )
    if tax_missing:
        return MandatoryCheckResult(
            check_id="tax_treatment_supported",
            status="fail",
            reason_code="INSUFFICIENT_EVIDENCE",
            evidence_ids=_find_supporting_evidence(review_input, {"tax_treatment"}),
            missing_evidence=["tax_supporting_documentation"],
            policy_ids=["POL-EVID-002"],
        )
    return MandatoryCheckResult(
        check_id="tax_treatment_supported",
        status="pass",
        reason_code="none",
        evidence_ids=_find_supporting_evidence(review_input, {"tax_treatment"}),
        missing_evidence=[],
        policy_ids=["POL-EVID-002"],
    )


def _action_scope_check(review_input: Day6ReviewInput) -> MandatoryCheckResult:
    requested_action = (review_input.candidate_recommendation or {}).get("requested_action", "route_to_controller_approval")
    if requested_action in review_input.authority_context.prohibited_actions:
        return MandatoryCheckResult(
            check_id="action_within_system_authority",
            status="fail",
            reason_code="OUT_OF_SCOPE_ACTION",
            evidence_ids=[],
            missing_evidence=[],
            policy_ids=["POL-SCOPE-003"],
        )
    return MandatoryCheckResult(
        check_id="action_within_system_authority",
        status="pass",
        reason_code="none",
        evidence_ids=[],
        missing_evidence=[],
        policy_ids=["POL-SCOPE-003"],
    )


def _claim_has_value(review_input: Day6ReviewInput, claim_type: str, field: str, expected: object) -> bool:
    claim = next((item for item in review_input.claim_ledger if item.claim_type == claim_type), None)
    if claim is None:
        return False
    return claim.metadata.get(field) == expected


def _find_supporting_evidence(review_input: Day6ReviewInput, claim_types: set[str]) -> list[str]:
    evidence_ids: list[str] = []
    for claim in review_input.claim_ledger:
        if claim.claim_type in claim_types:
            evidence_ids.extend(claim.supporting_evidence_ids)
    return list(dict.fromkeys(evidence_ids))


def _evidence_ids_by_source_type(review_input: Day6ReviewInput, source_types: Iterable[str]) -> list[str]:
    accepted = set(source_types)
    return [item.evidence_id for item in review_input.evidence_ledger if item.source_type in accepted]


def _collect_conflict_evidence(review_input: Day6ReviewInput) -> list[str]:
    evidence_ids: list[str] = []
    for claim in review_input.claim_ledger:
        evidence_ids.extend(claim.conflicting_evidence_ids)
    return list(dict.fromkeys(evidence_ids))

