#!/usr/bin/env python3
"""
Environment verification script.

Run before local development or CI smoke tests to confirm the required
environment variables are set and the backing Azure services are reachable
through DefaultAzureCredential.

Usage:
    python scripts/verify_env.py --track core
    python scripts/verify_env.py --track core --env
    python scripts/verify_env.py --track full
    python scripts/verify_env.py --track full --include-langsmith

Prerequisites: production dependencies must be installed
    uv sync --dev
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlparse

from aegisap.security.config import load_security_config
from aegisap.security.policy import validate_security_posture


CORE_REQUIRED_ENV_VARS = [
    "AZURE_SUBSCRIPTION_ID",
    "AZURE_RESOURCE_GROUP",
    "AZURE_LOCATION",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_VERSION",
    "AZURE_OPENAI_CHAT_DEPLOYMENT",
    "AZURE_SEARCH_ENDPOINT",
    "AZURE_SEARCH_INDEX",
    "AZURE_STORAGE_ACCOUNT_URL",
    "AZURE_STORAGE_CONTAINER",
]

FULL_ONLY_ENV_VARS = [
    "AZURE_POSTGRES_HOST",
    "AZURE_POSTGRES_PORT",
    "AZURE_POSTGRES_DB",
    "AZURE_POSTGRES_USER",
    "AZURE_KEY_VAULT_URI",
    "APPLICATIONINSIGHTS_CONNECTION_STRING",
]

OPTIONAL_LANGSMITH_ENV_VARS = [
    "LANGSMITH_API_KEY",
    "LANGSMITH_PROJECT",
]

PASS = "PASS"
FAIL = "FAIL"

POSTGRES_SCOPE = "https://ossrdbms-aad.database.windows.net/.default"
OPENAI_SCOPE = "https://cognitiveservices.azure.com/.default"


def result(name: str, status: str, detail: str) -> dict[str, str]:
    return {"check": name, "status": status, "detail": detail}


def print_results(results: list[dict[str, str]]) -> int:
    width = max(len(r["check"]) for r in results) + 2
    overall_fail = any(r["status"] == FAIL for r in results)
    print("\nEnvironment Verification\n" + "=" * 80)
    for item in results:
        print(f"{item['check']:<{width}} {item['status']:<5} {item['detail']}")
    print("=" * 80)
    return 1 if overall_fail else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--track",
        choices=["core", "full"],
        default="core",
        help="Day 0 track to verify. Default: core",
    )
    parser.add_argument("--env", action="store_true", help="validate environment variables only")
    parser.add_argument(
        "--include-langsmith",
        action="store_true",
        help="require and verify LangSmith connectivity in addition to Azure checks",
    )
    return parser.parse_args()


def require_env(required_keys: list[str]) -> list[dict[str, str]]:
    results = []
    for key in required_keys:
        value = os.getenv(key)
        if value:
            results.append(result(f"env:{key}", PASS, "present"))
        else:
            results.append(result(f"env:{key}", FAIL, "missing"))
    return results


def check_security_posture() -> dict[str, str]:
    try:
        config = load_security_config()
        validate_security_posture(config)
        return result(
            "security_posture",
            PASS,
            f"environment={config.environment}, credential_mode={config.credential_mode}",
        )
    except Exception as exc:
        return result("security_posture", FAIL, str(exc))


def langsmith_requested(args: argparse.Namespace) -> bool:
    if args.include_langsmith:
        return True

    present = [bool(os.getenv(key)) for key in OPTIONAL_LANGSMITH_ENV_VARS]
    return all(present)


def required_env_for_track(track: str) -> list[str]:
    if track == "full":
        return CORE_REQUIRED_ENV_VARS + FULL_ONLY_ENV_VARS
    return CORE_REQUIRED_ENV_VARS


def build_credential() -> Any:
    from azure.identity import DefaultAzureCredential

    try:
        return DefaultAzureCredential(exclude_interactive_browser_credential=True)
    except ValueError as exc:
        print(
            f"Falling back to Azure CLI credential flow for local verification: {exc}",
            file=sys.stderr,
        )
        return DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_interactive_browser_credential=True,
        )


def check_openai(credential: Any) -> dict[str, str]:
    deployment = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]
    try:
        from azure.identity import get_bearer_token_provider
        from openai import AzureOpenAI

        token_provider = get_bearer_token_provider(credential, OPENAI_SCOPE)
        client = AzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            azure_ad_token_provider=token_provider,
            api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        )
        client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": "Reply with OK"}],
            max_tokens=1,
        )
        return result("azure_openai", PASS, f"deployment '{deployment}' reachable with DefaultAzureCredential")
    except Exception as exc:  # pragma: no cover - SDK exceptions vary
        message = str(exc)
        if "DeploymentNotFound" in message or "404" in message:
            message += " | Check the OpenAI chat deployment name and confirm scripts/provision-core.ps1 or scripts/provision-full.ps1 created it."
        return result("azure_openai", FAIL, message)


def check_search(credential: Any) -> dict[str, str]:
    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"].rstrip("/")
    index_name = os.environ["AZURE_SEARCH_INDEX"]
    try:
        from azure.search.documents.indexes import SearchIndexClient

        client = SearchIndexClient(endpoint=endpoint, credential=credential)
        visible_indexes = list(client.list_index_names())
        if index_name not in visible_indexes:
            detail = (
                f"service reachable with RBAC, but target index '{index_name}' is not visible. "
                "Run the provisioning script again or create the starter index."
            )
            return result("azure_search", FAIL, detail)
        detail = f"service reachable with RBAC, {len(visible_indexes)} index(es) visible; target index '{index_name}' visible"
        return result("azure_search", PASS, detail)
    except Exception as exc:  # pragma: no cover - SDK exceptions vary
        message = str(exc)
        if "403" in message or "Forbidden" in message:
            message += " | Check Search Service Contributor and Search Index Data Contributor on the search service."
        return result("azure_search", FAIL, message)


def check_postgres(credential: Any) -> dict[str, str]:
    import psycopg

    conninfo = (
        f"host={os.environ['AZURE_POSTGRES_HOST']} "
        f"port={os.environ['AZURE_POSTGRES_PORT']} "
        f"dbname={os.environ['AZURE_POSTGRES_DB']} "
        f"user={os.environ['AZURE_POSTGRES_USER']} "
        f"password={credential.get_token(POSTGRES_SCOPE).token} "
        "sslmode=require"
    )
    try:
        with psycopg.connect(conninfo, connect_timeout=10) as conn:
            with conn.cursor() as cur:
                cur.execute("select current_user, current_database(), version();")
                current_user, db_name, version = cur.fetchone()
        detail = f"connected to '{db_name}' as '{current_user}' ({version.split(',')[0]})"
        return result("postgres", PASS, detail)
    except Exception as exc:
        message = str(exc)
        if "password authentication failed" in message.lower():
            message += " | Check PostgreSQL Microsoft Entra admin setup and the AZURE_POSTGRES_USER principal."
        return result("postgres", FAIL, message)


def check_storage(credential: Any) -> dict[str, str]:
    try:
        from azure.storage.blob import BlobServiceClient

        service_client = BlobServiceClient(
            account_url=os.environ["AZURE_STORAGE_ACCOUNT_URL"],
            credential=credential,
        )
        container = os.environ["AZURE_STORAGE_CONTAINER"]
        client = service_client.get_container_client(container)
        client.get_container_properties()
        return result("blob_storage", PASS, f"container '{container}' reachable with Azure RBAC")
    except Exception as exc:  # pragma: no cover - SDK exceptions vary
        message = str(exc)
        if "403" in message or "AuthorizationPermissionMismatch" in message or "Forbidden" in message:
            message += " | Check Storage Blob Data Contributor on the storage account."
        return result("blob_storage", FAIL, message)


def check_key_vault(credential: Any) -> dict[str, str]:
    try:
        from azure.keyvault.secrets import SecretClient

        client = SecretClient(vault_url=os.environ["AZURE_KEY_VAULT_URI"], credential=credential)
        next(iter(client.list_properties_of_secrets()), None)
        return result("key_vault", PASS, "vault reachable with DefaultAzureCredential")
    except Exception as exc:  # pragma: no cover - SDK exceptions vary
        return result("key_vault", FAIL, str(exc))


def _run_az_json(*args: str) -> Any:
    completed = subprocess.run(
        ["az", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or "Azure CLI command failed"
        raise RuntimeError(message)
    output = completed.stdout.strip()
    return json.loads(output) if output else None


def _run_az_text(*args: str) -> str:
    completed = subprocess.run(
        ["az", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or "Azure CLI command failed"
        raise RuntimeError(message)
    return completed.stdout.strip()


def check_search_local_auth_disabled() -> dict[str, str]:
    try:
        endpoint = os.environ["AZURE_SEARCH_ENDPOINT"].rstrip("/")
        search_name = urlparse(endpoint).netloc.split(".")[0]
        value = _run_az_text(
            "search",
            "service",
            "show",
            "--name",
            search_name,
            "--resource-group",
            os.environ["AZURE_RESOURCE_GROUP"],
            "--query",
            "disableLocalAuth",
            "-o",
            "tsv",
        ).lower()
        if value == "true":
            return result("search_local_auth", PASS, "Azure AI Search local auth disabled")
        return result("search_local_auth", FAIL, "Azure AI Search local auth is still enabled")
    except Exception as exc:
        return result("search_local_auth", FAIL, str(exc))


def check_key_vault_diagnostics() -> dict[str, str]:
    try:
        vault_name = urlparse(os.environ["AZURE_KEY_VAULT_URI"]).netloc.split(".")[0]
        vault_id = _run_az_text(
            "keyvault",
            "show",
            "--name",
            vault_name,
            "--resource-group",
            os.environ["AZURE_RESOURCE_GROUP"],
            "--query",
            "id",
            "-o",
            "tsv",
        )
        payload = _run_az_json(
            "monitor",
            "diagnostic-settings",
            "list",
            "--resource",
            vault_id,
            "-o",
            "json",
        )
        settings = payload.get("value", []) if isinstance(payload, dict) else payload or []
        for setting in settings:
            logs = setting.get("logs", [])
            has_audit = any(
                log.get("category") == "AuditEvent" and bool(log.get("enabled"))
                for log in logs
            )
            if has_audit and setting.get("workspaceId"):
                return result(
                    "key_vault_diagnostics",
                    PASS,
                    f"AuditEvent logs enabled and routed to workspace '{setting['workspaceId']}'",
                )
        return result(
            "key_vault_diagnostics",
            FAIL,
            "No Key Vault diagnostic setting was found with AuditEvent logs enabled to Log Analytics.",
        )
    except Exception as exc:
        return result("key_vault_diagnostics", FAIL, str(exc))


def check_langsmith() -> dict[str, str]:
    try:
        from langsmith import Client as LangSmithClient

        client = LangSmithClient(
            api_key=os.environ["LANGSMITH_API_KEY"],
            api_url="https://api.smith.langchain.com",
        )
        next(client.list_projects(limit=1), None)
        return result("langsmith", PASS, "API reachable")
    except Exception as exc:
        return result("langsmith", FAIL, str(exc))


def parse_app_insights_connection_string(connection_string: str) -> dict[str, str]:
    parts: dict[str, str] = {}
    for item in connection_string.split(";"):
        if "=" in item:
            key, value = item.split("=", 1)
            parts[key] = value
    return parts


def check_app_insights() -> dict[str, str]:
    try:
        parts = parse_app_insights_connection_string(os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"])
        ingestion = parts.get("IngestionEndpoint")
        if not ingestion:
            return result("app_insights", FAIL, "missing IngestionEndpoint in connection string")
        parsed = urlparse(ingestion)
        if not parsed.scheme or not parsed.netloc:
            return result("app_insights", FAIL, "invalid ingestion endpoint")
        req = urllib.request.Request(ingestion.rstrip("/") + "/")
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                response.read()
            return result("app_insights", PASS, f"endpoint '{parsed.netloc}' reachable")
        except urllib.error.HTTPError as exc:
            if exc.code in (400, 401, 403, 404):
                return result("app_insights", PASS, f"endpoint '{parsed.netloc}' reachable (HTTP {exc.code})")
            return result("app_insights", FAIL, f"HTTP {exc.code}")
    except Exception as exc:
        return result("app_insights", FAIL, str(exc))


def main() -> int:
    args = parse_args()
    results = []
    results.extend(require_env(required_env_for_track(args.track)))
    results.append(check_security_posture())

    if langsmith_requested(args):
        results.extend(require_env(OPTIONAL_LANGSMITH_ENV_VARS))

    if any(item["status"] == FAIL for item in results) or args.env:
        return print_results(results)

    credential = build_credential()

    results.append(check_openai(credential))
    results.append(check_search(credential))
    results.append(check_storage(credential))

    if args.track == "full":
        results.append(check_postgres(credential))
        results.append(check_key_vault(credential))
        results.append(check_app_insights())
        results.append(check_key_vault_diagnostics())

    results.append(check_search_local_auth_disabled())

    if langsmith_requested(args):
        results.append(check_langsmith())

    return print_results(results)


if __name__ == "__main__":
    sys.exit(main())
