from aegisap.day_01.fixture_loader import load_fixture_candidate, load_fixture_package
from aegisap.day_01.service import canonicalize_with_candidate
from aegisap.day2.config import HIGH_VALUE_THRESHOLD, ROUTE_PRECEDENCE
from aegisap.day2.state import make_initial_state
from tests.day2.helpers import make_invoice


def test_make_initial_state_has_thread_local_vendor_context() -> None:
    invoice = make_invoice()

    state = make_initial_state(
        invoice,
        package_id="msg-state-001",
        known_vendor=True,
        high_value_threshold=HIGH_VALUE_THRESHOLD,
        route_precedence=ROUTE_PRECEDENCE,
    )

    assert state.invoice.invoice_number == "INV-1007"
    assert state.invoice_id == "INV-1007"
    assert state.package_id == "msg-state-001"
    assert state.vendor.vendor_name == "Contoso Ltd"
    assert state.vendor.verification.verified is False
    assert state.route is None


def test_make_initial_state_accepts_real_day_01_output() -> None:
    package = load_fixture_package("happy_path")
    candidate = load_fixture_candidate("happy_path")
    invoice = canonicalize_with_candidate(package, candidate)

    state = make_initial_state(
        invoice,
        package_id=package.message_id,
        known_vendor=True,
        high_value_threshold=HIGH_VALUE_THRESHOLD,
        route_precedence=ROUTE_PRECEDENCE,
    )

    assert state.invoice.invoice_number == "INV-1007"
    assert state.package_id == "msg-happy-001"
    assert state.thread_id == "thread_msg-happy-001_INV-1007"
