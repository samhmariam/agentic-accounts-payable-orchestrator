"""tests/day13/test_mcp_server.py — unit tests for MCP server endpoints"""
from __future__ import annotations
from fastapi.testclient import TestClient

import pytest

pytest.importorskip("fastapi", reason="fastapi not installed")
pytest.importorskip("httpx", reason="httpx not installed")


class TestMcpServer:
    @pytest.fixture(autouse=True)
    def _skip_auth(self, monkeypatch):
        monkeypatch.setenv("AEGISAP_MCP_SKIP_AUTH", "1")

    @pytest.fixture()
    def client(self):
        from aegisap.mcp.server import create_mcp_app
        return TestClient(create_mcp_app())

    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_capabilities_lists_required_tools(self, client):
        resp = client.get("/capabilities")
        assert resp.status_code == 200
        data = resp.json()
        tool_names = {t["name"] for t in data["tools"]}
        assert "query_invoice_status" in tool_names
        assert "list_pending_approvals" in tool_names
        assert "get_vendor_policy" in tool_names

    def test_query_invoice_status_known(self, client):
        resp = client.post(
            "/tools/query_invoice_status",
            json={"invoice_id": "INV-001"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["invoice_id"] == "INV-001"
        assert "status" in data

    def test_query_invoice_status_unknown(self, client):
        resp = client.post(
            "/tools/query_invoice_status",
            json={"invoice_id": "INV-UNKNOWN"},
        )
        assert resp.status_code == 404

    def test_list_pending_approvals(self, client):
        resp = client.post(
            "/tools/list_pending_approvals",
            json={"limit": 10},
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_vendor_policy_known(self, client):
        resp = client.post(
            "/tools/get_vendor_policy",
            json={"vendor_id": "ACME-001"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["vendor_id"] == "ACME-001"

    def test_get_vendor_policy_unknown(self, client):
        resp = client.post(
            "/tools/get_vendor_policy",
            json={"vendor_id": "NONEXISTENT"},
        )
        assert resp.status_code == 404
