from __future__ import annotations

from aegisap.common.clocks import utc_now_iso
from aegisap.day2.idempotency import ensure_action_once
from aegisap.day2.router import apply_route_decision, decide_route
from aegisap.day2.state import WorkflowState
from aegisap.day2.tracing import traced_node
from aegisap.domain.evidence import ActionRecommendation, EvidenceItem


@traced_node("init_workflow")
def init_workflow(state: WorkflowState) -> WorkflowState:
    state.current_node = "init_workflow"
    state.status = "initialized"
    state.evidence.append(
        EvidenceItem(
            kind="workflow_initialized",
            source="init_workflow",
            detail="workflow state initialized from canonical Day 1 invoice",
            value=state.invoice_id,
            node_name="init_workflow",
            recorded_at=utc_now_iso(),
        )
    )
    state.completed_nodes.append("init_workflow")
    return state


@traced_node("route_invoice")
def route_invoice(state: WorkflowState) -> WorkflowState:
    state.current_node = "route_invoice"
    decision = decide_route(state)
    apply_route_decision(state, decision)
    state.completed_nodes.append("route_invoice")
    return state


@traced_node("high_value_review")
def high_value_review(state: WorkflowState) -> WorkflowState:
    state.current_node = "high_value_review"
    state.status = "in_review"
    state.evidence.append(
        EvidenceItem(
            kind="threshold_check",
            source="high_value_review",
            detail="invoice gross amount breached high value control threshold",
            value={
                "gross_amount": str(state.invoice.gross_amount),
                "threshold": str(state.policy.high_value_threshold),
            },
            node_name="high_value_review",
            recorded_at=utc_now_iso(),
        )
    )
    if ensure_action_once(state, "high_value_review", "manager_approval_required"):
        state.recommendations.append(
            ActionRecommendation(
                action="manager_approval_required",
                reason="invoice exceeds finance materiality threshold",
                owner="finance_manager",
            )
        )
    state.completed_nodes.append("high_value_review")
    return state


@traced_node("new_vendor_review")
def new_vendor_review(state: WorkflowState) -> WorkflowState:
    state.current_node = "new_vendor_review"
    state.status = "in_review"
    verification_evidence = EvidenceItem(
        kind="vendor_lookup",
        source="approved_vendor_registry",
        detail="vendor not found in registry for this workflow thread",
        value=False,
        node_name="new_vendor_review",
        recorded_at=utc_now_iso(),
    )
    state.vendor.verification.verified = False
    state.vendor.verification.source = "approved_vendor_registry"
    state.vendor.verification.checked_at = verification_evidence.recorded_at
    state.vendor.verification.evidence.append(verification_evidence)
    state.evidence.append(verification_evidence)
    if ensure_action_once(state, "new_vendor_review", "run_vendor_verification"):
        state.recommendations.append(
            ActionRecommendation(
                action="run_vendor_verification",
                reason="vendor is not yet approved in master registry",
                owner="vendor_management",
            )
        )
    state.completed_nodes.append("new_vendor_review")
    return state


@traced_node("clean_path_finalize")
def clean_path_finalize(state: WorkflowState) -> WorkflowState:
    state.current_node = "clean_path_finalize"
    state.status = "completed"
    state.evidence.append(
        EvidenceItem(
            kind="clean_path",
            source="clean_path_finalize",
            detail="invoice cleared deterministic routing checks",
            value=True,
            node_name="clean_path_finalize",
            recorded_at=utc_now_iso(),
        )
    )
    state.completed_nodes.append("clean_path_finalize")
    return state


@traced_node("finalize_workflow")
def finalize_workflow(state: WorkflowState) -> WorkflowState:
    state.current_node = "finalize_workflow"
    if state.status != "completed":
        state.status = "in_review"
    state.run_notes.append(
        f"route={state.route}; status={state.status}; recommendations={len(state.recommendations)}"
    )
    state.evidence.append(
        EvidenceItem(
            kind="workflow_finalized",
            source="finalize_workflow",
            detail="workflow finalized with aggregate metrics and recommendations",
            value={
                "total_latency_ms": state.total_latency_ms,
                "total_cost_usd": round(state.total_cost_usd, 6),
            },
            node_name="finalize_workflow",
            recorded_at=utc_now_iso(),
        )
    )
    state.completed_nodes.append("finalize_workflow")
    return state
