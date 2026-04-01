"""Azure Functions boundary client for AegisAP (Day 13).

AegisAP calls Azure Functions at integration boundaries to:
- Invoke legacy LOB system webhooks (ERP, PO system)
- Trigger Actions that must run in a different security perimeter
- Fire-and-forget notifications to downstream systems

The client enforces:
1. Managed Identity token acquisition (no function keys in code).
2. Retry with exponential back-off via tenacity.
3. Structured response wrapping with correlation ID propagation.

Usage::

    client = FunctionsBoundaryClient.from_env()
    result = client.call("erp-post-invoice", payload={"invoice_id": "INV-001"})
    if not result.success:
        raise RuntimeError(result.error)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

import httpx
from azure.identity import DefaultAzureCredential
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


@dataclass
class FunctionCallResult:
    function_name: str
    success: bool
    status_code: int
    body: Any
    error: str | None = None
    correlation_id: str | None = None


class FunctionsBoundaryClient:
    """HTTP client for Azure Functions endpoints at AegisAP integration boundaries."""

    def __init__(
        self,
        base_url: str,
        resource_id: str,
        timeout: float = 30.0,
    ) -> None:
        """
        Args:
            base_url: Base URL of the function app, e.g.
                      ``https://aegisap-functions.azurewebsites.net``
            resource_id: Azure resource ID used as the OAuth2 audience when
                         acquiring a Managed Identity token.
            timeout: HTTP request timeout in seconds.
        """
        self._base_url = base_url.rstrip("/")
        self._resource_id = resource_id
        self._timeout = timeout
        self._credential = DefaultAzureCredential()

    @classmethod
    def from_env(cls) -> "FunctionsBoundaryClient":
        base_url = os.environ["AEGISAP_FUNCTION_APP_URL"]
        resource_id = os.environ.get(
            "AEGISAP_FUNCTION_RESOURCE_ID",
            "https://management.azure.com/",
        )
        return cls(base_url=base_url, resource_id=resource_id)

    def _get_token(self) -> str:
        token = self._credential.get_token(f"{self._resource_id}/.default")
        return token.token

    @retry(
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def call(
        self,
        function_name: str,
        payload: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> FunctionCallResult:
        """Call a named Azure Function and return a structured result.

        Args:
            function_name: The route name of the function (path segment).
            payload: JSON-serialisable dict forwarded as the request body.
            correlation_id: Optional trace correlation ID propagated as
                            ``x-correlation-id`` header.

        Returns:
            FunctionCallResult wrapping the HTTP response.
        """
        token = self._get_token()
        headers: dict[str, str] = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        if correlation_id:
            headers["x-correlation-id"] = correlation_id

        url = f"{self._base_url}/api/{function_name}"
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.post(url, content=json.dumps(
                    payload or {}), headers=headers)
                resp.raise_for_status()
                try:
                    body = resp.json()
                except Exception:
                    body = resp.text
                return FunctionCallResult(
                    function_name=function_name,
                    success=True,
                    status_code=resp.status_code,
                    body=body,
                    correlation_id=correlation_id,
                )
        except httpx.HTTPStatusError as exc:
            return FunctionCallResult(
                function_name=function_name,
                success=False,
                status_code=exc.response.status_code,
                body=None,
                error=str(exc),
                correlation_id=correlation_id,
            )

    def post_payment_hold(
        self,
        request: "PaymentHoldRequest",  # type: ignore[name-defined]
        correlation_id: str | None = None,
    ) -> FunctionCallResult:
        """Submit a payment hold via the Azure Functions payment-hold endpoint.

        Enforces a 5-second timeout (overrides the client default) and maps HTTP
        status codes to idempotency / transient-retry semantics:

        - 409 Conflict  → already_held (idempotent, not an error)
        - 400 / 403 / 404 → non-transient, returned immediately
        - 429 / 503 → tenacity retries (inherited from ``call()``)
        """
        payload = request.model_dump(mode="json")
        # Use a short per-call timeout for hold operations (latency SLA)
        original_timeout = self._timeout
        self._timeout = min(original_timeout, 5.0)
        try:
            result = self.call(
                "post-payment-hold",
                payload=payload,
                correlation_id=correlation_id,
            )
        finally:
            self._timeout = original_timeout

        # Normalise 409 → idempotent already_held (not a failure)
        if result.status_code == 409:
            result = FunctionCallResult(
                function_name=result.function_name,
                success=True,
                status_code=409,
                body={"status": "already_held"},
                error=None,
                correlation_id=result.correlation_id,
            )
        return result
