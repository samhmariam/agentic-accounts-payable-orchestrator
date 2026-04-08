"""AegisAP MCP server — FastAPI application factory (Day 13).

Creates a FastAPI app that exposes AegisAP domain tools as MCP-compatible
HTTP endpoints.  The server is wrapped with McpAuthMiddleware so every
request must carry a valid Entra Bearer token.

Start the server::

    uvicorn aegisap.mcp.server:app --host 0.0.0.0 --port 8080

Or run it programmatically::

    app = create_mcp_app()
    import uvicorn; uvicorn.run(app, host="0.0.0.0", port=8080)
"""

from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from .auth import McpAuthMiddleware
from .lob_adapter import LobAdapter
from .schemas import (
    InvoiceQueryRequest,
    InvoiceQueryResponse,
    ListPendingApprovalsRequest,
    McpCapabilities,
    PaymentHoldRequest,
    PaymentHoldResponse,
    HoldStatus,
    VendorPolicyRequest,
    VendorPolicyResponse,
)


def create_mcp_app(use_stubs: bool | None = None) -> FastAPI:
    """Create and configure the AegisAP MCP FastAPI application."""
    fast_app = FastAPI(
        title="AegisAP MCP Server",
        version="1.0.0",
        description="Model Context Protocol server exposing AegisAP invoice-processing tools.",
    )

    adapter = LobAdapter(use_stubs=use_stubs)

    @fast_app.get("/capabilities", response_model=McpCapabilities)
    async def capabilities() -> McpCapabilities:
        """Return the server's MCP capabilities advertisement."""
        return McpCapabilities()

    @fast_app.post("/tools/query_invoice_status", response_model=InvoiceQueryResponse)
    async def query_invoice_status(req: InvoiceQueryRequest) -> InvoiceQueryResponse:
        """Retrieve the current status of an invoice by ID."""
        response = adapter.query_invoice_status(req)
        if response.error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=response.error,
            )
        return response

    @fast_app.post("/tools/list_pending_approvals", response_model=list[InvoiceQueryResponse])
    async def list_pending_approvals(
        req: ListPendingApprovalsRequest,
    ) -> list[InvoiceQueryResponse]:
        """List invoices pending approval for a specific approver."""
        return adapter.list_pending_approvals(req)

    @fast_app.post("/tools/get_vendor_policy", response_model=VendorPolicyResponse)
    async def get_vendor_policy(req: VendorPolicyRequest) -> VendorPolicyResponse:
        """Retrieve the payment-approval policy for a vendor."""
        response = adapter.get_vendor_policy(req)
        if response.policy_version == "unknown":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor policy {req.vendor_id!r} not found.",
            )
        return response

    @fast_app.post("/tools/submit_payment_hold", response_model=PaymentHoldResponse)
    async def submit_payment_hold(req: PaymentHoldRequest) -> PaymentHoldResponse:
        """Place a payment hold on an invoice.

        Requires ``actor_group_verified=True``; callers without verified group
        membership receive 403 Forbidden.  The underlying Functions call uses a
        5-second timeout and is idempotent via ``idempotency_key``.
        """
        if not req.actor_group_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="actor_group_verified must be True to place a payment hold.",
            )
        import os as _os
        import uuid as _uuid
        correlation_id = _os.environ.get(
            "AEGISAP_CORRELATION_ID", str(_uuid.uuid4()))

        functions_url = _os.environ.get("AEGISAP_FUNCTION_APP_URL", "")
        if not functions_url or adapter.use_stubs:
            # Stub path: return a synthetic hold response without calling Functions
            hold_id = f"hold-stub-{req.idempotency_key[:8]}"
            return PaymentHoldResponse(
                idempotency_key=req.idempotency_key,
                hold_id=hold_id,
                invoice_id=req.invoice_id,
                status=HoldStatus.PLACED,
                placed_by_oid=req.actor_oid,
                compensating_action_registered=True,
            )

        from aegisap.integration.azure_functions_boundary import FunctionsBoundaryClient
        client = FunctionsBoundaryClient.from_env()
        result = client.post_payment_hold(req, correlation_id=correlation_id)

        if result.success:
            body = result.body if isinstance(result.body, dict) else {}
            raw_status = body.get("status", "placed")
            try:
                hold_status = HoldStatus(raw_status)
            except ValueError:
                hold_status = HoldStatus.PLACED
            return PaymentHoldResponse(
                idempotency_key=req.idempotency_key,
                hold_id=body.get("hold_id"),
                invoice_id=req.invoice_id,
                status=hold_status,
                placed_by_oid=req.actor_oid,
                compensating_action_registered=body.get(
                    "compensating_action_registered", False),
            )

        # Non-transient errors from the Functions boundary
        if result.status_code in (400, 403, 404):
            raise HTTPException(
                status_code=result.status_code,
                detail=result.error or "Functions boundary returned a non-transient error.",
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=result.error or "Functions boundary unavailable.",
        )

    @fast_app.get("/health")
    async def health() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    # Wrap with auth middleware (bypassed in test/stub mode)
    skip_auth = (
        os.environ.get("AEGISAP_MCP_SKIP_AUTH", "0") == "1"
        or (use_stubs is True)
    )
    if not skip_auth:
        tenant_id = os.environ.get("AZURE_TENANT_ID", "")
        audience = os.environ.get("AEGISAP_MCP_AUDIENCE", "")
        if tenant_id and audience:
            from starlette.middleware import Middleware
            fast_app.add_middleware(
                McpAuthMiddleware,  # type: ignore[arg-type]
                tenant_id=tenant_id,
                audience=audience,
                skip_auth=False,
            )

    return fast_app


# Module-level app instance for uvicorn
app = create_mcp_app()
