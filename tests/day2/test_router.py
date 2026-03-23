from decimal import Decimal

from aegisap.day2.config import HIGH_VALUE_THRESHOLD, ROUTE_PRECEDENCE
from aegisap.day2.router import decide_route
from aegisap.day2.state import make_initial_state
from tests.day2.helpers import make_invoice


def test_route_high_value_precedes_new_vendor() -> None:
    state = make_initial_state(
        make_invoice(
            gross_amount=Decimal("50000.00"),
            net_amount=Decimal("40000.00"),
            vat_amount=Decimal("10000.00"),
        ),
        package_id="msg-hv-001",
        known_vendor=False,
        high_value_threshold=HIGH_VALUE_THRESHOLD,
        route_precedence=ROUTE_PRECEDENCE,
    )

    decision = decide_route(state)

    assert decision.route == "high_value"
    assert "high_value" in decision.triggered_conditions
    assert "new_vendor" in decision.triggered_conditions


def test_route_clean_path_when_no_exception_fires() -> None:
    state = make_initial_state(
        make_invoice(),
        package_id="msg-clean-001",
        known_vendor=True,
        high_value_threshold=HIGH_VALUE_THRESHOLD,
        route_precedence=ROUTE_PRECEDENCE,
    )

    decision = decide_route(state)

    assert decision.route == "clean_path"
    assert decision.triggered_conditions == []
