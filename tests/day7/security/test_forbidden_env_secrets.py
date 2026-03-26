from __future__ import annotations

import pytest

from aegisap.security.config import load_security_config
from aegisap.security.policy import validate_security_posture


def test_config_rejects_search_admin_key_outside_local() -> None:
    config = load_security_config(
        {
            "AEGISAP_ENVIRONMENT": "cloud",
            "AZURE_KEY_VAULT_URI": "https://example.vault.azure.net/",
            "SEARCH_ADMIN_KEY": "secret-search-key",
        }
    )

    with pytest.raises(RuntimeError, match="forbidden runtime secrets"):
        validate_security_posture(config)


def test_config_rejects_postgres_dsn_outside_local() -> None:
    config = load_security_config(
        {
            "AEGISAP_ENVIRONMENT": "staging",
            "AZURE_KEY_VAULT_URI": "https://example.vault.azure.net/",
            "AEGISAP_POSTGRES_DSN": "postgresql://user:pass@example",
        }
    )

    with pytest.raises(RuntimeError, match="AEGISAP_POSTGRES_DSN"):
        validate_security_posture(config)


def test_config_rejects_raw_resume_token_secret_outside_local() -> None:
    config = load_security_config(
        {
            "AEGISAP_ENVIRONMENT": "cloud",
            "AZURE_KEY_VAULT_URI": "https://example.vault.azure.net/",
            "AEGISAP_RESUME_TOKEN_SECRET": "raw-runtime-secret",
        }
    )

    with pytest.raises(RuntimeError, match="AEGISAP_RESUME_TOKEN_SECRET"):
        validate_security_posture(config)


def test_local_environment_can_use_local_resume_secret() -> None:
    config = load_security_config(
        {
            "AEGISAP_ENVIRONMENT": "local",
            "AEGISAP_RESUME_TOKEN_SECRET": "local-secret",
        }
    )

    validate_security_posture(config)
