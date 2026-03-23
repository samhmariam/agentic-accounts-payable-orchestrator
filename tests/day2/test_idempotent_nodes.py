from aegisap.day2.config import HIGH_VALUE_THRESHOLD, ROUTE_PRECEDENCE
from aegisap.day2.nodes import new_vendor_review
from aegisap.day2.state import make_initial_state
from tests.day2.helpers import make_invoice


def test_new_vendor_review_recommendation_is_not_duplicated() -> None:
    invoice = make_invoice(supplier_name="Unknown Vendor", invoice_number="UV-1001")
    state = make_initial_state(
        invoice,
        package_id="msg-uv-001",
        known_vendor=False,
        high_value_threshold=HIGH_VALUE_THRESHOLD,
        route_precedence=ROUTE_PRECEDENCE,
    )

    new_vendor_review(state)
    new_vendor_review(state)

    actions = [r.action for r in state.recommendations]
    assert actions.count("run_vendor_verification") == 1
