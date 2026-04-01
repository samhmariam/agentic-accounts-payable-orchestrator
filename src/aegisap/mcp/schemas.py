"""Pydantic schemas for the AegisAP MCP server (Day 13).

These schemas define the contract that external MCP clients (e.g., Claude
Desktop, Copilot Studio, or custom agents) must conform to when calling
AegisAP MCP tools.

All schema changes must be versioned.  The current version is v1.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class McpCapabilities(BaseModel):
    """Advertised capabilities returned by the /capabilities endpoint."""

    protocol_version: str = "2024-11-05"
    server_name: str = "aegisap-mcp"
    server_version: str = "1.0.0"
    tools: list[str] = Field(
        default_factory=lambda: [
            "query_invoice_status",
            "list_pending_approvals",
            "get_vendor_policy",
            "submit_payment_hold",
        ]
    )


class InvoiceStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    ERROR = "error"


class InvoiceQueryRequest(BaseModel):
    """Request body for the ``query_invoice_status`` MCP tool."""

    invoice_id: str = Field(..., min_length=1,
                            description="Canonical invoice identifier")
    requester_oid: str | None = Field(
        None,
        description="Entra OID of the requesting user (from OBO token claims).",
    )


class InvoiceQueryResponse(BaseModel):
    """Response schema for ``query_invoice_status``."""

    invoice_id: str
    status: InvoiceStatus
    amount: float | None = None
    currency: str | None = None
    vendor_name: str | None = None
    approved_by_oid: str | None = None
    citation_ids: list[str] = Field(default_factory=list)
    error: str | None = None


class ListPendingApprovalsRequest(BaseModel):
    """Request body for ``list_pending_approvals``."""

    approver_oid: str = Field(..., description="Entra OID of the approver.")
    limit: int = Field(default=20, ge=1, le=100)


class VendorPolicyRequest(BaseModel):
    """Request body for ``get_vendor_policy``."""

    vendor_id: str = Field(..., min_length=1)
    policy_version: str | None = None


class VendorPolicyResponse(BaseModel):
    """Response schema for ``get_vendor_policy``."""

    vendor_id: str
    policy_version: str
    auto_approve_threshold: float
    requires_dual_approval_above: float
    currency: str
    citation_ids: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase B — Payment Hold write-path (Day 13+)
# ---------------------------------------------------------------------------

class HoldReason(str, Enum):
    VENDOR_COMPLIANCE = "vendor_compliance"
    AMOUNT_OVER_THRESHOLD = "amount_over_threshold"
    MISSING_PO = "missing_po"
    FRAUD_SIGNAL = "fraud_signal"
    MANUAL_REVIEW = "manual_review"


class HoldStatus(str, Enum):
    PLACED = "placed"
    ALREADY_HELD = "already_held"
    REJECTED = "rejected"


class PaymentHoldRequest(BaseModel):
    """Request body for the ``submit_payment_hold`` MCP tool."""

    idempotency_key: str = Field(
        ..., min_length=1, description="Client-generated idempotency key (UUID recommended)."
    )
    invoice_id: str = Field(..., min_length=1)
    vendor_id: str = Field(..., min_length=1)
    hold_reason: HoldReason
    actor_oid: str = Field(...,
                           description="Entra OID of the actor placing the hold.")
    actor_group_verified: bool = Field(
        ...,
        description="True only if the caller's group membership was verified via OBO+Graph.",
    )
    timeout_budget_ms: int = Field(
        default=5000, ge=100, le=30_000,
        description="Maximum ms the server may spend on downstream calls.",
    )


class PaymentHoldResponse(BaseModel):
    """Response schema for ``submit_payment_hold``."""

    idempotency_key: str
    hold_id: str | None = None
    invoice_id: str
    status: HoldStatus
    placed_by_oid: str
    compensating_action_registered: bool = False
    error: str | None = None
