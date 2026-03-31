from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from aegisap.common.hashing import stable_sha256

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_RE = re.compile(
    r"(?=(?:\D*\d){10,})(?:(?:\+\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?){2,4}\d{3,4})"
)
VAT_RE = re.compile(r"\b(?:VAT|TAX)[\s:#-]*[A-Z0-9-]{6,}\b", re.IGNORECASE)
BANK_RE = re.compile(r"\b(?:\d[ -]?){8,20}\b")
ADDRESS_RE = re.compile(
    r"\b\d{1,5}\s+[A-Z0-9][A-Z0-9\s]{3,40}\s(?:Street|St|Road|Rd|Lane|Ln|Avenue|Ave|Drive|Dr)\b",
    re.IGNORECASE,
)
MAX_TEXT_LENGTH = 140


def redact_text(text: str) -> tuple[str, bool]:
    redacted = text
    changed = False

    def replace(pattern: re.Pattern[str], replacement: str) -> None:
        nonlocal redacted, changed
        updated = pattern.sub(replacement, redacted)
        if updated != redacted:
            redacted = updated
            changed = True

    replace(EMAIL_RE, "[REDACTED_EMAIL]")
    replace(PHONE_RE, "[REDACTED_PHONE]")
    replace(VAT_RE, "[REDACTED_TAX_ID]")
    redacted = BANK_RE.sub(_mask_bank_like_text, redacted)
    changed = changed or redacted != text
    replace(ADDRESS_RE, "[REDACTED_ADDRESS]")

    if len(redacted) > MAX_TEXT_LENGTH:
        redacted = f"{redacted[:MAX_TEXT_LENGTH].rstrip()}..."
        changed = True

    return redacted, changed


def redact_pii(text: str) -> str:
    redacted, _changed = redact_text(text)
    return redacted


def redact_value(value: Any) -> tuple[Any, bool]:
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, Mapping):
        changed = False
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            sanitized, item_changed = redact_value(item)
            redacted[str(key)] = sanitized
            changed = changed or item_changed
        return redacted, changed
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        changed = False
        redacted_items: list[Any] = []
        for item in value:
            sanitized, item_changed = redact_value(item)
            redacted_items.append(sanitized)
            changed = changed or item_changed
        return redacted_items, changed
    return value, False


def summarize_evidence_text(text: str) -> tuple[str, bool]:
    redacted, changed = redact_text(text)
    return redacted, changed


def _mask_bank_like_text(match: re.Match[str]) -> str:
    digits = re.sub(r"[^0-9]", "", match.group(0))
    if len(digits) < 8:
        return match.group(0)
    hashed = stable_sha256(digits)[:8]
    return f"[REDACTED_BANK:{hashed}]"
