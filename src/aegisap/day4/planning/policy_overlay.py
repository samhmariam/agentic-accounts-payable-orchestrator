from __future__ import annotations

from .plan_types import CaseFacts, DerivedPolicyOverlay, EscalationRoute, RiskFlag

DEFAULT_APPROVAL_THRESHOLD_GBP = 25_000
DEFAULT_CONTROLLER_THRESHOLD_GBP = 40_000
DEFAULT_ESCALATION_QUEUE = "finance_ops_manual_review"


def derive_policy_overlay(case_facts: CaseFacts) -> DerivedPolicyOverlay:
    approval_threshold = case_facts.amount_approval_threshold_gbp or DEFAULT_APPROVAL_THRESHOLD_GBP
    controller_threshold = case_facts.controller_approval_threshold_gbp or DEFAULT_CONTROLLER_THRESHOLD_GBP

    risk_flags: list[RiskFlag] = []
    mandatory_task_types: list[str] = []
    global_preconditions: list[str] = []
    global_stop_conditions: list[str] = []
    escalation_triggers: list[str] = []
    required_approvals: list[str] = []
    recommendation_blocks: list[str] = []
    escalation_owners = ["ap_manager"]
    escalation_reason_template = "Escalate for manual review when mandatory controls remain unresolved."

    if case_facts.supplier_exists:
        risk_flags.append("existing_supplier")

    mandatory_task_types.extend(["policy_retrieval", "vendor_history_check"])

    if not case_facts.po_present:
        risk_flags.append("missing_po")
        mandatory_task_types.extend(["po_match_verification", "po_waiver_check"])
        global_preconditions.append("po_verified_or_waived")
        global_stop_conditions.append("missing_required_po_evidence")
        escalation_triggers.append("missing_po")
        recommendation_blocks.append("po_condition_unsatisfied")

    if case_facts.bank_details_changed:
        risk_flags.append("bank_details_changed")
        mandatory_task_types.append("vendor_bank_verification")
        global_preconditions.append("bank_change_authoritatively_verified")
        global_stop_conditions.append("unverified_bank_change")
        escalation_triggers.append("bank_details_changed")
        recommendation_blocks.append("bank_change_verification_unsatisfied")
        escalation_owners.append("vendor_master_team")

    if case_facts.invoice_amount_gbp >= approval_threshold:
        risk_flags.append("high_value")
        mandatory_task_types.append("threshold_approval_check")
        required_approvals.append("ap_manager")
        global_preconditions.append("approval_route_defined_for_threshold_case")
        global_stop_conditions.append("approval_not_obtained_for_high_value_case")
        escalation_triggers.append("high_value_invoice")
        recommendation_blocks.append("approval_path_unsatisfied")

    if case_facts.invoice_amount_gbp >= controller_threshold:
        required_approvals.append("controller")
        if "controller" not in escalation_owners:
            escalation_owners.append("controller")

    if not case_facts.po_present and case_facts.bank_details_changed:
        mandatory_task_types.append("manual_escalation_package")
        global_stop_conditions.append("missing_po_and_bank_change_require_manual_review")
        escalation_triggers.append("missing_po_and_bank_change")
        recommendation_blocks.append("manual_review_required")

    if (
        "high_value" in risk_flags
        and "missing_po" in risk_flags
        and "bank_details_changed" in risk_flags
    ):
        risk_flags.append("combined_risk")
        if "manual_escalation_package" not in mandatory_task_types:
            mandatory_task_types.append("manual_escalation_package")
        global_stop_conditions.append("combined_risk_requires_manual_review")
        escalation_triggers.append("combined_risk_flags_present")
        recommendation_blocks.append("combined_risk_requires_escalation")
        escalation_reason_template = (
            "Escalate immediately: combined missing PO, changed bank details, and threshold approval exposure."
        )

    mandatory_task_types.append("payment_recommendation_draft")

    if len(mandatory_task_types) == 3:
        risk_flags.append("clean_path")

    return DerivedPolicyOverlay(
        risk_flags=_unique(risk_flags),
        mandatory_task_types=_unique(mandatory_task_types),
        global_preconditions=_unique(global_preconditions),
        global_stop_conditions=_unique(global_stop_conditions),
        escalation_triggers=_unique(escalation_triggers),
        required_approvals=_unique(required_approvals),
        recommendation_blocks=_unique(recommendation_blocks),
        escalation_route=EscalationRoute(
            queue=DEFAULT_ESCALATION_QUEUE,
            owners=_unique(escalation_owners),
        ),
        escalation_reason_template=escalation_reason_template,
    )


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))
