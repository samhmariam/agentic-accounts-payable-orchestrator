from dataclasses import asdict

from aegisap.day3.agents.decision_synthesizer import synthesize_decision
from aegisap.day3.agents.po_match_agent import verify_po_match
from aegisap.day3.agents.vendor_risk_verifier import verify_vendor_risk
from aegisap.day3.retrieval.structured_po_lookup import StructuredPOLookup
from aegisap.day3.retrieval.structured_vendor_lookup import StructuredVendorLookup


def test_specialist_handoffs_return_typed_contract_fields():
    invoice = {
        "case_id": "CASE-3006",
        "vendor_id": "VEND-001",
        "vendor_name": "Acme Office Supplies",
        "po_number": "PO-9001",
        "amount": 12500.00,
        "bank_account_last4": "4421",
    }

    vendor_evidence = StructuredVendorLookup().search(vendor_id="VEND-001", vendor_name=None)
    po_evidence = StructuredPOLookup().search(po_number="PO-9001")

    vendor_finding = verify_vendor_risk(invoice, vendor_evidence)
    po_finding = verify_po_match(invoice, po_evidence)
    decision = synthesize_decision(vendor_risk=vendor_finding, po_match=po_finding)

    vendor_payload = asdict(vendor_finding)
    po_payload = asdict(po_finding)
    decision_payload = asdict(decision)

    assert {
        "status",
        "risk_level",
        "key_findings",
        "evidence_ids",
        "recommended_action",
        "confidence",
        "open_questions",
    } <= vendor_payload.keys()
    assert {
        "status",
        "risk_level",
        "key_findings",
        "evidence_ids",
        "recommended_action",
        "confidence",
        "variance_amount",
        "open_questions",
    } <= po_payload.keys()
    assert {
        "recommendation",
        "rationale",
        "evidence_ids",
        "confidence",
        "next_step",
        "policy_notes",
    } <= decision_payload.keys()
