from aegisap.day3.graph import run_day3_workflow


def test_evaluation_scores_are_populated_for_completed_case():
    invoice = {
        "case_id": "CASE-3005",
        "invoice_id": "INV-3005",
        "invoice_date": "2026-03-01",
        "vendor_id": "VEND-001",
        "vendor_name": "Acme Office Supplies",
        "po_number": "PO-9001",
        "amount": 12500.00,
        "currency": "GBP",
        "bank_account_last4": "4421",
    }

    state = run_day3_workflow(invoice)

    assert state.status == "completed"
    assert state.eval_scores["faithfulness"] == 1.0
    assert state.eval_scores["completeness"] == 1.0
    assert state.eval_scores["policy_grounding"] == 1.0
    assert isinstance(state.eval_scores["notes"], list)
