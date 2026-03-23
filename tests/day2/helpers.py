from __future__ import annotations

from datetime import date
from decimal import Decimal

from aegisap.day_01.models import CanonicalInvoice


def make_invoice(**overrides: object) -> CanonicalInvoice:
    base = {
        "supplier_name": "Contoso Ltd",
        "invoice_number": "INV-1007",
        "invoice_date": date(2026, 3, 14),
        "currency": "GBP",
        "net_amount": Decimal("1250.00"),
        "vat_amount": Decimal("250.00"),
        "gross_amount": Decimal("1500.00"),
        "po_reference": "PO-7781",
        "bank_details_hash": "0" * 64,
    }
    base.update(overrides)
    return CanonicalInvoice(**base)
