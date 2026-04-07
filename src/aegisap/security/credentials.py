from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from aegisap.security.config import load_security_config
from aegisap.security.policy import validate_security_posture

# Foundry uses the ai.azure.com audience even when clients call the
# OpenAI-compatible endpoint on *.openai.azure.com.
FOUNDRY_INFERENCE_SCOPE = "https://ai.azure.com/.default"


def _day0_state_candidates() -> list[Path]:
    repo_root = Path(__file__).resolve().parents[3]
    return [
        repo_root / ".day0" / "full.json",
        repo_root / ".day0" / "core.json",
    ]


@lru_cache(maxsize=1)
def _load_local_day0_environment() -> dict[str, str]:
    config = load_security_config()
    if not config.is_local_like:
        return {}

    for state_path in _day0_state_candidates():
        if not state_path.exists():
            continue
        payload = json.loads(state_path.read_text())
        environment = payload.get("environment", {})
        loaded: dict[str, str] = {}
        for key, value in environment.items():
            text = str(value).strip() if value is not None else ""
            if not text:
                continue
            if not os.environ.get(key, "").strip():
                os.environ[key] = text
                loaded[key] = text
        return loaded
    return {}


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        _load_local_day0_environment()
        value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required environment variable: {name}")
    return value


@lru_cache(maxsize=1)
def get_token_credential():
    from azure.identity import DefaultAzureCredential

    config = load_security_config()
    validate_security_posture(config)
    if config.is_local_like:
        try:
            return DefaultAzureCredential(exclude_interactive_browser_credential=True)
        except ValueError:
            return DefaultAzureCredential(
                exclude_environment_credential=True,
                exclude_interactive_browser_credential=True,
            )
    return DefaultAzureCredential(exclude_interactive_browser_credential=True)


@lru_cache(maxsize=1)
def get_openai_client():
    from azure.identity import get_bearer_token_provider
    from openai import AzureOpenAI

    token_provider = get_bearer_token_provider(get_token_credential(), FOUNDRY_INFERENCE_SCOPE)
    return AzureOpenAI(
        azure_endpoint=_required_env("AZURE_OPENAI_ENDPOINT"),
        azure_ad_token_provider=token_provider,
        api_version=_required_env("AZURE_OPENAI_API_VERSION"),
    )


def get_search_query_client(*, endpoint: str, index_name: str):
    from azure.search.documents import SearchClient

    return SearchClient(
        endpoint=endpoint.rstrip("/"),
        index_name=index_name,
        credential=get_token_credential(),
    )


def get_blob_service_client(*, account_url: str):
    from azure.storage.blob import BlobServiceClient

    return BlobServiceClient(account_url=account_url, credential=get_token_credential())


def get_key_vault_secret_client(*, vault_url: str | None = None):
    from azure.keyvault.secrets import SecretClient

    resolved_vault_url = (vault_url or _required_env("AZURE_KEY_VAULT_URI")).rstrip("/")
    return SecretClient(vault_url=resolved_vault_url, credential=get_token_credential())


def security_runtime_mode() -> str:
    config = load_security_config()
    validate_security_posture(config)
    return config.credential_mode


def redact_credential_summary() -> dict[str, Any]:
    config = load_security_config()
    validate_security_posture(config)
    return {
        "environment": config.environment,
        "credential_mode": config.credential_mode,
        "key_vault_enabled": bool(config.key_vault_uri),
    }
