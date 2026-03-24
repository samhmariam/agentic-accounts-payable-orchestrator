from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .agents.decision_synthesizer import synthesize_decision
from .agents.po_match_agent import verify_po_match
from .agents.vendor_risk_verifier import verify_vendor_risk
from .evaluation.scorecard import score_case
from .retrieval.authority_policy import load_authority_policy
from .retrieval.azure_ai_search_adapter import build_unstructured_retriever
from .retrieval.interfaces import RetrievalConfig, build_retrieval_config
from .retrieval.ranker import apply_authority_ranking
from .retrieval.structured_po_lookup import StructuredPOLookup
from .retrieval.structured_vendor_lookup import StructuredVendorLookup
from .state.workflow_state import WorkflowState, make_initial_state


def _policy_path() -> Path:
    return Path(__file__).resolve().parent / "policies" / "source_authority_rules.yaml"


def _invoice_date(invoice: dict[str, Any]) -> date:
    return date.fromisoformat(invoice.get("invoice_date", date.today().isoformat()))


def _serialize_dataclass(value: Any) -> dict[str, Any]:
    if is_dataclass(value):
        return asdict(value)
    return {"value": str(value)}


def intake_router(state: WorkflowState) -> WorkflowState:
    state.enter_node("intake_router")
    vendor_check_required = any(
        state.invoice.get(key) for key in ("vendor_id", "vendor_name", "bank_account_last4")
    )
    po_check_required = True
    state.record_telemetry(
        "intake_router",
        vendor_check_required=int(vendor_check_required),
        po_check_required=int(po_check_required),
    )
    state.status = "routing"
    return state


def retrieve_vendor_context(
    state: WorkflowState,
    *,
    policy: dict[str, Any],
    retrieval_config: RetrievalConfig,
) -> WorkflowState:
    state.enter_node("retrieve_vendor_context")
    invoice = state.invoice
    today = _invoice_date(invoice)

    vendor_lookup = StructuredVendorLookup()
    unstructured = build_unstructured_retriever(retrieval_config)

    vendor_structured = vendor_lookup.search(
        vendor_id=invoice.get("vendor_id"),
        vendor_name=invoice.get("vendor_name"),
    )
    vendor_unstructured = unstructured.search(
        query=f'{invoice.get("vendor_name", "")} bank change {invoice.get("bank_account_last4", "")}',
        max_results=retrieval_config.max_results,
    )
    policy_evidence = unstructured.search(
        query="AP policy bank change vendor master system of record",
        max_results=retrieval_config.max_results,
    )

    vendor_evidence = apply_authority_ranking(
        vendor_structured + vendor_unstructured,
        policy=policy,
        query_terms={
            "vendor_id": invoice.get("vendor_id"),
            "vendor_name": invoice.get("vendor_name"),
            "bank_account_last4": invoice.get("bank_account_last4"),
        },
        today=today,
        recency_mode="mutable_fact",
    )
    policy_ranked = apply_authority_ranking(
        policy_evidence,
        policy=policy,
        query_terms={"vendor_id": invoice.get("vendor_id")},
        today=today,
        recency_mode="policy",
    )

    state.add_evidence("vendor", vendor_evidence)
    state.add_evidence("policy", policy_ranked)
    state.record_telemetry(
        "retrieve_vendor_context",
        vendor_count=len(vendor_evidence),
        policy_count=len(policy_ranked),
        backend=retrieval_config.mode,
    )
    return state


def vendor_risk_verifier(state: WorkflowState) -> WorkflowState:
    state.enter_node("vendor_risk_verifier")
    finding = verify_vendor_risk(state.invoice, state.bucket("vendor", "policy"))
    state.record_agent_finding("vendor_risk", finding)
    state.record_telemetry(
        "vendor_risk_verifier",
        status=finding.status,
        evidence_count=len(finding.evidence_ids),
    )
    return state


def retrieve_po_context(state: WorkflowState, *, policy: dict[str, Any]) -> WorkflowState:
    state.enter_node("retrieve_po_context")
    po_lookup = StructuredPOLookup()
    po_evidence = po_lookup.search(po_number=state.invoice.get("po_number"))
    po_ranked = apply_authority_ranking(
        po_evidence,
        policy=policy,
        query_terms={
            "po_number": state.invoice.get("po_number"),
            "vendor_id": state.invoice.get("vendor_id"),
        },
        today=_invoice_date(state.invoice),
        recency_mode="reference",
    )
    state.add_evidence("po", po_ranked)
    state.record_telemetry("retrieve_po_context", po_count=len(po_ranked))
    return state


def po_match_agent(state: WorkflowState) -> WorkflowState:
    state.enter_node("po_match_agent")
    finding = verify_po_match(state.invoice, state.bucket("po"))
    state.record_agent_finding("po_match", finding)
    state.record_telemetry(
        "po_match_agent",
        status=finding.status,
        evidence_count=len(finding.evidence_ids),
    )
    return state


def decision_synthesizer(state: WorkflowState) -> WorkflowState:
    state.enter_node("decision_synthesizer")
    finding = synthesize_decision(
        vendor_risk=state.agent_findings["vendor_risk"],
        po_match=state.agent_findings["po_match"],
    )
    state.record_agent_finding("decision", finding)
    state.record_telemetry(
        "decision_synthesizer",
        recommendation=finding.recommendation,
        next_step=finding.next_step,
    )
    return state


def evaluation_scoring(state: WorkflowState) -> WorkflowState:
    state.enter_node("evaluation_scoring")
    state.eval_scores = score_case(state)
    state.record_telemetry(
        "evaluation_scoring",
        **{key: value for key, value in state.eval_scores.items() if key != "notes"},
    )
    return state


def finalize_case(state: WorkflowState) -> WorkflowState:
    state.enter_node("finalize_case")
    decision = state.agent_findings["decision"]
    state.branch_history.append(decision.next_step)
    state.status = "completed"
    state.last_updated_at = state.last_updated_at
    state.record_telemetry(
        "finalize_case",
        status=state.status,
        finding_count=len(state.agent_findings),
    )
    return state


def run_day3_workflow(
    invoice: dict[str, Any],
    *,
    retrieval_mode: str = "fixture",
    retrieval_config: RetrievalConfig | None = None,
) -> WorkflowState:
    state = make_initial_state(invoice)
    policy = load_authority_policy(_policy_path())
    resolved_config = retrieval_config or build_retrieval_config(retrieval_mode)

    for node in (
        intake_router,
        lambda current: retrieve_vendor_context(current, policy=policy, retrieval_config=resolved_config),
        vendor_risk_verifier,
        lambda current: retrieve_po_context(current, policy=policy),
        po_match_agent,
        decision_synthesizer,
        evaluation_scoring,
        finalize_case,
    ):
        state = node(state)

    state.record_telemetry(
        "summary",
        workflow_id=state.workflow_id,
        evidence_count=len(state.evidence_registry),
        findings=_serialize_dataclass(state.agent_findings["decision"])["recommendation"],
    )
    return state
