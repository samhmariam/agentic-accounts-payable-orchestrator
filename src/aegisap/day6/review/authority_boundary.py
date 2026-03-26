from __future__ import annotations

from aegisap.day6.state.models import AuthorisationCheck, Day6ReviewInput


def evaluate_authority_boundary(
    review_input: Day6ReviewInput,
    *,
    injection_detected: bool,
) -> AuthorisationCheck:
    approval_claim = next(
        (claim for claim in review_input.claim_ledger if claim.claim_type == "approval_claim"),
        None,
    )
    requested_action = (review_input.candidate_recommendation or {}).get(
        "requested_action",
        "route_to_controller_approval",
    )
    action_prohibited = requested_action in review_input.authority_context.prohibited_actions

    if action_prohibited:
        return AuthorisationCheck(
            required=True,
            present=False,
            approval_channel_valid=False,
            approver_identity_verified=False,
            approved_by=None,
            notes="Requested action is outside the system authority boundary.",
        )

    if approval_claim is None:
        return AuthorisationCheck(
            required=bool(review_input.authority_context.required_approvals),
            present=True,
            approval_channel_valid=not injection_detected,
            approver_identity_verified=not injection_detected,
            approved_by=None,
            notes=(
                "Workflow is authorised to continue to the next control step because no unverified "
                "approval claim is being relied on."
            ),
        )

    channel = str(approval_claim.metadata.get("channel", "")).strip()
    approved_by = approval_claim.metadata.get("approved_by")
    channel_valid = channel in review_input.authority_context.registered_approval_channels
    approver_verified = bool(approval_claim.metadata.get("approver_identity_verified"))
    artifact_found = any(item.source_type == "approval_record" for item in review_input.evidence_ledger)
    present = channel_valid and approver_verified and artifact_found and not injection_detected

    return AuthorisationCheck(
        required=True,
        present=present,
        approval_channel_valid=channel_valid,
        approver_identity_verified=approver_verified,
        approved_by=str(approved_by) if approved_by else None,
        notes=(
            "Approval claim is backed by a registered channel."
            if present
            else "Approval claim could not be verified in a registered channel."
        ),
    )

