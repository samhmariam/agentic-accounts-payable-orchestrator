from __future__ import annotations

import json

from aegisap.routing.model_router import ModelGateway, ModelInvocationRequest

from .models import EvidenceValue, ExtractedInvoiceCandidate, InvoicePackageInput

SYSTEM_INSTRUCTIONS = (
    "You are the Intake & Canonicalization extraction agent.\n"
    "Extract fields only from the provided invoice package.\n"
    "Return JSON only.\n"
    "Use exactly these keys: supplier_name_text, invoice_number_text, invoice_date_text, "
    "currency_text, net_amount, vat_amount, gross_amount, po_reference_text, bank_details_text.\n"
    "For net_amount, vat_amount, and gross_amount, return an object with pdf_text and/or email_text, not a bare string.\n"
    "Do not normalize amount separators.\n"
    "Copy monetary values exactly as they appear in source text.\n"
    "When the same amount appears in both PDF and email, populate both.\n"
    "Do not invent values. Leave missing fields as null."
)


def _normalize_evidence_value(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, str):
        return {"pdf_text": value}
    if isinstance(value, EvidenceValue):
        return value
    if isinstance(value, dict):
        if "pdf_text" in value or "email_text" in value:
            return value
        text = value.get("text")
        if isinstance(text, str):
            return {"pdf_text": text}
        pdf_text = value.get("pdf")
        email_text = value.get("email")
        if isinstance(pdf_text, str) or isinstance(email_text, str):
            payload: dict[str, str] = {}
            if isinstance(pdf_text, str):
                payload["pdf_text"] = pdf_text
            if isinstance(email_text, str):
                payload["email_text"] = email_text
            return payload
    return value


def _normalize_candidate_payload(data: dict[str, object]) -> dict[str, object]:
    alias_map = {
        "supplier_name": "supplier_name_text",
        "invoice_number": "invoice_number_text",
        "invoice_date": "invoice_date_text",
        "currency": "currency_text",
        "po_reference": "po_reference_text",
        "bank_details": "bank_details_text",
    }
    allowed_fields = {
        "supplier_name_text",
        "invoice_number_text",
        "invoice_date_text",
        "currency_text",
        "net_amount",
        "vat_amount",
        "gross_amount",
        "po_reference_text",
        "bank_details_text",
    }

    normalized: dict[str, object] = {}
    for key, value in data.items():
        target_key = alias_map.get(key, key)
        if target_key not in allowed_fields:
            continue
        if target_key in {"net_amount", "vat_amount", "gross_amount"}:
            normalized[target_key] = _normalize_evidence_value(value)
            continue
        normalized[target_key] = value
    return normalized


def _parse_candidate_payload(payload: str) -> ExtractedInvoiceCandidate:
    text = payload.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("model returned non-JSON extraction output") from exc

    if not isinstance(data, dict):
        raise ValueError("model returned non-object extraction output")

    return ExtractedInvoiceCandidate.model_validate(_normalize_candidate_payload(data))


def extract_candidate(package: InvoicePackageInput) -> ExtractedInvoiceCandidate:
    package_json = json.dumps(package.model_dump(mode="json"), ensure_ascii=True)
    prompt = (
        "Extract the invoice candidate from this package.\n"
        "Return a JSON object matching the ExtractedInvoiceCandidate schema.\n"
        "Allowed keys only: supplier_name_text, invoice_number_text, invoice_date_text, "
        "currency_text, net_amount, vat_amount, gross_amount, po_reference_text, bank_details_text.\n"
        "The amount fields must be objects like {\"pdf_text\": \"12500.00 GBP\", \"email_text\": null}.\n"
        f"Invoice package:\n{package_json}"
    )
    response_text, _decision, _ledger_entry = ModelGateway().invoke_text(
        ModelInvocationRequest(
            task_class="extract",
            node_name="invoice_extraction",
            system_instruction=SYSTEM_INSTRUCTIONS,
            user_prompt=prompt,
            prompt_revision="day1",
            metadata={"tenant": "aegisap-training"},
            source_snapshot_hash=package.message_id,
            citation_hash=package.message_id,
        )
    )
    return _parse_candidate_payload(response_text)
