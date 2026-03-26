from aegisap.day4.planning.policy_overlay import derive_policy_overlay
from tests.day4.helpers import load_case_facts


def test_derives_combined_risk_controls_for_high_value_invoice_with_missing_po_and_bank_change() -> None:
    overlay = derive_policy_overlay(load_case_facts("high_value_missing_po_bank_change"))

    assert {"existing_supplier", "missing_po", "bank_details_changed", "high_value", "combined_risk"} <= set(
        overlay.risk_flags
    )
    assert {
        "po_match_verification",
        "po_waiver_check",
        "vendor_bank_verification",
        "threshold_approval_check",
        "manual_escalation_package",
    } <= set(overlay.mandatory_task_types)
    assert {"ap_manager", "controller"} <= set(overlay.required_approvals)
    assert overlay.escalation_route.queue == "finance_ops_manual_review"
