from __future__ import annotations

from aegisap.day4.state.workflow_state import WorkflowState as Day4WorkflowState
from aegisap.day6.review.authority_boundary import evaluate_authority_boundary
from aegisap.day6.review.decision_mapping import map_review_outcome
from aegisap.day6.review.evidence_sufficiency import evaluate_evidence_sufficiency
from aegisap.day6.review.prompt_injection import detect_prompt_injection
from aegisap.day6.review.reflection import build_reflection_review
from aegisap.day6.state.day4_handoff import build_day6_review_input_from_day4
from aegisap.day6.state.models import Day6ReviewInput, ReviewOutcome


def run_day6_review(review_input: Day6ReviewInput) -> ReviewOutcome:
    injection_signals = detect_prompt_injection(review_input)
    conflicting_claims = [
        claim.claim_id
        for claim in review_input.claim_ledger
        if claim.conflicting_evidence_ids
    ]
    evidence_assessment = evaluate_evidence_sufficiency(
        review_input,
        injection_detected=bool(injection_signals),
        conflicting_claims=conflicting_claims,
    )
    authorisation_check = evaluate_authority_boundary(
        review_input,
        injection_detected=bool(injection_signals),
    )
    reflection_review = build_reflection_review(
        review_input,
        evidence_assessment=evidence_assessment,
        authorisation_check=authorisation_check,
        injection_signals=injection_signals,
    )
    return map_review_outcome(
        review_input,
        evidence_assessment=evidence_assessment,
        authorisation_check=authorisation_check,
        injection_signals=injection_signals,
        reflection_review=reflection_review,
    )


def run_day6_review_from_day4(
    day4_state: Day4WorkflowState,
    *,
    thread_id: str,
) -> tuple[Day6ReviewInput, ReviewOutcome]:
    review_input = build_day6_review_input_from_day4(day4_state, thread_id=thread_id)
    return review_input, run_day6_review(review_input)

