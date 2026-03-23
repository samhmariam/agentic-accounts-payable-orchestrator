from __future__ import annotations

from aegisap.day2.state import WorkflowState


def is_high_value(state: WorkflowState) -> bool:
    return state.invoice.gross_amount >= state.policy.high_value_threshold


def is_new_vendor(state: WorkflowState) -> bool:
    return not state.vendor.is_known_vendor
