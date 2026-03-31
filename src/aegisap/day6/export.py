"""
Export helpers for the Day 6 policy review layer.
Converts review outcomes to AuditEvent rows and notebook-friendly dicts.
"""
from __future__ import annotations

from typing import Any


def refusal_to_audit_row(outcome: Any, review_input: Any = None) -> dict[str, Any]:
    """
    Convert a ReviewOutcome + optional Day6ReviewInput to a flat dict
    suitable for inserting into the audit_events table or displaying in marimo.
    """
    if hasattr(outcome, "model_dump"):
        d = outcome.model_dump(mode="json")
    elif hasattr(outcome, "__dict__"):
        d = vars(outcome)
    else:
        d = {"raw": str(outcome)}

    row: dict[str, Any] = {
        "outcome": d.get("outcome", str(outcome)),
        "policy_version": d.get("policy_version", ""),
        "reviewer_model": d.get("reviewer_model", ""),
        "reasons": [
            r.get("message", "") if isinstance(r, dict) else str(r)
            for r in d.get("reasons", [])
        ],
        "escalation_required": d.get("escalation_required", False),
        "next_action": str(d.get("next_action", "")),
        "citations": len(d.get("citations", [])),
    }
    if review_input is not None:
        ri = review_input.model_dump(mode="json") if hasattr(
            review_input, "model_dump") else {}
        row["case_id"] = ri.get("case_id", "")
        row["injection_flags_count"] = len(ri.get("injection_flags", []))
    return row


def injection_signals_to_table(signals: list[Any]) -> list[dict[str, Any]]:
    rows = []
    for s in signals:
        if hasattr(s, "model_dump"):
            d = s.model_dump(mode="json")
        elif hasattr(s, "__dict__"):
            d = vars(s)
        else:
            d = {}
        rows.append(
            {
                "evidence_id": d.get("evidence_id", ""),
                "signal": d.get("signal", ""),
                "severity": d.get("severity", ""),
            }
        )
    return rows
