"""Line-of-business system adapter for the AegisAP MCP server (Day 13).

The LobAdapter translates MCP tool calls into calls to the actual
AegisAP domain services (or Azure Functions at LOB boundaries).

In production this adapter would call real ERP and document-store APIs.
In the training environment it returns deterministic stubs so notebooks
run without live Azure dependencies.
"""

from __future__ import annotations

import os
from typing import Any

from .schemas import (
    InvoiceQueryRequest,
    InvoiceQueryResponse,
    InvoiceStatus,
    ListPendingApprovalsRequest,
    VendorPolicyRequest,
    VendorPolicyResponse,
)

# ---------------------------------------------------------------------------
# Stub data for training environment
# ---------------------------------------------------------------------------
_STUB_INVOICES: dict[str, dict[str, Any]] = {
    "INV-001": {
        "status": InvoiceStatus.APPROVED,
        "amount": 450.0,
        "currency": "GBP",
        "vendor_name": "ACME Supplies Ltd",
        "approved_by_oid": "oid-finance-director-stub",
        "citation_ids": ["policy-doc-001#clause-3"],
    },
    "INV-002": {
        "status": InvoiceStatus.ESCALATED,
        "amount": 15000.0,
        "currency": "GBP",
        "vendor_name": "BigCo Corp",
        "approved_by_oid": None,
        "citation_ids": [],
    },
    "INV-003": {
        "status": InvoiceStatus.PENDING,
        "amount": 99.0,
        "currency": "GBP",
        "vendor_name": "Stationery Direct",
        "approved_by_oid": None,
        "citation_ids": [],
    },
}

_STUB_VENDOR_POLICIES: dict[str, dict[str, Any]] = {
    "ACME": {
        "policy_version": "2024-v1",
        "auto_approve_threshold": 500.0,
        "requires_dual_approval_above": 10000.0,
        "currency": "GBP",
        "citation_ids": ["vendor-policy-ACME-2024"],
    }
}


class LobAdapter:
    """Adapter between MCP tool calls and AegisAP domain services."""

    def __init__(self, use_stubs: bool | None = None) -> None:
        if use_stubs is None:
            use_stubs = os.environ.get("AEGISAP_MCP_USE_STUBS", "1") == "1"
        self._use_stubs = use_stubs

    def query_invoice_status(self, req: InvoiceQueryRequest) -> InvoiceQueryResponse:
        if self._use_stubs:
            inv = _STUB_INVOICES.get(req.invoice_id)
            if inv is None:
                return InvoiceQueryResponse(
                    invoice_id=req.invoice_id,
                    status=InvoiceStatus.ERROR,
                    error=f"Invoice {req.invoice_id!r} not found in stub data.",
                )
            return InvoiceQueryResponse(invoice_id=req.invoice_id, **inv)
        raise NotImplementedError("Live LOB adapter not yet implemented.")

    def list_pending_approvals(
        self, req: ListPendingApprovalsRequest
    ) -> list[InvoiceQueryResponse]:
        if self._use_stubs:
            pending = [
                InvoiceQueryResponse(invoice_id=iid, **data)
                for iid, data in _STUB_INVOICES.items()
                if data["status"] == InvoiceStatus.PENDING
            ]
            return pending[: req.limit]
        raise NotImplementedError("Live LOB adapter not yet implemented.")

    def get_vendor_policy(self, req: VendorPolicyRequest) -> VendorPolicyResponse:
        if self._use_stubs:
            policy = _STUB_VENDOR_POLICIES.get(req.vendor_id)
            if policy is None:
                return VendorPolicyResponse(
                    vendor_id=req.vendor_id,
                    policy_version="unknown",
                    auto_approve_threshold=0.0,
                    requires_dual_approval_above=0.0,
                    currency="GBP",
                )
            return VendorPolicyResponse(vendor_id=req.vendor_id, **policy)
        raise NotImplementedError("Live LOB adapter not yet implemented.")
