"""tests/day13/test_payment_hold.py — tests for the MCP submit_payment_hold route."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from aegisap.mcp.server import create_mcp_app
    app = create_mcp_app(use_stubs=True)
    return TestClient(app)


class TestSubmitPaymentHoldRoute:
    """Tests for POST /tools/submit_payment_hold."""

    def _valid_payload(self, **overrides) -> dict:
        base = {
            "idempotency_key": "test-idem-key-001",
            "invoice_id": "INV-TEST-001",
            "vendor_id": "VDR-42",
            "hold_reason": "missing_po",
            "actor_oid": "actor-oid-123",
            "actor_group_verified": True,
            "timeout_budget_ms": 5000,
        }
        base.update(overrides)
        return base

    def test_returns_placed_status_stub_mode(self, client):
        resp = client.post("/tools/submit_payment_hold",
                           json=self._valid_payload())
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "placed"
        assert body["invoice_id"] == "INV-TEST-001"
        assert body["placed_by_oid"] == "actor-oid-123"

    def test_idempotency_key_echoed(self, client):
        resp = client.post("/tools/submit_payment_hold", json=self._valid_payload(
            idempotency_key="my-unique-key-xyz"
        ))
        assert resp.status_code == 200
        assert resp.json()["idempotency_key"] == "my-unique-key-xyz"

    def test_rejects_unverified_actor(self, client):
        resp = client.post("/tools/submit_payment_hold", json=self._valid_payload(
            actor_group_verified=False
        ))
        assert resp.status_code == 403
        assert "actor_group_verified" in resp.json()["detail"]

    def test_all_hold_reasons_accepted(self, client):
        for reason in ("vendor_compliance", "amount_over_threshold", "missing_po",
                       "fraud_signal", "manual_review"):
            resp = client.post("/tools/submit_payment_hold", json=self._valid_payload(
                hold_reason=reason
            ))
            assert resp.status_code == 200, f"Failed for hold_reason={reason}"

    def test_capabilities_includes_submit_payment_hold(self, client):
        resp = client.get("/capabilities")
        assert resp.status_code == 200
        tools = resp.json()["tools"]
        tool_names = {tool["name"] for tool in tools}
        assert "submit_payment_hold" in tool_names

    def test_compensating_action_registered_in_stub(self, client):
        resp = client.post("/tools/submit_payment_hold",
                           json=self._valid_payload())
        assert resp.status_code == 200
        assert resp.json()["compensating_action_registered"] is True


class TestPaymentHoldSchemas:
    """Validate Pydantic schema behaviour for PaymentHoldRequest / PaymentHoldResponse."""

    def test_hold_reason_enum_values(self):
        from aegisap.mcp.schemas import HoldReason
        values = {e.value for e in HoldReason}
        expected = {
            "vendor_compliance", "amount_over_threshold",
            "missing_po", "fraud_signal", "manual_review",
        }
        assert values == expected

    def test_hold_status_enum_values(self):
        from aegisap.mcp.schemas import HoldStatus
        values = {e.value for e in HoldStatus}
        assert values == {"placed", "already_held", "rejected"}

    def test_request_validation_requires_actor_group_verified(self):
        from aegisap.mcp.schemas import PaymentHoldRequest, HoldReason
        import pydantic
        with pytest.raises(pydantic.ValidationError):
            PaymentHoldRequest(
                idempotency_key="k",
                invoice_id="INV-001",
                vendor_id="VDR-1",
                hold_reason=HoldReason.MISSING_PO,
                actor_oid="oid",
                # Missing actor_group_verified
            )
