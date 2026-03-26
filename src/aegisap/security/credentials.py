from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from aegisap.security.config import load_security_config
from aegisap.security.policy import validate_security_posture

OPENAI_SCOPE = "https://cognitiveservices.azure.com/.default"


def _required_env(name: str) -> str:
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

    token_provider = get_bearer_token_provider(get_token_credential(), OPENAI_SCOPE)
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

