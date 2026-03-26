from __future__ import annotations

from aegisap.security.key_vault import get_resume_token_secret


def test_get_resume_token_secret_prefers_local_secret(monkeypatch) -> None:
    monkeypatch.setenv("AEGISAP_ENVIRONMENT", "local")
    monkeypatch.setenv("AEGISAP_RESUME_TOKEN_SECRET", "local-token")
    monkeypatch.delenv("AZURE_KEY_VAULT_URI", raising=False)

    assert get_resume_token_secret() == "local-token"


def test_get_resume_token_secret_uses_key_vault_in_cloud(monkeypatch) -> None:
    monkeypatch.setenv("AEGISAP_ENVIRONMENT", "cloud")
    monkeypatch.setenv("AZURE_KEY_VAULT_URI", "https://example.vault.azure.net/")
    monkeypatch.setenv("AEGISAP_RESUME_TOKEN_SECRET_NAME", "resume-secret")
    monkeypatch.delenv("AEGISAP_RESUME_TOKEN_SECRET", raising=False)
    monkeypatch.setattr("aegisap.security.key_vault.get_secret_value", lambda *args, **kwargs: "vault-token")

    assert get_resume_token_secret() == "vault-token"
