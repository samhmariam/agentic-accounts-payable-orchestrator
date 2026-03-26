from __future__ import annotations

from aegisap.day6.policy.registry import POLICY_VERSION, PROMPT_VERSION, REVIEWER_MODEL
from aegisap.day6.state.models import (
    AuthorisationCheck,
    Day6ReviewInput,
    EvidenceAssessment,
    EvidenceCitation,
    InjectionSignal,
    NextAction,
    ReflectionReview,
    ReviewOutcome,
    ReviewReason,
)


def map_review_outcome(
    review_input: Day6ReviewInput,
    *,
    evidence_assessment: EvidenceAssessment,
    authorisation_check: AuthorisationCheck,
    injection_signals: list[InjectionSignal],
    reflection_review: ReflectionReview,
) -> ReviewOutcome:
    reasons: list[ReviewReason] = []
    citations: list[EvidenceCitation] = []

    for signal in injection_signals:
        code = (
            "UNVERIFIED_APPROVAL_CLAIM"
            if signal.signal == "confirmed by phone"
            else "PROMPT_INJECTION_ATTEMPT"
        )
        if signal.signal in {"ignore prior rules", "do not escalate"}:
            code = "UNTRUSTED_OVERRIDE_REQUEST"
        reasons.append(
            ReviewReason(
                code=code,
                severity="high" if code != "UNVERIFIED_APPROVAL_CLAIM" else "high",
                message=_message_for_signal(signal.signal),
                evidence_ids=[signal.evidence_id],
                policy_ids=["POL-CTRL-001", "POL-AUTH-004"],
            )
        )
        citations.extend(_citations_for(review_input, [signal.evidence_id]))

    for check in evidence_assessment.mandatory_checks:
        if check.status != "fail":
            continue
        if check.reason_code in {"PROMPT_INJECTION_ATTEMPT", "none"}:
            continue
        reasons.append(
            ReviewReason(
                code=check.reason_code,  # type: ignore[arg-type]
                severity="medium" if check.reason_code == "INSUFFICIENT_EVIDENCE" else "high",
                message=_message_for_check(check.check_id, check.reason_code),
                evidence_ids=check.evidence_ids,
                policy_ids=check.policy_ids,
            )
        )
        citations.extend(_citations_for(review_input, check.evidence_ids))

    if not authorisation_check.present:
        reasons.append(
            ReviewReason(
                code=(
                    "OUT_OF_SCOPE_ACTION"
                    if not authorisation_check.approval_channel_valid and "outside" in authorisation_check.notes.lower()
                    else "MISSING_AUTHORITY"
                ),
                severity="high",
                message=authorisation_check.notes,
                evidence_ids=_approval_claim_evidence(review_input),
                policy_ids=["POL-AUTH-004", "POL-SCOPE-003"],
            )
        )
        citations.extend(_citations_for(review_input, _approval_claim_evidence(review_input)))

    unique_reasons = _dedupe_reasons(reasons)
    unique_citations = _dedupe_citations(citations)
    outcome = reflection_review.recommended_outcome
    next_actions = _build_next_actions(outcome)
    summary = _build_summary(outcome, unique_reasons, review_input)

    return ReviewOutcome(
        case_id=review_input.case_id,
        thread_id=review_input.thread_id,
        outcome=outcome,
        decision_summary=summary,
        reasons=unique_reasons,
        citations=unique_citations,
        authorisation_check=authorisation_check,
        evidence_assessment=evidence_assessment,
        next_actions=next_actions,
        model_trace={
            "prompt_version": PROMPT_VERSION,
            "policy_version": POLICY_VERSION,
            "reviewer_model": REVIEWER_MODEL,
        },
    )


def _approval_claim_evidence(review_input: Day6ReviewInput) -> list[str]:
    claim = next((item for item in review_input.claim_ledger if item.claim_type == "approval_claim"), None)
    if claim is None:
        return []
    return claim.supporting_evidence_ids


def _citations_for(review_input: Day6ReviewInput, evidence_ids: list[str]) -> list[EvidenceCitation]:
    by_id = {item.evidence_id: item for item in review_input.evidence_ledger}
    citations: list[EvidenceCitation] = []
    for evidence_id in evidence_ids:
        evidence = by_id.get(evidence_id)
        if evidence is None:
            continue
        citations.append(
            EvidenceCitation(
                evidence_id=evidence.evidence_id,
                source_type=evidence.source_type,
                excerpt=evidence.extract,
            )
        )
    return citations


def _build_next_actions(outcome: str) -> list[NextAction]:
    if outcome == "approved_to_proceed":
        return [
            NextAction(
                action="Continue to the next governed workflow step.",
                owner="system",
                blocking=False,
            )
        ]
    if outcome == "needs_human_review":
        return [
            NextAction(
                action="Pause the thread and request human review with the missing requirements.",
                owner="operator",
                blocking=True,
            )
        ]
    return [
        NextAction(
            action="Stop automated progression and route the case to the Finance Controller.",
            owner="finance_controller",
            blocking=True,
        )
    ]


def _build_summary(outcome: str, reasons: list[ReviewReason], review_input: Day6ReviewInput) -> str:
    if outcome == "approved_to_proceed":
        return (
            "Automated progression may continue because mandatory evidence checks passed and "
            "the workflow remains inside policy and authority boundaries."
        )
    if outcome == "needs_human_review":
        return (
            "Automated progression paused because the case may still be valid but missing or "
            "conflicting evidence requires a human decision."
        )
    top_reason = reasons[0].message if reasons else "policy review detected an unsafe continuation path"
    return (
        "Automated progression stopped because "
        f"{top_reason.lower()} for case {review_input.case_id}."
    )


def _message_for_signal(signal: str) -> str:
    mapping = {
        "ignore prior rules": "Email contains override language instructing the workflow to ignore prior rules.",
        "approve urgently": "Case material attempts to rush approval outside the governed workflow.",
        "skip review": "Case material attempts to skip a mandatory review step.",
        "bypass": "Case material attempts to bypass established controls.",
        "do not escalate": "Case material attempts to prevent a required escalation path.",
        "just process this now": "Case material attempts to trigger immediate processing without policy checks.",
        "confirmed by phone": "Claim of approval by phone is not an authorised approval artifact.",
    }
    return mapping.get(signal, f"Case material includes unsafe override language: {signal}.")


def _message_for_check(check_id: str, reason_code: str) -> str:
    if reason_code == "CONTRADICTORY_EVIDENCE":
        return f"Mandatory check '{check_id}' found contradictory evidence that blocks automated progression."
    if reason_code == "MISSING_AUTHORITY":
        return f"Mandatory check '{check_id}' could not verify the required approval path."
    if reason_code == "OUT_OF_SCOPE_ACTION":
        return f"Mandatory check '{check_id}' found a requested action outside the system authority boundary."
    return f"Mandatory check '{check_id}' failed because required evidence was missing or incomplete."


def _dedupe_reasons(reasons: list[ReviewReason]) -> list[ReviewReason]:
    unique: dict[tuple[str, str], ReviewReason] = {}
    for reason in reasons:
        unique[(reason.code, reason.message)] = reason
    return list(unique.values())


def _dedupe_citations(citations: list[EvidenceCitation]) -> list[EvidenceCitation]:
    unique: dict[str, EvidenceCitation] = {}
    for citation in citations:
        unique[citation.evidence_id] = citation
    return list(unique.values())

