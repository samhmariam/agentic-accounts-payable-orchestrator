from __future__ import annotations

from typing import Iterable

from ..state.evidence_models import EvidenceItem
from ..state.handoff_models import VendorRiskFinding


def _top_authoritative_bank_evidence(evidence_items: Iterable[EvidenceItem]) -> EvidenceItem | None:
    candidates = [
        item
        for item in evidence_items
        if item.metadata.get("bank_account_last4")
        and item.source_type in {"erp_vendor_master", "approved_bank_change"}
    ]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda item: (
            item.authority_tier * -1,
            item.authority_adjusted_score,
            item.event_time.isoformat() if item.event_time else "",
        ),
        reverse=True,
    )[0]


def verify_vendor_risk(invoice: dict, evidence_items: list[EvidenceItem]) -> VendorRiskFinding:
    agent_name = "vendor_risk_verifier"
    for item in evidence_items:
        item.mark_used_by(agent_name)

    authoritative = _top_authoritative_bank_evidence(evidence_items)
    invoice_bank_last4 = invoice.get("bank_account_last4")
    key_findings: list[str] = []
    evidence_ids: list[str] = []
    open_questions: list[str] = []

    if authoritative is None:
        return VendorRiskFinding(
            status="review",
            risk_level="high",
            key_findings=["No authoritative vendor bank evidence was available."],
            evidence_ids=[],
            recommended_action="hold_for_manual_review",
            confidence=0.35,
            open_questions=["Validate current approved bank details in vendor master."],
        )

    evidence_ids.append(authoritative.evidence_id)
    authoritative_last4 = authoritative.metadata.get("bank_account_last4")
    key_findings.append(
        f'Authoritative bank evidence is {authoritative.source_type} with account ending {authoritative_last4}.'
    )

    contradicting_history = []
    for item in evidence_items:
        historical_last4 = item.metadata.get("bank_account_last4")
        if historical_last4 and historical_last4 != authoritative_last4:
            contradicting_history.append(item)
    for item in contradicting_history:
        evidence_ids.append(item.evidence_id)

    if contradicting_history:
        key_findings.append(
            "Lower-authority or older evidence contains different bank details and is treated as historical context."
        )

    if invoice_bank_last4 and invoice_bank_last4 != authoritative_last4:
        key_findings.append(
            f'Invoice bank details ({invoice_bank_last4}) do not match the approved bank details ({authoritative_last4}).'
        )
        return VendorRiskFinding(
            status="review",
            risk_level="high",
            key_findings=key_findings,
            evidence_ids=list(dict.fromkeys(evidence_ids)),
            recommended_action="hold_for_bank_validation",
            confidence=0.95,
            open_questions=[
                "Was there a newly approved bank change after the vendor master update?",
                "Does AP have a signed bank-change approval ticket for the invoice bank account?",
            ],
        )

    if contradicting_history:
        key_findings.append(
            "Silent-failure guard applied: current structured evidence outranks stale email or onboarding documents."
        )

    return VendorRiskFinding(
        status="pass",
        risk_level="low",
        key_findings=key_findings,
        evidence_ids=list(dict.fromkeys(evidence_ids)),
        recommended_action="proceed",
        confidence=0.91,
        open_questions=open_questions,
    )
