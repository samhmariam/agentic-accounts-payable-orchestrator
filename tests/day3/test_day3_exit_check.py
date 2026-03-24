from aegisap.day3.graph import run_day3_workflow


def test_day3_exit_check_prefers_current_vendor_master_over_stale_email():
    invoice = {
        "case_id": "CASE-3001",
        "invoice_id": "INV-3001",
        "invoice_date": "2026-03-01",
        "vendor_id": "VEND-001",
        "vendor_name": "Acme Office Supplies",
        "po_number": "PO-9001",
        "amount": 12500.00,
        "currency": "GBP",
        "bank_account_last4": "4421",
    }

    state = run_day3_workflow(invoice)
    vendor_risk = state.agent_findings["vendor_risk"]
    decision = state.agent_findings["decision"]

    assert vendor_risk.status == "pass"
    assert decision.recommendation == "approve"
    assert "outranks stale tier 3 email evidence".lower() in " ".join(decision.policy_notes).lower()
    assert "vendor-master-VEND-001" in decision.evidence_ids
    assert any(eid == "doc-onboarding-old-bank" for eid in vendor_risk.evidence_ids)


def test_missing_po_routes_to_manual_review():
    invoice = {
        "case_id": "CASE-3002",
        "invoice_id": "INV-3002",
        "invoice_date": "2026-03-01",
        "vendor_id": "VEND-001",
        "vendor_name": "Acme Office Supplies",
        "amount": 12500.00,
        "currency": "GBP",
        "bank_account_last4": "4421",
    }

    state = run_day3_workflow(invoice)

    assert state.agent_findings["po_match"].status == "missing_po"
    assert state.agent_findings["decision"].recommendation == "manual_review"
    assert state.agent_findings["decision"].next_step == "route_to_po_exception_queue"


def test_no_authoritative_vendor_evidence_holds_case():
    invoice = {
        "case_id": "CASE-3003",
        "invoice_id": "INV-3003",
        "invoice_date": "2026-03-01",
        "vendor_id": "VEND-999",
        "vendor_name": "Unknown Vendor",
        "po_number": "PO-9001",
        "amount": 12500.00,
        "currency": "GBP",
        "bank_account_last4": "0000",
    }

    state = run_day3_workflow(invoice)

    assert state.agent_findings["vendor_risk"].status == "review"
    assert state.agent_findings["decision"].recommendation == "manual_review"
