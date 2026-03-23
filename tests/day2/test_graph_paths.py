from decimal import Decimal

import pytest

from aegisap.day2.config import HIGH_VALUE_THRESHOLD, ROUTE_PRECEDENCE
from aegisap.day2.graph import build_graph
from aegisap.day2.state import WorkflowState, make_initial_state
from tests.day2.helpers import make_invoice


@pytest.fixture()
def graph():
    try:
        return build_graph()
    except ImportError:
        pytest.skip("LangGraph not installed in current environment")


def _run(
    graph,
    *,
    supplier_name: str = "Contoso Ltd",
    gross_amount: Decimal = Decimal("1500.00"),
    known_vendor: bool,
) -> WorkflowState:
    invoice = make_invoice(
        supplier_name=supplier_name,
        gross_amount=gross_amount,
        net_amount=gross_amount - Decimal("250.00"),
        vat_amount=Decimal("250.00"),
    )
    state = make_initial_state(
        invoice,
        package_id="msg-graph-001",
        known_vendor=known_vendor,
        high_value_threshold=HIGH_VALUE_THRESHOLD,
        route_precedence=ROUTE_PRECEDENCE,
    )
    result = graph.invoke(state)
    if isinstance(result, WorkflowState):
        return result
    return WorkflowState.model_validate(result)


def test_clean_path(graph) -> None:
    result = _run(graph, gross_amount=Decimal("1500.00"), known_vendor=True)
    assert result.route == "clean_path"
    assert result.status == "completed"
    assert "clean_path_finalize" in result.completed_nodes


def test_high_value_path(graph) -> None:
    result = _run(graph, gross_amount=Decimal("20000.00"), known_vendor=True)
    assert result.route == "high_value"
    assert result.status == "in_review"
    assert any(r.action == "manager_approval_required" for r in result.recommendations)


def test_new_vendor_path(graph) -> None:
    result = _run(
        graph,
        supplier_name="Blueleaf Advisory",
        gross_amount=Decimal("1500.00"),
        known_vendor=False,
    )
    assert result.route == "new_vendor"
    assert result.status == "in_review"
    assert any(r.action == "run_vendor_verification" for r in result.recommendations)


def test_high_value_precedes_new_vendor(graph) -> None:
    result = _run(
        graph,
        supplier_name="Blueleaf Advisory",
        gross_amount=Decimal("20000.00"),
        known_vendor=False,
    )
    assert result.route == "high_value"
    assert any(
        item.kind == "routing_rule_suppressed" and item.detail.startswith("new_vendor")
        for item in result.evidence
    )
