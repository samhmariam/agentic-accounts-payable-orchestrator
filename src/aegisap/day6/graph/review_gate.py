from __future__ import annotations

from aegisap.day4.state.workflow_state import WorkflowState as Day4WorkflowState
from aegisap.day6.review.authority_boundary import evaluate_authority_boundary
from aegisap.day6.review.decision_mapping import map_review_outcome
from aegisap.day6.review.evidence_sufficiency import evaluate_evidence_sufficiency
from aegisap.day6.review.prompt_injection import detect_prompt_injection
from aegisap.day6.review.reflection import build_reflection_review
from aegisap.day6.state.day4_handoff import build_day6_review_input_from_day4
from aegisap.day6.state.models import Day6ReviewInput, ReviewOutcome
from aegisap.observability.context import WorkflowObservabilityContext
from aegisap.observability.langsmith_bridge import publish_langsmith_run
from aegisap.observability.tracing import add_span_event, node_span_attributes, set_span_attributes, start_observability_span


def run_day6_review(review_input: Day6ReviewInput) -> ReviewOutcome:
    with start_observability_span(
        "aegis.workflow.day6.review",
        attributes=node_span_attributes(
            node_name="policy_tax_compliance_review",
            idempotent=True,
            evidence_count=len(review_input.evidence_ledger),
            prompt_revision=review_input.policy_context.policy_version,
            model_name="rule_based_day6_review",
        ),
    ):
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
        outcome = map_review_outcome(
            review_input,
            evidence_assessment=evidence_assessment,
            authorisation_check=authorisation_check,
            injection_signals=injection_signals,
            reflection_review=reflection_review,
        )
        set_span_attributes(
            {
                "aegis.policy_version": outcome.model_trace.policy_version,
                "aegis.outcome_type": outcome.outcome,
                "aegis.approval_status": "not_requested",
            }
        )
        if outcome.outcome == "needs_human_review":
            add_span_event(
                "human_review_escalated",
                {
                    "error_class": "manual_review_required",
                    "attempt_number": 1,
                    "backoff_ms": 0,
                    "remaining_budget_ms": 0,
                    "dependency_name": "day6_review",
                    "decision_reason_code": "NEEDS_HUMAN_REVIEW",
                },
            )
        if outcome.outcome == "not_authorised_to_continue":
            add_span_event(
                "policy_refusal",
                {
                    "error_class": "policy_refusal",
                    "attempt_number": 1,
                    "backoff_ms": 0,
                    "remaining_budget_ms": 0,
                    "dependency_name": "day6_review",
                    "decision_reason_code": outcome.reasons[0].code if outcome.reasons else None,
                },
            )
        return outcome


def run_day6_review_from_day4(
    day4_state: Day4WorkflowState,
    *,
    thread_id: str,
    observability_context: WorkflowObservabilityContext | None = None,
) -> tuple[Day6ReviewInput, ReviewOutcome]:
    review_input = build_day6_review_input_from_day4(day4_state, thread_id=thread_id)
    outcome = run_day6_review(review_input)
    if observability_context is not None:
        publish_langsmith_run(
            context=observability_context,
            name="aegis.workflow.day6.review",
            run_type="chain",
            inputs={"thread_id_hash": observability_context.hashed_thread_id},
            outputs={"outcome": outcome.outcome, "reason_count": len(outcome.reasons)},
            tags=["day6", "review"],
        )
    return review_input, outcome
