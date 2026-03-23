from decimal import Decimal

import pytest

from aegisap.day_01.fixture_loader import load_fixture_candidate, load_fixture_package
from aegisap.day_01.service import IntakeReject, canonicalize_with_candidate


def test_happy_path_fixture_canonicalizes():
    package = load_fixture_package("happy_path")
    candidate = load_fixture_candidate("happy_path")

    invoice = canonicalize_with_candidate(package, candidate)

    assert invoice.supplier_name == "Contoso Ltd"
    assert invoice.invoice_number == "INV-1007"
    assert invoice.currency == "GBP"
    assert invoice.net_amount == Decimal("1250.00")
    assert invoice.vat_amount == Decimal("250.00")
    assert invoice.gross_amount == Decimal("1500.00")
    assert invoice.po_reference == "PO-7781"


def test_locale_mismatch_fixture_reconciles_successfully():
    package = load_fixture_package("locale_mismatch")
    candidate = load_fixture_candidate("locale_mismatch")

    invoice = canonicalize_with_candidate(package, candidate)

    assert invoice.supplier_name == "Rhein Energie GmbH"
    assert invoice.currency == "EUR"
    assert invoice.net_amount == Decimal("1000.00")
    assert invoice.vat_amount == Decimal("250.00")
    assert invoice.gross_amount == Decimal("1250.00")
    assert invoice.po_reference == "PO-9001"


def test_missing_po_fixture_is_rejected():
    package = load_fixture_package("missing_po")
    candidate = load_fixture_candidate("missing_po")

    with pytest.raises(IntakeReject, match="po_reference_text is required"):
        canonicalize_with_candidate(package, candidate)


def test_truncated_po_reference_is_rejected():
    package = load_fixture_package("happy_path")
    candidate = load_fixture_candidate("happy_path").model_copy(update={"po_reference_text": "PO-"})

    with pytest.raises(IntakeReject, match="po_reference_text evidence not found"):
        canonicalize_with_candidate(package, candidate)


def test_truncated_bank_details_are_rejected():
    package = load_fixture_package("happy_path")
    candidate = load_fixture_candidate("happy_path").model_copy(
        update={"bank_details_text": "IBAN GB29NWBK"}
    )

    with pytest.raises(IntakeReject, match="bank_details_text evidence not found"):
        canonicalize_with_candidate(package, candidate)
