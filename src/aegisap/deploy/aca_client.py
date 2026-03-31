"""
Azure Container Apps thin client.

Uses the Azure Resource Manager REST API via ``azure-identity``
(``DefaultAzureCredential``) — no extra SDK package required.

Typical usage::

    client = AcaClient.from_env()
    health = client.health_check()
    if health.is_ready:
        client.set_traffic(active_revision=health.latest_revision, weight=100)
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from azure.identity import DefaultAzureCredential

_ARM_SCOPE = "https://management.azure.com/.default"
_ARM_BASE = "https://management.azure.com"
_ACA_API = "2024-03-01"


@dataclass
class RevisionHealth:
    app_name: str
    app_url: str
    latest_revision: str
    provision_state: str
    is_ready: bool
    status_code: int | None  # HTTP probe result


def _arm_get(path: str, subscription_id: str) -> dict[str, Any]:
    """Issue an authenticated GET to the ARM REST API."""
    cred = DefaultAzureCredential()
    token = cred.get_token(_ARM_SCOPE).token
    url = f"{_ARM_BASE}{path}?api-version={_ACA_API}"
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
        return json.loads(resp.read())


def _arm_patch(path: str, body: dict[str, Any]) -> dict[str, Any]:
    """Issue an authenticated PATCH to the ARM REST API."""
    cred = DefaultAzureCredential()
    token = cred.get_token(_ARM_SCOPE).token
    url = f"{_ARM_BASE}{path}?api-version={_ACA_API}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method="PATCH",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
        return json.loads(resp.read())


class AcaClient:
    """Minimal client for Azure Container Apps REST operations."""

    def __init__(
        self,
        subscription_id: str,
        resource_group: str,
        app_name: str,
    ) -> None:
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.app_name = app_name

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_env(cls) -> "AcaClient":
        """Build from environment variables.

        Required env vars:
        - ``AZURE_SUBSCRIPTION_ID``
        - ``AZURE_RESOURCE_GROUP``
        - ``AZURE_CONTAINER_APP_NAME``
        """
        sub = os.environ["AZURE_SUBSCRIPTION_ID"]
        rg = os.environ["AZURE_RESOURCE_GROUP"]
        name = os.environ["AZURE_CONTAINER_APP_NAME"]
        return cls(subscription_id=sub, resource_group=rg, app_name=name)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _resource_path(self) -> str:
        return (
            f"/subscriptions/{self.subscription_id}"
            f"/resourceGroups/{self.resource_group}"
            f"/providers/Microsoft.App/containerApps/{self.app_name}"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_app(self) -> dict[str, Any]:
        """Return the full ARM resource representation for this Container App."""
        return _arm_get(self._resource_path(), self.subscription_id)

    def health_check(self) -> RevisionHealth:
        """Return basic health metadata and probe the /health endpoint."""
        app = self.get_app()
        props = app.get("properties", {})
        latest_rev = props.get("latestRevisionName", "")
        provision_state = props.get("provisioningState", "unknown")
        app_url = props.get("configuration", {}).get(
            "ingress", {}
        ).get("fqdn", "")
        if app_url:
            app_url = f"https://{app_url}"

        status_code: int | None = None
        if app_url:
            probe_url = f"{app_url}/health"
            try:
                req = urllib.request.Request(probe_url, method="GET")  # noqa: S310
                with urllib.request.urlopen(req, timeout=10) as r:  # noqa: S310
                    status_code = r.status
            except urllib.error.HTTPError as exc:
                status_code = exc.code
            except Exception:
                pass

        return RevisionHealth(
            app_name=self.app_name,
            app_url=app_url,
            latest_revision=latest_rev,
            provision_state=provision_state,
            is_ready=(provision_state == "Succeeded" and status_code == 200),
            status_code=status_code,
        )

    def set_traffic(
        self,
        active_revision: str,
        weight: int = 100,
    ) -> dict[str, Any]:
        """Set 100 % traffic to ``active_revision``."""
        body = {
            "properties": {
                "configuration": {
                    "ingress": {
                        "traffic": [
                            {
                                "revisionName": active_revision,
                                "weight": weight,
                                "latestRevision": False,
                            }
                        ]
                    }
                }
            }
        }
        return _arm_patch(self._resource_path(), body)
