from __future__ import annotations

import json
import os
from functools import lru_cache

from aegisap.security.credentials import get_openai_client

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


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(f"missing required environment variable: {name}")

@lru_cache(maxsize=1)
def _get_client():
    return get_openai_client()


def _extract_message_text(response) -> str:
    content = response.choices[0].message.content
    if isinstance(content, str):
        return content

    parts: list[str] = []
    for item in content or []:
        text = getattr(item, "text", None)
        if text:
            parts.append(text)
    return "".join(parts)


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
    client = _get_client()
    deployment = _required_env("AZURE_OPENAI_CHAT_DEPLOYMENT")
    package_json = json.dumps(package.model_dump(mode="json"), ensure_ascii=True)

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {
                "role": "user",
                "content": (
                    "Extract the invoice candidate from this package.\n"
                    "Return a JSON object matching the ExtractedInvoiceCandidate schema.\n"
                    f"Invoice package:\n{package_json}"
                ),
            },
        ],
    )
    return _parse_candidate_payload(_extract_message_text(response))
