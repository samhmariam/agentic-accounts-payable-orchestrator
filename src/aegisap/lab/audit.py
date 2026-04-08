from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


PASS = "pass"
FAIL = "fail"
SKIP = "skip"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resolve_repo_root(repo_root: str | Path | None) -> Path:
    if repo_root is not None:
        return Path(repo_root)
    return Path(__file__).resolve().parents[3]


def _result(name: str, status: str, detail: str, **extra: Any) -> dict[str, Any]:
    payload = {"check": name, "status": status, "detail": detail}
    payload.update({key: value for key, value in extra.items() if value is not None})
    return payload


def _write_payload(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


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


def _resource_name_from_url(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc or parsed.path
    if not host:
        raise ValueError(f"Could not infer resource name from URL: {url!r}")
    return host.split(".")[0]


def _normalise_pna(value: Any) -> str:
    text = str(value or "").strip().lower()
    return text or "unknown"


def _check_search(resource_group: str) -> dict[str, Any]:
    endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT", "").strip()
    if not endpoint:
        return _result("search_posture", SKIP, "AZURE_SEARCH_ENDPOINT not set")

    name = _resource_name_from_url(endpoint)
    try:
        payload = _run_az_json(
            "search",
            "service",
            "show",
            "--name",
            name,
            "--resource-group",
            resource_group,
            "-o",
            "json",
        ) or {}
    except Exception as exc:
        return _result("search_posture", FAIL, str(exc), resource=name)

    public_network_access = _normalise_pna(payload.get("publicNetworkAccess"))
    disable_local_auth = payload.get("disableLocalAuth")
    failures: list[str] = []
    if public_network_access != "disabled":
        failures.append(f"publicNetworkAccess={public_network_access!r}")
    if disable_local_auth is not True:
        failures.append(f"disableLocalAuth={disable_local_auth!r}")

    return _result(
        "search_posture",
        PASS if not failures else FAIL,
        "Azure AI Search blocks public access and local auth."
        if not failures
        else "; ".join(failures),
        resource=name,
        public_network_access=public_network_access,
        disable_local_auth=disable_local_auth,
    )


def _check_openai(resource_group: str) -> dict[str, Any]:
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").strip()
    if not endpoint:
        return _result("openai_posture", SKIP, "AZURE_OPENAI_ENDPOINT not set")

    name = _resource_name_from_url(endpoint)
    try:
        payload = _run_az_json(
            "cognitiveservices",
            "account",
            "show",
            "--name",
            name,
            "--resource-group",
            resource_group,
            "-o",
            "json",
        ) or {}
    except Exception as exc:
        return _result("openai_posture", FAIL, str(exc), resource=name)

    props = payload.get("properties", {})
    public_network_access = _normalise_pna(
        props.get("publicNetworkAccess", payload.get("publicNetworkAccess"))
    )
    failures: list[str] = []
    if public_network_access != "disabled":
        failures.append(f"publicNetworkAccess={public_network_access!r}")

    return _result(
        "openai_posture",
        PASS if not failures else FAIL,
        "Azure OpenAI public network access is disabled."
        if not failures
        else "; ".join(failures),
        resource=name,
        public_network_access=public_network_access,
    )


def _check_storage(resource_group: str) -> dict[str, Any]:
    account_url = os.environ.get("AZURE_STORAGE_ACCOUNT_URL", "").strip()
    if not account_url:
        return _result("storage_posture", SKIP, "AZURE_STORAGE_ACCOUNT_URL not set")

    name = _resource_name_from_url(account_url)
    try:
        payload = _run_az_json(
            "storage",
            "account",
            "show",
            "--name",
            name,
            "--resource-group",
            resource_group,
            "-o",
            "json",
        ) or {}
    except Exception as exc:
        return _result("storage_posture", FAIL, str(exc), resource=name)

    public_network_access = _normalise_pna(payload.get("publicNetworkAccess"))
    allow_blob_public_access = payload.get("allowBlobPublicAccess")
    default_action = (payload.get("networkRuleSet") or {}).get("defaultAction")
    failures: list[str] = []
    if public_network_access != "disabled":
        failures.append(f"publicNetworkAccess={public_network_access!r}")
    if allow_blob_public_access is not False:
        failures.append(f"allowBlobPublicAccess={allow_blob_public_access!r}")

    return _result(
        "storage_posture",
        PASS if not failures else FAIL,
        "Storage account blocks public network access and blob public access."
        if not failures
        else "; ".join(failures),
        resource=name,
        public_network_access=public_network_access,
        allow_blob_public_access=allow_blob_public_access,
        default_action=default_action,
    )


def _check_key_vault(resource_group: str) -> dict[str, Any]:
    vault_uri = os.environ.get("AZURE_KEY_VAULT_URI", "").strip()
    if not vault_uri:
        return _result("key_vault_posture", SKIP, "AZURE_KEY_VAULT_URI not set")

    name = _resource_name_from_url(vault_uri)
    try:
        payload = _run_az_json(
            "keyvault",
            "show",
            "--name",
            name,
            "--resource-group",
            resource_group,
            "-o",
            "json",
        ) or {}
    except Exception as exc:
        return _result("key_vault_posture", FAIL, str(exc), resource=name)

    props = payload.get("properties", {})
    public_network_access = _normalise_pna(
        props.get("publicNetworkAccess", payload.get("publicNetworkAccess"))
    )
    default_action = (props.get("networkAcls") or {}).get("defaultAction")
    failures: list[str] = []
    if public_network_access != "disabled":
        failures.append(f"publicNetworkAccess={public_network_access!r}")

    return _result(
        "key_vault_posture",
        PASS if not failures else FAIL,
        "Key Vault public network access is disabled."
        if not failures
        else "; ".join(failures),
        resource=name,
        public_network_access=public_network_access,
        default_action=default_action,
    )


def run_production_audit(
    *,
    repo_root: str | Path | None = None,
    out_path: str | Path | None = None,
) -> dict[str, Any]:
    root = _resolve_repo_root(repo_root)
    target = Path(out_path) if out_path is not None else root / "build" / "audit" / "production_audit.json"
    resource_group = os.environ.get("AZURE_RESOURCE_GROUP", "").strip()

    if not resource_group:
        return _write_payload(
            target,
            {
                "generated_at": _utc_now_iso(),
                "resource_group": None,
                "training_artifact": True,
                "authoritative_evidence": False,
                "all_passed": False,
                "checks": [],
                "note": "Preview mode: set AZURE_RESOURCE_GROUP and relevant AZURE_* endpoints to audit live Azure posture.",
            },
        )

    checks = [
        _check_search(resource_group),
        _check_openai(resource_group),
        _check_storage(resource_group),
        _check_key_vault(resource_group),
    ]
    actionable = [check for check in checks if check["status"] != SKIP]
    failed = [check for check in actionable if check["status"] == FAIL]
    authoritative = bool(actionable)

    note = None
    if not authoritative:
        note = "No live resource endpoints were configured, so the audit could not interrogate Azure."

    return _write_payload(
        target,
        {
            "generated_at": _utc_now_iso(),
            "resource_group": resource_group,
            "training_artifact": not authoritative,
            "authoritative_evidence": authoritative,
            "all_passed": authoritative and not failed,
            "checks": checks,
            "note": note,
        },
    )
