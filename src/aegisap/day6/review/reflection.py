from __future__ import annotations

from aegisap.day6.state.models import (
    AuthorisationCheck,
    Day6ReviewInput,
    EvidenceAssessment,
    InjectionSignal,
    ReflectionReview,
)


def build_reflection_review(
    review_input: Day6ReviewInput,
    *,
    evidence_assessment: EvidenceAssessment,
    authorisation_check: AuthorisationCheck,
    injection_signals: list[InjectionSignal],
) -> ReflectionReview:
    unresolved_conflicts = list(dict.fromkeys(review_input.conflict_flags))
    override_signals = [signal.signal for signal in injection_signals]

    if injection_signals or not authorisation_check.present:
        recommended_outcome = "not_authorised_to_continue"
        rationale = (
            "Automated progression is unsafe because the case attempts to bypass policy "
            "or relies on missing authority."
        )
    elif evidence_assessment.sufficiency == "conflicting":
        recommended_outcome = "needs_human_review"
        rationale = "Contradictory evidence must be resolved by a human reviewer."
    elif evidence_assessment.sufficiency == "insufficient":
        recommended_outcome = "needs_human_review"
        rationale = "Evidence is incomplete for an automated decision but the case may still be legitimate."
    else:
        recommended_outcome = "approved_to_proceed"
        rationale = "Mandatory controls passed and the workflow can continue to the next governed step."

    return ReflectionReview(
        required_claims=[
            "invoice_identity_verified",
            "supplier_identity_verified",
            "approval_route_defined",
            "action_within_system_authority",
        ],
        unresolved_conflicts=unresolved_conflicts,
        override_signals=override_signals,
        recommended_outcome=recommended_outcome,
        rationale=rationale,
    )

