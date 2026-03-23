from tests.day2.helpers import make_invoice

from aegisap.day2.config import HIGH_VALUE_THRESHOLD, ROUTE_PRECEDENCE
from aegisap.day2.nodes import new_vendor_review
from aegisap.day2.state import make_initial_state


GLOBAL_VENDOR_CACHE = {"vendor_verified": False}


def bad_global_check(vendor_name: str) -> bool:
    return GLOBAL_VENDOR_CACHE["vendor_verified"]


def bad_global_verify(vendor_name: str) -> None:
    GLOBAL_VENDOR_CACHE["vendor_verified"] = True


def test_global_vendor_cache_is_silent_failure_pattern() -> None:
    bad_global_verify("Approved Vendor")
    assert bad_global_check("Brand New Vendor") is True


def test_vendor_verification_is_scoped_to_workflow_thread() -> None:
    first = make_invoice(supplier_name="Approved Vendor", invoice_number="AP-1001")
    second = make_invoice(supplier_name="Brand New Vendor", invoice_number="BN-1001")

    state_one = make_initial_state(
        first,
        package_id="msg-approved-001",
        known_vendor=True,
        high_value_threshold=HIGH_VALUE_THRESHOLD,
        route_precedence=ROUTE_PRECEDENCE,
        thread_id="thread-approved",
    )
    state_two = make_initial_state(
        second,
        package_id="msg-new-vendor-001",
        known_vendor=False,
        high_value_threshold=HIGH_VALUE_THRESHOLD,
        route_precedence=ROUTE_PRECEDENCE,
        thread_id="thread-new-vendor",
    )

    new_vendor_review(state_two)

    assert state_one.vendor.verification.verified is False
    assert state_two.vendor.verification.verified is False
    assert state_one.thread_id != state_two.thread_id
    assert len(state_one.vendor.verification.evidence) == 0
    assert len(state_two.vendor.verification.evidence) == 1
