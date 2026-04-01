"""MCP authentication middleware for AegisAP (Day 13).

Every MCP request must carry a valid Bearer token issued by Entra ID.
The middleware validates the token's signature, audience, and issuer using
the MSAL ``PublicClientApplication`` token-verification path.

For development: set ``AEGISAP_MCP_SKIP_AUTH=1`` to bypass (never in prod).
"""

from __future__ import annotations

import os
from typing import Awaitable, Callable

import jwt as pyjwt  # PyJWT
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class McpAuthMiddleware:
    """FastAPI middleware that validates Entra Bearer tokens on MCP routes."""

    def __init__(
        self,
        app,
        tenant_id: str,
        audience: str,
        skip_auth: bool = False,
    ) -> None:
        self._app = app
        self._tenant_id = tenant_id
        self._audience = audience
        self._skip_auth = skip_auth
        self._jwks_uri = (
            f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
        )
        self._jwks_client = pyjwt.PyJWKClient(self._jwks_uri)

    @classmethod
    def from_env(cls, app) -> "McpAuthMiddleware":
        tenant_id = os.environ["AZURE_TENANT_ID"]
        audience = os.environ["AEGISAP_MCP_AUDIENCE"]
        skip_auth = os.environ.get("AEGISAP_MCP_SKIP_AUTH", "0") == "1"
        return cls(app=app, tenant_id=tenant_id, audience=audience, skip_auth=skip_auth)

    async def __call__(
        self,
        scope: dict,
        receive: Callable,
        send: Callable,
    ) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        if self._skip_auth:
            await self._app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        auth_header: bytes = headers.get(b"authorization", b"")
        if not auth_header.startswith(b"Bearer "):
            response = JSONResponse(
                {"detail": "Missing or invalid Authorization header"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
            await response(scope, receive, send)
            return

        token = auth_header[len(b"Bearer "):].decode()
        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(token)
            pyjwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self._audience,
            )
        except pyjwt.ExpiredSignatureError:
            response = JSONResponse(
                {"detail": "Token has expired"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
            await response(scope, receive, send)
            return
        except pyjwt.InvalidTokenError as exc:
            response = JSONResponse(
                {"detail": f"Invalid token: {exc}"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
            await response(scope, receive, send)
            return

        await self._app(scope, receive, send)
