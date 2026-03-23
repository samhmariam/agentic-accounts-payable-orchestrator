from __future__ import annotations

import hashlib
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from .models import CanonicalInvoice, EvidenceValue, ExtractedInvoiceCandidate, InvoicePackageInput

CURRENCY_MAP = {
    "€": "EUR",
    "£": "GBP",
    "$": "USD",
}

DATE_FORMATS = (
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%d.%m.%Y",
    "%d %b %Y",
    "%d %B %Y",
)

CENT = Decimal("0.01")
CURRENCY_TOKEN_PATTERN = r"(?:EUR|GBP|USD|€|\$|£)"


def _collapse_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().casefold()


def _is_alnum(char: str) -> bool:
    return char.isalnum()


def _is_identifier_joiner(char: str) -> bool:
    return char in "-/."


def _has_structured_boundaries(raw_value: str, haystack: str) -> bool:
    needle = _collapse_ws(raw_value)
    hay = _collapse_ws(haystack)
    start = 0

    while True:
        idx = hay.find(needle, start)
        if idx == -1:
            return False

        before = hay[idx - 1] if idx > 0 else ""
        after_idx = idx + len(needle)
        after = hay[after_idx] if after_idx < len(hay) else ""

        start_ok = not _is_alnum(needle[0]) or not before or not _is_alnum(before)
        end_char = needle[-1]
        end_needs_boundary = _is_alnum(end_char) or _is_identifier_joiner(end_char)
        end_ok = not end_needs_boundary or not after or not _is_alnum(after)

        if start_ok and end_ok:
            return True

        start = idx + 1


def _pdf_haystack(package: InvoicePackageInput) -> str:
    return "\n".join(a.extracted_text for a in package.attachments if a.extracted_text)


def _email_haystack(package: InvoicePackageInput) -> str:
    return f"{package.email_subject}\n{package.email_body}"


def _assert_present(raw_value: str, haystack: str, field_name: str, *, structured: bool = False) -> None:
    present = (
        _has_structured_boundaries(raw_value, haystack)
        if structured
        else _collapse_ws(raw_value) in _collapse_ws(haystack)
    )
    if not present:
        raise ValueError(f"{field_name} evidence not found in source text: {raw_value!r}")


def _require_text(
    raw_value: str | None,
    package: InvoicePackageInput,
    field_name: str,
    *,
    structured: bool = False,
) -> str:
    if raw_value is None or not raw_value.strip():
        raise ValueError(f"{field_name} is required")

    combined = f"{_pdf_haystack(package)}\n{_email_haystack(package)}"
    _assert_present(raw_value, combined, field_name, structured=structured)
    return raw_value.strip()


def normalize_currency(raw: str) -> str:
    cleaned = raw.strip().upper()
    if cleaned in {"EUR", "GBP", "USD"}:
        return cleaned

    symbol = raw.strip()
    if symbol in CURRENCY_MAP:
        return CURRENCY_MAP[symbol]

    raise ValueError(f"unsupported currency: {raw!r}")


def parse_invoice_date(raw: str) -> datetime.date:
    value = raw.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"unsupported invoice date format: {raw!r}")


def parse_money(raw: str, *, allow_zero: bool = False) -> Decimal:
    """
    Deterministic amount parser.

    Reject ambiguous single-separator values like '1.250' or '1,250'
    because they can silently mean either 1250.00 or 1.25 depending on locale.
    """
    s = raw.strip().replace("\u00A0", "").replace(" ", "").replace("'", "")
    match = re.fullmatch(
        rf"(?:(?P<prefix>{CURRENCY_TOKEN_PATTERN}))?"
        r"(?P<number>[0-9][0-9.,]*)"
        rf"(?:(?P<suffix>{CURRENCY_TOKEN_PATTERN}))?",
        s.upper(),
    )
    if not match:
        raise ValueError(f"invalid amount format: {raw!r}")

    if match.group("prefix") and match.group("suffix"):
        raise ValueError(f"amount must contain at most one currency token: {raw!r}")

    s = match.group("number")

    if not re.search(r"\d", s):
        raise ValueError(f"amount contains no digits: {raw!r}")

    if s.startswith("-"):
        raise ValueError(f"negative amounts not allowed on Day 1: {raw!r}")

    if "," in s and "." in s:
        decimal_sep = "," if s.rfind(",") > s.rfind(".") else "."
        thousand_sep = "." if decimal_sep == "," else ","
        s = s.replace(thousand_sep, "").replace(decimal_sep, ".")
    elif "," in s:
        parts = s.split(",")
        if len(parts) == 2 and len(parts[1]) == 2:
            s = f"{parts[0]}.{parts[1]}"
        elif len(parts) > 2 and all(len(p) == 3 for p in parts[1:]):
            s = "".join(parts)
        elif len(parts) == 2 and len(parts[1]) == 3:
            raise ValueError(f"ambiguous amount, reject at boundary: {raw!r}")
        else:
            raise ValueError(f"unsupported comma amount format: {raw!r}")
    elif "." in s:
        parts = s.split(".")
        if len(parts) == 2 and len(parts[1]) == 2:
            pass
        elif len(parts) > 2 and all(len(p) == 3 for p in parts[1:]):
            s = "".join(parts)
        elif len(parts) == 2 and len(parts[1]) == 3:
            raise ValueError(f"ambiguous amount, reject at boundary: {raw!r}")
        else:
            raise ValueError(f"unsupported dot amount format: {raw!r}")

    try:
        amount = Decimal(s).quantize(CENT, rounding=ROUND_HALF_UP)
    except InvalidOperation as exc:
        raise ValueError(f"invalid amount: {raw!r}") from exc

    if allow_zero:
        if amount < 0:
            raise ValueError(f"amount must be >= 0: {raw!r}")
    else:
        if amount <= 0:
            raise ValueError(f"amount must be > 0: {raw!r}")

    return amount


def hash_bank_details(raw: str) -> str:
    cleaned = re.sub(r"[^A-Z0-9]", "", raw.upper())
    if len(cleaned) < 8:
        raise ValueError("bank details text too short to hash safely")
    return hashlib.sha256(cleaned.encode("utf-8")).hexdigest()


def reconcile_amount(
    evidence: EvidenceValue | None,
    package: InvoicePackageInput,
    *,
    field_name: str,
    allow_zero: bool = False,
) -> Decimal:
    if evidence is None:
        raise ValueError(f"{field_name} is required")

    values: set[Decimal] = set()

    pdf_text = _pdf_haystack(package)
    email_text = _email_haystack(package)

    if evidence.pdf_text:
        _assert_present(evidence.pdf_text, pdf_text, f"{field_name}.pdf_text")
        values.add(parse_money(evidence.pdf_text, allow_zero=allow_zero))

    if evidence.email_text:
        _assert_present(evidence.email_text, email_text, f"{field_name}.email_text")
        values.add(parse_money(evidence.email_text, allow_zero=allow_zero))

    if not values:
        raise ValueError(f"{field_name} has no usable evidence")

    if len(values) > 1:
        normalized = ", ".join(sorted(str(v) for v in values))
        raise ValueError(f"{field_name} mismatch between sources: {normalized}")

    return next(iter(values))


def to_canonical_invoice(
    candidate: ExtractedInvoiceCandidate,
    package: InvoicePackageInput,
) -> CanonicalInvoice:
    supplier_name = _require_text(candidate.supplier_name_text, package, "supplier_name_text")
    invoice_number = _require_text(
        candidate.invoice_number_text, package, "invoice_number_text", structured=True
    )
    invoice_date_text = _require_text(
        candidate.invoice_date_text, package, "invoice_date_text", structured=True
    )
    currency_text = _require_text(candidate.currency_text, package, "currency_text", structured=True)
    po_reference = _require_text(candidate.po_reference_text, package, "po_reference_text", structured=True)
    bank_details_text = _require_text(
        candidate.bank_details_text, package, "bank_details_text", structured=True
    )

    return CanonicalInvoice(
        supplier_name=supplier_name,
        invoice_number=invoice_number,
        invoice_date=parse_invoice_date(invoice_date_text),
        currency=normalize_currency(currency_text),
        net_amount=reconcile_amount(candidate.net_amount, package, field_name="net_amount"),
        vat_amount=reconcile_amount(candidate.vat_amount, package, field_name="vat_amount", allow_zero=True),
        gross_amount=reconcile_amount(candidate.gross_amount, package, field_name="gross_amount"),
        po_reference=po_reference,
        bank_details_hash=hash_bank_details(bank_details_text),
    )
