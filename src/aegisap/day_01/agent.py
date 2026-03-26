from __future__ import annotations

import json

from aegisap.routing.model_router import ModelGateway, ModelInvocationRequest

from .models import ExtractedInvoiceCandidate, InvoicePackageInput

SYSTEM_INSTRUCTIONS = (
    "You are the Intake & Canonicalization extraction agent.\n"
    "Extract fields only from the provided invoice package.\n"
    "Return JSON only.\n"
    "Do not normalize amount separators.\n"
    "Copy monetary values exactly as they appear in source text.\n"
    "When the same amount appears in both PDF and email, populate both.\n"
    "Do not invent values. Leave missing fields as null."
)
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

    return ExtractedInvoiceCandidate.model_validate(data)


def extract_candidate(package: InvoicePackageInput) -> ExtractedInvoiceCandidate:
    package_json = json.dumps(package.model_dump(mode="json"), ensure_ascii=True)
    prompt = (
        "Extract the invoice candidate from this package.\n"
        "Return a JSON object matching the ExtractedInvoiceCandidate schema.\n"
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
