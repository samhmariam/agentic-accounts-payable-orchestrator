from __future__ import annotations

from decimal import Decimal
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from aegisap.day_01.models import CanonicalInvoice
from aegisap.common.clocks import utc_now_iso
from aegisap.domain.evidence import ActionRecommendation, EvidenceItem
from aegisap.domain.metrics import NodeMetric

Route = Literal["high_value", "new_vendor", "clean_path"]
Status = Literal["initialized", "routing", "in_review", "completed", "failed"]


class VendorVerification(BaseModel):
    verified: bool = False
    source: str | None = None
    checked_at: str | None = None
    evidence: list[EvidenceItem] = Field(default_factory=list)


class VendorContext(BaseModel):
    vendor_name: str
    is_known_vendor: bool = False
    verification: VendorVerification = Field(default_factory=VendorVerification)


class WorkflowPolicy(BaseModel):
    high_value_threshold: Decimal
    route_precedence: list[Route]


class WorkflowState(BaseModel):
    workflow_id: str
    thread_id: str
    package_id: str
    invoice_id: str
    started_at: str
    last_updated_at: str

    invoice: CanonicalInvoice
    vendor: VendorContext
    policy: WorkflowPolicy

    current_node: str = "init"
    route: Route | None = None
    route_reason: str | None = None
    status: Status = "initialized"

    completed_nodes: list[str] = Field(default_factory=list)
    retry_counts: dict[str, int] = Field(default_factory=dict)

    evidence: list[EvidenceItem] = Field(default_factory=list)
    recommendations: list[ActionRecommendation] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    validation_errors: list[str] = Field(default_factory=list)

    node_metrics: list[NodeMetric] = Field(default_factory=list)
    total_tokens_prompt: int = 0
    total_tokens_completion: int = 0
    total_cost_usd: float = 0.0
    total_latency_ms: int = 0

    idempotency_keys: dict[str, str] = Field(default_factory=dict)
    side_effects: list[str] = Field(default_factory=list)
    run_notes: list[str] = Field(default_factory=list)


def make_initial_state(
    invoice: CanonicalInvoice,
    *,
    package_id: str,
    known_vendor: bool,
    high_value_threshold: Decimal,
    route_precedence: list[Route],
    thread_id: str | None = None,
) -> WorkflowState:
    now = utc_now_iso()
    return WorkflowState(
        workflow_id=f"wf_{uuid4().hex[:12]}",
        thread_id=thread_id or f"thread_{package_id}_{invoice.invoice_number}",
        package_id=package_id,
        invoice_id=invoice.invoice_number,
        started_at=now,
        last_updated_at=now,
        invoice=invoice,
        vendor=VendorContext(
            vendor_name=invoice.supplier_name,
            is_known_vendor=known_vendor,
        ),
        policy=WorkflowPolicy(
            high_value_threshold=high_value_threshold,
            route_precedence=route_precedence,
        ),
    )
