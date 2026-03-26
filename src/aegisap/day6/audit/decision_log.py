from __future__ import annotations

from aegisap.day6.state.models import ReviewOutcome


def build_operator_summary(review: ReviewOutcome) -> str:
    reasons = "; ".join(reason.message for reason in review.reasons[:2])
    if review.outcome == "approved_to_proceed":
        return "Automated progression allowed. Mandatory Day 6 checks passed."
    if review.outcome == "needs_human_review":
        return (
            "Automated progression paused for human review. "
            f"Outstanding issues: {reasons or 'missing or conflicting evidence.'}"
        )
    return (
        "Automated progression stopped. "
        f"{reasons or 'The case violated a policy or authority boundary.'}"
    )
