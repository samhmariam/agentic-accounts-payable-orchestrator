from __future__ import annotations

from decimal import Decimal
from dataclasses import dataclass

from aegisap.common.clocks import utc_now_iso
from aegisap.day2.predicates import is_high_value, is_new_vendor
from aegisap.day2.state import Route, WorkflowState
from aegisap.domain.evidence import EvidenceItem


@dataclass(frozen=True)
class RouteDecision:
    route: Route
    reason: str
    triggered_conditions: list[str]


def decide_route(state: WorkflowState) -> RouteDecision:
    triggered: list[str] = []
    if is_high_value(state):
        triggered.append("high_value")
    if is_new_vendor(state):
        triggered.append("new_vendor")

    route: Route = "clean_path"
    for candidate in state.policy.route_precedence:
        if candidate in triggered:
            route = candidate  # type: ignore[assignment]
            break

    if route == "high_value":
        reason = (
            "invoice gross amount "
            f"{state.invoice.gross_amount.quantize(Decimal('0.01'))} meets or exceeds "
            f"threshold {state.policy.high_value_threshold.quantize(Decimal('0.01'))}"
        )
    elif route == "new_vendor":
        reason = "vendor not found in approved vendor registry"
    else:
        reason = "no routing exception fired"

    return RouteDecision(route=route, reason=reason, triggered_conditions=triggered)


def apply_route_decision(state: WorkflowState, decision: RouteDecision) -> WorkflowState:
    state.route = decision.route
    state.route_reason = decision.reason
    state.status = "routing"
    state.last_updated_at = utc_now_iso()

    state.evidence.append(
        EvidenceItem(
            kind="routing_decision",
            source="route_invoice",
            detail=decision.reason,
            value=decision.route,
            node_name="route_invoice",
            recorded_at=state.last_updated_at,
        )
    )

    for condition in decision.triggered_conditions:
        state.evidence.append(
            EvidenceItem(
                kind="routing_rule",
                source="route_invoice",
                detail=f"{condition} predicate returned true",
                value=True,
                node_name="route_invoice",
                recorded_at=state.last_updated_at,
            )
        )

    suppressed = [c for c in decision.triggered_conditions if c != decision.route]
    for condition in suppressed:
        state.evidence.append(
            EvidenceItem(
                kind="routing_rule_suppressed",
                source="route_invoice",
                detail=f"{condition} also true but suppressed by precedence",
                value=True,
                node_name="route_invoice",
                recorded_at=state.last_updated_at,
            )
        )

    return state


def route_selector(state: WorkflowState) -> str:
    if state.route is None:
        raise ValueError("route_selector called before route was decided")
    return state.route
