from __future__ import annotations

from datetime import datetime, timezone

from aegisap.day4.planning.plan_types import PlanTask
from aegisap.day4.state.workflow_state import WorkflowState as Day4WorkflowState
from aegisap.day5.state.checksum import compute_payload_checksum
from aegisap.day6.policy.registry import build_policy_context
from aegisap.day6.state.models import (
    AuthorityContext,
    ClaimLedgerItem,
    Day6ReviewInput,
    EvidenceLedgerItem,
)


def build_day6_review_input_from_day4(
    day4_state: Day4WorkflowState,
    *,
    thread_id: str,
) -> Day6ReviewInput:
    plan = day4_state.plan
    if plan is None:
        raise ValueError("Day 6 review requires a validated Day 4 plan.")

    evidence_ledger = _build_evidence_ledger(day4_state)
    return Day6ReviewInput(
        case_id=day4_state.case_facts.case_id,
        thread_id=thread_id,
        candidate_recommendation=day4_state.recommendation,
        escalation_package=day4_state.escalation_package,
        evidence_ledger=evidence_ledger,
        claim_ledger=_build_claim_ledger(day4_state),
        policy_context=build_policy_context(day4_state),
        authority_context=AuthorityContext(
            required_approvals=day4_state.eligibility.required_approvals[:],
            registered_approval_channels=[
                "erp_approval_record",
                "controller_queue",
                "ap_manager_queue",
            ],
            allowed_actions=[
                "route_to_controller_approval",
                "request_manual_review",
                "publish_payment_recommendation",
            ],
            prohibited_actions=[
                "execute_payment",
                "override_policy",
                "skip_approval_checks",
            ],
        ),
        missing_requirements=list(
            dict.fromkeys(
                day4_state.eligibility.missing_evidence + day4_state.eligibility.unmet_preconditions
            )
        ),
        conflict_flags=list(dict.fromkeys(day4_state.eligibility.blocking_conditions)),
        review_metadata={
            "source": "day4_handoff",
            "plan_id": plan.plan_id,
            "recommendation_gate_reasons": (
                day4_state.recommendation_gate_result.reasons
                if day4_state.recommendation_gate_result is not None
                else []
            ),
        },
    )


def _build_evidence_ledger(day4_state: Day4WorkflowState) -> list[EvidenceLedgerItem]:
    now = datetime.now(timezone.utc).isoformat()
    evidence_items: list[EvidenceLedgerItem] = [
        EvidenceLedgerItem(
            evidence_id=f"case_facts:{day4_state.case_facts.case_id}",
            source_type="case_summary",
            source_ref="day4.case_facts",
            trust_tier="derived",
            timestamp=now,
            extract=(
                f"Case {day4_state.case_facts.case_id} for invoice {day4_state.case_facts.invoice_id} "
                f"and supplier {day4_state.case_facts.supplier_id}."
            ),
            payload_hash=compute_payload_checksum(day4_state.case_facts.model_dump(mode="json")),
            derived_claim_ids=[
                "claim_invoice_identity",
                "claim_supplier_identity",
            ],
        )
    ]

    for evidence_id in day4_state.retrieved_evidence:
        source_type, trust_tier = _classify_retrieved_evidence(evidence_id)
        evidence_items.append(
            EvidenceLedgerItem(
                evidence_id=evidence_id,
                source_type=source_type,
                source_ref=evidence_id,
                trust_tier=trust_tier,
                timestamp=now,
                extract=_default_extract_for_evidence(evidence_id),
                payload_hash=compute_payload_checksum({"evidence_id": evidence_id}),
                derived_claim_ids=[],
            )
        )

    tasks_by_id = {
        task.task_id: task
        for task in (day4_state.plan.tasks if day4_state.plan is not None else [])
    }
    for entry in day4_state.task_ledger:
        artifact = day4_state.artifacts.get(entry.task_id, {})
        payload = {
            "task_type": entry.task_type,
            "status": entry.status,
            "outputs": entry.outputs or {},
            "artifact": artifact,
            "required_evidence": _task_required_evidence(tasks_by_id.get(entry.task_id)),
        }
        evidence_items.append(
            EvidenceLedgerItem(
                evidence_id=f"task:{entry.task_id}",
                source_type="tool_artifact",
                source_ref=entry.task_id,
                trust_tier="derived",
                timestamp=entry.completed_at or entry.started_at or now,
                extract=_task_extract(entry.task_type, entry.outputs or {}),
                payload_hash=compute_payload_checksum(payload),
                derived_claim_ids=[f"claim:{entry.task_type}"],
            )
        )

    return evidence_items


def _build_claim_ledger(day4_state: Day4WorkflowState) -> list[ClaimLedgerItem]:
    claims = [
        ClaimLedgerItem(
            claim_id="claim_invoice_identity",
            claim_type="invoice_identity_verified",
            summary=f"Invoice {day4_state.case_facts.invoice_id} is the target case record.",
            supporting_evidence_ids=[f"case_facts:{day4_state.case_facts.case_id}"],
        ),
        ClaimLedgerItem(
            claim_id="claim_supplier_identity",
            claim_type="supplier_identity_verified",
            summary=f"Supplier {day4_state.case_facts.supplier_id} is the target supplier.",
            supporting_evidence_ids=[f"case_facts:{day4_state.case_facts.case_id}"],
        ),
    ]

    for entry in day4_state.task_ledger:
        outputs = entry.outputs or {}
        claims.append(
            ClaimLedgerItem(
                claim_id=f"claim:{entry.task_type}",
                claim_type=entry.task_type,
                summary=_task_extract(entry.task_type, outputs),
                supporting_evidence_ids=[f"task:{entry.task_id}"],
                conflicting_evidence_ids=[],
                requires_authority=entry.task_type == "threshold_approval_check",
                metadata=outputs,
            )
        )

    if day4_state.recommendation is not None:
        claims.append(
            ClaimLedgerItem(
                claim_id="claim_candidate_recommendation",
                claim_type="candidate_recommendation",
                summary="Day 4 produced a candidate payment recommendation ready for downstream control review.",
                supporting_evidence_ids=[
                    f"task:{entry.task_id}"
                    for entry in day4_state.task_ledger
                    if entry.status == "completed"
                ],
            )
        )
    if day4_state.escalation_package is not None:
        claims.append(
            ClaimLedgerItem(
                claim_id="claim_manual_review_required",
                claim_type="manual_review_required",
                summary="Day 4 produced a manual review package because the recommendation gate did not pass.",
                supporting_evidence_ids=[
                    f"task:{entry.task_id}"
                    for entry in day4_state.task_ledger
                    if entry.status in {"blocked", "escalated", "completed"}
                ],
            )
        )
    return claims


def _classify_retrieved_evidence(evidence_id: str) -> tuple[str, str]:
    if evidence_id.startswith("policy:"):
        return "policy_doc", "policy"
    if evidence_id.startswith("supplier_master:"):
        return "vendor_master", "authoritative"
    if evidence_id.startswith(("erp:", "po-", "gr-")):
        return "erp_record", "authoritative"
    if evidence_id.startswith("email:"):
        return "email", "untrusted"
    if evidence_id.startswith("approved_bank_change:"):
        return "approval_record", "authoritative"
    return "retrieval_note", "derived"


def _default_extract_for_evidence(evidence_id: str) -> str:
    if evidence_id.startswith("email:"):
        return f"Case email evidence referenced as {evidence_id}."
    if evidence_id.startswith("policy:"):
        return f"Policy reference captured as {evidence_id}."
    if evidence_id.startswith("supplier_master:"):
        return f"Supplier master record linked as {evidence_id}."
    return f"Retrieved evidence referenced as {evidence_id}."


def _task_extract(task_type: str, outputs: dict[str, object]) -> str:
    if task_type == "po_match_verification":
        return f"PO verification returned status={outputs.get('po_match_status')}."
    if task_type == "po_waiver_check":
        return f"PO waiver presence={outputs.get('waiver_present')} authority={outputs.get('waiver_authority')}."
    if task_type == "vendor_bank_verification":
        return f"Bank change verified={outputs.get('bank_change_verified')}."
    if task_type == "threshold_approval_check":
        return (
            "Approval route defined="
            f"{outputs.get('approval_path_defined')} required_approvals={outputs.get('required_approvals')}."
        )
    if task_type == "payment_recommendation_draft":
        return "Candidate payment recommendation draft assembled."
    if task_type == "manual_escalation_package":
        return "Manual escalation package assembled from blocking conditions."
    return f"{task_type} completed with outputs {outputs}."


def _task_required_evidence(task: PlanTask | None) -> list[str]:
    if task is None:
        return []
    return task.required_evidence[:]

