"""
Shared Azure service probing utilities used by all AegisAP marimo notebooks.

Each probe_* function returns a ProbeResult so notebooks can display
uniform status tiles without duplicating credential or error-handling logic.
"""
from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Self-contained path bootstrap — makes `aegisap` importable regardless of
# how marimo loads this module (venv, global Python, subprocess kernel, etc.)
# ---------------------------------------------------------------------------


def _bootstrap_path() -> None:
    # notebooks/_shared/ → notebooks/ → workspace root
    root = Path(__file__).resolve().parents[2]
    src = str(root / "src")
    if src not in sys.path:
        sys.path.insert(0, src)


_bootstrap_path()


@dataclass
class ProbeResult:
    service: str
    ok: bool
    latency_ms: int = 0
    detail: str = ""
    principal: str = ""


def probe_openai() -> ProbeResult:
    """Verify Azure OpenAI is reachable with DefaultAzureCredential."""
    t0 = time.monotonic()
    try:
        from azure.identity import get_bearer_token_provider, DefaultAzureCredential  # type: ignore
        from openai import AzureOpenAI  # type: ignore

        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
        api_version = os.environ.get(
            "AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        if not endpoint:
            return ProbeResult("Azure OpenAI", False, detail="AZURE_OPENAI_ENDPOINT not set")
        cred = DefaultAzureCredential(
            exclude_interactive_browser_credential=True)
        token_provider = get_bearer_token_provider(
            cred, "https://cognitiveservices.azure.com/.default"
        )
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
            api_version=api_version,
        )
        client.models.list()
        ms = int((time.monotonic() - t0) * 1000)
        return ProbeResult("Azure OpenAI", True, latency_ms=ms, detail=endpoint)
    except Exception as exc:  # noqa: BLE001
        ms = int((time.monotonic() - t0) * 1000)
        return ProbeResult("Azure OpenAI", False, latency_ms=ms, detail=str(exc)[:120])


def probe_search() -> ProbeResult:
    """Verify Azure AI Search is reachable with DefaultAzureCredential."""
    t0 = time.monotonic()
    try:
        from azure.identity import DefaultAzureCredential  # type: ignore
        from azure.search.documents.indexes import SearchIndexClient  # type: ignore

        endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT", "")
        if not endpoint:
            return ProbeResult("Azure AI Search", False, detail="AZURE_SEARCH_ENDPOINT not set")
        cred = DefaultAzureCredential(
            exclude_interactive_browser_credential=True)
        idx_client = SearchIndexClient(endpoint=endpoint, credential=cred)
        names = list(idx_client.list_index_names())
        ms = int((time.monotonic() - t0) * 1000)
        return ProbeResult("Azure AI Search", True, latency_ms=ms, detail=f"{len(names)} index(es)")
    except Exception as exc:  # noqa: BLE001
        ms = int((time.monotonic() - t0) * 1000)
        return ProbeResult("Azure AI Search", False, latency_ms=ms, detail=str(exc)[:120])


def probe_postgres() -> ProbeResult:
    """Verify PostgreSQL Flexible Server is reachable."""
    t0 = time.monotonic()
    try:
        import psycopg  # type: ignore

        dsn = os.environ.get("POSTGRES_DSN", "")
        if not dsn:
            return ProbeResult("PostgreSQL", False, detail="POSTGRES_DSN not set")
        with psycopg.connect(dsn, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        ms = int((time.monotonic() - t0) * 1000)
        return ProbeResult("PostgreSQL", True, latency_ms=ms, detail="SELECT 1 OK")
    except Exception as exc:  # noqa: BLE001
        ms = int((time.monotonic() - t0) * 1000)
        return ProbeResult("PostgreSQL", False, latency_ms=ms, detail=str(exc)[:120])


def probe_key_vault() -> ProbeResult:
    """Verify Key Vault is reachable and return the managed principal name."""
    t0 = time.monotonic()
    try:
        from azure.identity import DefaultAzureCredential  # type: ignore
        from azure.keyvault.secrets import SecretClient  # type: ignore

        uri = os.environ.get("AZURE_KEY_VAULT_URI", "")
        if not uri:
            return ProbeResult("Key Vault", False, detail="AZURE_KEY_VAULT_URI not set")
        cred = DefaultAzureCredential(
            exclude_interactive_browser_credential=True)
        client = SecretClient(vault_url=uri, credential=cred)
        # List (up to 1) secret names to confirm RBAC works — never reads values
        next(iter(client.list_properties_of_secrets()), None)
        ms = int((time.monotonic() - t0) * 1000)
        return ProbeResult("Key Vault", True, latency_ms=ms, detail=uri)
    except Exception as exc:  # noqa: BLE001
        ms = int((time.monotonic() - t0) * 1000)
        return ProbeResult("Key Vault", False, latency_ms=ms, detail=str(exc)[:120])


def probe_identity() -> ProbeResult:
    """Return the identity principal name currently used by DefaultAzureCredential."""
    t0 = time.monotonic()
    try:
        from azure.identity import DefaultAzureCredential  # type: ignore

        cred = DefaultAzureCredential(
            exclude_interactive_browser_credential=True)
        token = cred.get_token("https://management.azure.com/.default")
        ms = int((time.monotonic() - t0) * 1000)
        # Decode JWT claims (no verification — display only)
        import base64
        import json as _json
        payload_b64 = token.token.split(".")[1]
        padding = 4 - len(payload_b64) % 4
        payload = _json.loads(base64.urlsafe_b64decode(
            payload_b64 + "=" * padding))
        principal = payload.get("upn") or payload.get(
            "appid") or payload.get("oid", "unknown")
        return ProbeResult("Identity", True, latency_ms=ms, principal=principal, detail=principal)
    except Exception as exc:  # noqa: BLE001
        ms = int((time.monotonic() - t0) * 1000)
        return ProbeResult("Identity", False, latency_ms=ms, detail=str(exc)[:120])


# Inlined from aegisap.security.config — avoids importing pydantic at probe time
_FORBIDDEN_ENV_VARS: frozenset[str] = frozenset({
    "SEARCH_ADMIN_KEY",
    "SEARCH_QUERY_KEY",
    "AZURE_SEARCH_ADMIN_KEY",
    "AZURE_SEARCH_QUERY_KEY",
    "AZURE_OPENAI_API_KEY",
    "OPENAI_API_KEY",
    "AZURE_STORAGE_KEY",
    "AZURE_STORAGE_CONNECTION_STRING",
    "LANGSMITH_API_KEY",
})


def probe_forbidden_env_vars() -> list[str]:
    """Return any forbidden environment variable names that are currently set."""
    return [v for v in _FORBIDDEN_ENV_VARS if os.environ.get(v, "").strip()]


def run_all_probes(track: str = "core") -> list[ProbeResult]:
    """Run probes appropriate for the chosen provisioning track."""
    results = [probe_identity(), probe_openai(), probe_search()]
    if track == "full":
        results += [probe_postgres(), probe_key_vault()]
    return results
