from __future__ import annotations

from aegisap.security.redaction import redact_text, summarize_evidence_text


def test_redact_text_masks_common_pii_patterns() -> None:
    redacted, changed = redact_text(
        "Email finance@example.com and call +44 20 7946 0958 about VAT REF-GBABCD1234 "
        "for account 12345678 sort code 12-34-56."
    )

    assert changed is True
    assert "finance@example.com" not in redacted
    assert "+44 20 7946 0958" not in redacted
    assert "GBABCD1234" not in redacted
    assert "12345678" not in redacted
    assert "[REDACTED_EMAIL]" in redacted
    assert "[REDACTED_PHONE]" in redacted
    assert "[REDACTED_TAX_ID]" in redacted


def test_redact_text_hashes_bank_like_values() -> None:
    redacted, changed = redact_text("Please confirm account 12345678 before release.")

    assert changed is True
    assert "12345678" not in redacted
    assert "[REDACTED_BANK:" in redacted


def test_summarize_evidence_text_truncates_long_freeform_content() -> None:
    summary, changed = summarize_evidence_text("A" * 600)

    assert changed is True
    assert len(summary) < 260
