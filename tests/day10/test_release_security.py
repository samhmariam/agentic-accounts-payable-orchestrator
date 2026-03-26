from __future__ import annotations

from aegisap.security.config import load_security_config
from aegisap.security.policy import validate_security_posture


def test_cloud_runtime_rejects_plain_resume_token_secret() -> None:
    config = load_security_config(
        {
            "AEGISAP_ENVIRONMENT": "production",
            "AZURE_KEY_VAULT_URI": "https://example.vault.azure.net/",
            "AEGISAP_RESUME_TOKEN_SECRET": "plain-secret",
        }
    )

    try:
        validate_security_posture(config)
    except RuntimeError as exc:
        assert "AEGISAP_RESUME_TOKEN_SECRET" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("plain resume token fallback should be rejected in production")
