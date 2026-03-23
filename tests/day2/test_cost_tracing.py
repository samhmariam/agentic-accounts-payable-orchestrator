from aegisap.day2.config import HIGH_VALUE_THRESHOLD, ROUTE_PRECEDENCE
from aegisap.day2.nodes import init_workflow, route_invoice
from aegisap.day2.state import make_initial_state
from tests.day2.helpers import make_invoice


def test_traced_nodes_append_metrics() -> None:
    invoice = make_invoice()
    state = make_initial_state(
        invoice,
        package_id="msg-metrics-001",
        known_vendor=True,
        high_value_threshold=HIGH_VALUE_THRESHOLD,
        route_precedence=ROUTE_PRECEDENCE,
    )

    init_workflow(state)
    route_invoice(state)

    assert len(state.node_metrics) == 2
    assert state.total_latency_ms >= 0
    assert all(metric.node_name in {"init_workflow", "route_invoice"} for metric in state.node_metrics)
