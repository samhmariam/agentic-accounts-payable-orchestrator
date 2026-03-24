from __future__ import annotations

from ..state.handoff_models import DecisionRecommendation, POMatchFinding, VendorRiskFinding


def synthesize_decision(
    *,
    vendor_risk: VendorRiskFinding,
    po_match: POMatchFinding,
) -> DecisionRecommendation:
    combined_evidence = list(dict.fromkeys(vendor_risk.evidence_ids + po_match.evidence_ids))

    if vendor_risk.status == "review":
        return DecisionRecommendation(
            recommendation="manual_review",
            rationale=(
                "Vendor risk check found a bank validation issue or missing authoritative evidence. "
                "Do not auto-approve until the approved bank account is confirmed."
            ),
            evidence_ids=combined_evidence,
            confidence=0.95,
            next_step="hold_case_for_ap_review",
            policy_notes=[
                "Current system-of-record vendor data outranks stale emails or onboarding messages."
            ],
        )

    if po_match.status in {"review", "missing_po"}:
        return DecisionRecommendation(
            recommendation="manual_review",
            rationale=(
                "Vendor risk passed, but the PO control did not fully pass. "
                "The case should not auto-approve until PO alignment is resolved."
            ),
            evidence_ids=combined_evidence,
            confidence=0.91,
            next_step="route_to_po_exception_queue",
            policy_notes=["Structured PO and goods receipt evidence control the match decision."],
        )

    return DecisionRecommendation(
        recommendation="approve",
        rationale=(
            "Vendor bank details align with current authoritative records, "
            "and the invoice matches the approved PO and receiving evidence."
        ),
        evidence_ids=combined_evidence,
        confidence=0.94,
        next_step="approve_for_payment",
        policy_notes=[
            "Tier 1 structured records outranks stale Tier 3 email evidence during synthesis."
        ],
    )
