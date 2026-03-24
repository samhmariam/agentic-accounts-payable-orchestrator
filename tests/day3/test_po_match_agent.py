from aegisap.day3.agents.po_match_agent import verify_po_match
from aegisap.day3.retrieval.structured_po_lookup import StructuredPOLookup


def test_po_match_agent_passes_exact_match_case():
    invoice = {
        "case_id": "CASE-3001",
        "vendor_id": "VEND-001",
        "po_number": "PO-9001",
        "amount": 12500.00,
    }
    evidence = StructuredPOLookup().search(po_number="PO-9001")
    finding = verify_po_match(invoice, evidence)

    assert finding.status == "pass"
    assert finding.risk_level == "low"
    assert finding.recommended_action == "proceed"


def test_po_match_agent_flags_incomplete_receipt():
    invoice = {
        "case_id": "CASE-3004",
        "vendor_id": "VEND-002",
        "po_number": "PO-9002",
        "amount": 4800.00,
    }

    evidence = StructuredPOLookup().search(po_number="PO-9002")
    finding = verify_po_match(invoice, evidence)

    assert finding.status == "review"
    assert finding.recommended_action == "review_receiving_status"
    assert "Goods receipt is incomplete." in finding.key_findings
