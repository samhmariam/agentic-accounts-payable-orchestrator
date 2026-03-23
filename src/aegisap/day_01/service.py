from __future__ import annotations

from pydantic import ValidationError

from .models import CanonicalInvoice, ExtractedInvoiceCandidate, InvoicePackageInput
from .normalizers import to_canonical_invoice


class IntakeReject(Exception):
    """Raised when an invoice is rejected at the Day 1 intake boundary."""


def run_day_01_intake(package: InvoicePackageInput) -> CanonicalInvoice:
    from .agent import extract_candidate

    try:
        candidate = extract_candidate(package)
        return to_canonical_invoice(candidate, package)
    except (ValidationError, ValueError) as exc:
        raise IntakeReject(f"invoice rejected at intake boundary: {exc}") from exc


def canonicalize_with_candidate(
    package: InvoicePackageInput,
    candidate: ExtractedInvoiceCandidate,
) -> CanonicalInvoice:
    """
    Deterministic test/helper path that bypasses the live model call.
    """
    try:
        return to_canonical_invoice(candidate, package)
    except (ValidationError, ValueError) as exc:
        raise IntakeReject(f"invoice rejected at intake boundary: {exc}") from exc
