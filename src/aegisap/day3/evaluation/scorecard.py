from __future__ import annotations

from ..state.workflow_state import WorkflowState


def score_case(state: WorkflowState) -> dict[str, float | list[str]]:
    decision = state.agent_findings["decision"]
    vendor_risk = state.agent_findings["vendor_risk"]
    po_match = state.agent_findings["po_match"]

    notes: list[str] = []
    evidence_exists = all(eid in state.evidence_registry for eid in decision.evidence_ids)
    faithfulness = 1.0 if evidence_exists else 0.0
    if not evidence_exists:
        notes.append("Decision cites one or more missing evidence ids.")

    completeness = 0.0
    if vendor_risk and po_match and decision:
        completeness = 1.0
    else:
        notes.append("One or more specialist findings are missing.")

    policy_grounding = 0.0
    if any("outrank" in note.lower() or "tier 1" in note.lower() for note in decision.policy_notes):
        policy_grounding = 1.0
    elif decision.recommendation == "manual_review":
        policy_grounding = 0.75
        notes.append("Decision routed to review, but source-priority language was weak.")
    else:
        notes.append("Decision does not explicitly state authority-tier logic.")

    return {
        "faithfulness": faithfulness,
        "completeness": completeness,
        "policy_grounding": policy_grounding,
        "notes": notes,
    }
