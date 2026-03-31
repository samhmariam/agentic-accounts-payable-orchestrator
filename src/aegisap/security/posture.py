"""
Security posture check — produces a machine-readable report of all
RBAC contracts, forbidden env vars, and identity probes.

Used by Day 7 notebook and the CI gate runner (scripts/check_all_gates.py).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class PostureCheck:
    name: str
    passed: bool
    detail: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityPosture:
    checks: list[PostureCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def failed_checks(self) -> list[PostureCheck]:
        return [c for c in self.checks if not c.passed]

    def as_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "checks": [asdict(c) for c in self.checks],
            "failed_count": len(self.failed_checks),
        }


def _check_forbidden_env_vars() -> PostureCheck:
    from aegisap.security.config import FORBIDDEN_ENV_VARS  # type: ignore
    found = [v for v in FORBIDDEN_ENV_VARS if os.environ.get(v, "").strip()]
    return PostureCheck(
        name="no_forbidden_env_vars",
        passed=not found,
        detail="No forbidden env vars present" if not found else f"Found: {found}",
        evidence={"forbidden_vars_found": found},
    )


def _check_identity() -> PostureCheck:
    try:
        from azure.identity import DefaultAzureCredential  # type: ignore
        cred = DefaultAzureCredential(
            exclude_interactive_browser_credential=True)
        token = cred.get_token("https://management.azure.com/.default")
        import base64
        import json as _j
        payload_b64 = token.token.split(".")[1]
        padding = 4 - len(payload_b64) % 4
        payload = _j.loads(base64.urlsafe_b64decode(
            payload_b64 + "=" * padding))
        principal = payload.get("upn") or payload.get(
            "appid") or payload.get("oid", "?")
        return PostureCheck(
            name="managed_identity_active",
            passed=True,
            detail=f"Principal: {principal}",
            evidence={"principal": principal},
        )
    except Exception as exc:  # noqa: BLE001
        return PostureCheck(
            name="managed_identity_active",
            passed=False,
            detail=str(exc)[:120],
        )


def _check_search_local_auth() -> PostureCheck:
    """
    Attempt to reach the Search /serviceStats endpoint with a dummy admin key.
    A 401 means local auth is disabled (correct). A 200 means it's enabled (wrong).
    """
    endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT", "")
    if not endpoint:
        return PostureCheck(
            name="search_local_auth_disabled",
            passed=False,
            detail="AZURE_SEARCH_ENDPOINT not set — cannot verify",
        )
    try:
        import urllib.request as _req
        import ssl as _ssl
        url = f"{endpoint.rstrip('/')}/servicestats?api-version=2023-11-01"
        request = _req.Request(url, headers={"api-key": "dummy-key-for-probe"})
        ctx = _ssl.create_default_context()
        try:
            _req.urlopen(request, context=ctx, timeout=5)
            # Got 200 — local auth is ON (bad)
            return PostureCheck(
                name="search_local_auth_disabled",
                passed=False,
                detail="Search accepted a dummy API key — local auth may be enabled",
            )
        except Exception as http_exc:
            err_str = str(http_exc)
            if "401" in err_str or "403" in err_str:
                return PostureCheck(
                    name="search_local_auth_disabled",
                    passed=True,
                    detail="Search rejected dummy key (401/403) — local auth is disabled",
                )
            return PostureCheck(
                name="search_local_auth_disabled",
                passed=False,
                detail=f"Unexpected response: {err_str[:80]}",
            )
    except Exception as exc:  # noqa: BLE001
        return PostureCheck(
            name="search_local_auth_disabled",
            passed=False,
            detail=str(exc)[:120],
        )


def _check_key_vault_reachable() -> PostureCheck:
    uri = os.environ.get("AZURE_KEY_VAULT_URI", "")
    if not uri:
        return PostureCheck(
            name="key_vault_reachable",
            passed=False,
            detail="AZURE_KEY_VAULT_URI not set",
        )
    try:
        from azure.identity import DefaultAzureCredential  # type: ignore
        from azure.keyvault.secrets import SecretClient  # type: ignore
        cred = DefaultAzureCredential(
            exclude_interactive_browser_credential=True)
        client = SecretClient(vault_url=uri, credential=cred)
        next(iter(client.list_properties_of_secrets()), None)
        return PostureCheck(
            name="key_vault_reachable",
            passed=True,
            detail=f"Key Vault reachable at {uri}",
        )
    except Exception as exc:  # noqa: BLE001
        return PostureCheck(
            name="key_vault_reachable",
            passed=False,
            detail=str(exc)[:120],
        )


def run_posture_check() -> SecurityPosture:
    """Run all security posture checks and return a SecurityPosture report."""
    return SecurityPosture(
        checks=[
            _check_forbidden_env_vars(),
            _check_identity(),
            _check_search_local_auth(),
            _check_key_vault_reachable(),
        ]
    )
