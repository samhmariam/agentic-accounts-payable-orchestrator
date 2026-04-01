"""On-Behalf-Of (OBO) token exchange for delegated identity flows.

The AegisAP orchestrator receives a user access token from the front-end
(scoped to the AegisAP application) and exchanges it for a downstream
service token that still carries the user's `oid`, `upn`, and group claims.

This is required in Day 11 so that invoice approvals carry the human
approver's identity rather than the orchestrator's managed identity.

Usage::

    provider = OboTokenProvider.from_env()
    token = provider.exchange(user_access_token, scopes=["https://management.azure.com/.default"])

Environment variables required:
    AZURE_TENANT_ID       — Entra tenant for the AegisAP app registration
    AZURE_CLIENT_ID       — App registration client ID
    AZURE_CLIENT_SECRET   — App registration client secret (or use cert via AZURE_CLIENT_CERTIFICATE_PATH)
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import msal  # type: ignore[import-untyped]


@dataclass
class OboResult:
    """Result of a successful OBO token exchange."""

    access_token: str
    token_type: str
    expires_in: int
    scope: str
    oid: str | None = None  # populated from id_token_claims if available


class OboTokenProvider:
    """MSAL-based On-Behalf-Of token provider.

    The instance is intended to be long-lived (module-level singleton in
    production); MSAL handles its own cache internally.
    """

    def __init__(self, tenant_id: str, client_id: str, client_secret: str) -> None:
        self._client_id = client_id
        authority = f"https://login.microsoftonline.com/{tenant_id}"
        self._app = msal.ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=authority,
        )

    @classmethod
    def from_env(cls) -> "OboTokenProvider":
        """Create an instance from environment variables."""
        tenant_id = os.environ["AZURE_TENANT_ID"]
        client_id = os.environ["AZURE_CLIENT_ID"]
        client_secret = os.environ["AZURE_CLIENT_SECRET"]
        return cls(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)

    def exchange(self, user_assertion: str, scopes: list[str]) -> OboResult:
        """Exchange a user access token for a downstream access token via OBO.

        Args:
            user_assertion: The access token received from the authenticated user.
            scopes: Downstream scopes to request, e.g.
                    ``["api://<resource-app-id>/.default"]``.

        Returns:
            OboResult with the downstream access token.

        Raises:
            RuntimeError: If MSAL returns an error response.
        """
        result = self._app.acquire_token_on_behalf_of(
            user_assertion=user_assertion,
            scopes=scopes,
        )
        if "error" in result:
            raise RuntimeError(
                f"OBO token exchange failed: {result['error']} — "
                f"{result.get('error_description', 'no description')}"
            )
        claims = result.get("id_token_claims") or {}
        return OboResult(
            access_token=result["access_token"],
            token_type=result.get("token_type", "Bearer"),
            expires_in=result.get("expires_in", 0),
            scope=result.get("scope", " ".join(scopes)),
            oid=claims.get("oid"),
        )
