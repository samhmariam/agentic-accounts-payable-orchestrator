from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from aegisap.security import credentials


def test_required_env_bootstraps_from_local_day0_state(monkeypatch, tmp_path) -> None:
    state_path = tmp_path / "core.json"
    state_path.write_text(
        json.dumps(
            {
                "environment": {
                    "AZURE_OPENAI_ENDPOINT": "https://example.openai.azure.com/",
                    "AZURE_OPENAI_API_VERSION": "2024-08-01-preview",
                }
            }
        )
    )

    monkeypatch.setenv("AEGISAP_ENVIRONMENT", "local")
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_VERSION", raising=False)
    monkeypatch.setattr(credentials, "_day0_state_candidates", lambda: [state_path])
    credentials._load_local_day0_environment.cache_clear()

    assert credentials._required_env("AZURE_OPENAI_ENDPOINT") == "https://example.openai.azure.com/"
    assert credentials._required_env("AZURE_OPENAI_API_VERSION") == "2024-08-01-preview"

    credentials._load_local_day0_environment.cache_clear()


def test_required_env_does_not_bootstrap_day0_state_in_cloud(monkeypatch, tmp_path) -> None:
    state_path = tmp_path / "core.json"
    state_path.write_text(
        json.dumps(
            {
                "environment": {
                    "AZURE_OPENAI_ENDPOINT": "https://example.openai.azure.com/",
                }
            }
        )
    )

    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.setattr(credentials, "_day0_state_candidates", lambda: [state_path])
    monkeypatch.setattr(credentials, "load_security_config", lambda: SimpleNamespace(is_local_like=False))
    credentials._load_local_day0_environment.cache_clear()

    with pytest.raises(RuntimeError, match="AZURE_OPENAI_ENDPOINT"):
        credentials._required_env("AZURE_OPENAI_ENDPOINT")

    credentials._load_local_day0_environment.cache_clear()
