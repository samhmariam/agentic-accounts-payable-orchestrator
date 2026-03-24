from __future__ import annotations

from ..state.evidence_models import EvidenceItem
from ..state.handoff_models import POMatchFinding


def verify_po_match(invoice: dict, evidence_items: list[EvidenceItem]) -> POMatchFinding:
    agent_name = "po_match_agent"
    for item in evidence_items:
        item.mark_used_by(agent_name)

    po_item = next((item for item in evidence_items if item.source_type == "po_table"), None)
    gr_item = next((item for item in evidence_items if item.source_type == "goods_receipt"), None)

    if not invoice.get("po_number"):
        return POMatchFinding(
            status="missing_po",
            risk_level="medium",
            key_findings=["Invoice does not contain a PO number."],
            evidence_ids=[],
            recommended_action="route_to_missing_po_branch",
            confidence=0.95,
            open_questions=["Was this invoice legitimately non-PO under policy?"],
        )

    if po_item is None:
        return POMatchFinding(
            status="review",
            risk_level="high",
            key_findings=[f'No PO record was found for {invoice["po_number"]}.'],
            evidence_ids=[],
            recommended_action="hold_for_po_validation",
            confidence=0.9,
            open_questions=["Confirm whether the PO exists in the ERP system."],
        )

    evidence_ids = [po_item.evidence_id]
    po_vendor_id = po_item.metadata["vendor_id"]
    po_amount = float(po_item.metadata["amount"])
    invoice_amount = float(invoice["amount"])
    variance_amount = round(invoice_amount - po_amount, 2)

    key_findings = [
        f'PO {po_item.metadata["po_number"]} exists for vendor {po_vendor_id}.',
        f"Invoice amount variance versus PO is {variance_amount}.",
    ]

    if gr_item is not None:
        evidence_ids.append(gr_item.evidence_id)
        key_findings.append(
            f'Goods receipt indicates all_received={gr_item.metadata["all_received"]}.'
        )

    if invoice["vendor_id"] != po_vendor_id:
        key_findings.append("Invoice vendor_id does not match the vendor on the PO.")
        return POMatchFinding(
            status="review",
            risk_level="high",
            key_findings=key_findings,
            evidence_ids=evidence_ids,
            recommended_action="hold_for_po_vendor_mismatch",
            confidence=0.96,
            variance_amount=variance_amount,
        )

    if abs(variance_amount) > 0.01:
        key_findings.append("Invoice amount does not match the PO amount.")
        return POMatchFinding(
            status="review",
            risk_level="medium",
            key_findings=key_findings,
            evidence_ids=evidence_ids,
            recommended_action="review_amount_variance",
            confidence=0.88,
            variance_amount=variance_amount,
        )

    if gr_item is not None and str(gr_item.metadata["all_received"]).lower() != "true":
        key_findings.append("Goods receipt is incomplete.")
        return POMatchFinding(
            status="review",
            risk_level="medium",
            key_findings=key_findings,
            evidence_ids=evidence_ids,
            recommended_action="review_receiving_status",
            confidence=0.84,
            variance_amount=variance_amount,
        )

    return POMatchFinding(
        status="pass",
        risk_level="low",
        key_findings=key_findings,
        evidence_ids=evidence_ids,
        recommended_action="proceed",
        confidence=0.93,
        variance_amount=variance_amount,
    )
