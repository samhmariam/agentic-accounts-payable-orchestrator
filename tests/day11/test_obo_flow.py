"""tests/day11/test_obo_flow.py — unit tests for OboTokenProvider"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers / stubs
# ---------------------------------------------------------------------------

@dataclass
class _FakeOboResult:
    access_token: str = "fake-access-token"
    oid: str = "user-oid-123"
    token_type: str = "Bearer"
    expires_in: int = 3600


class TestOboTokenProvider:
    def test_from_env_requires_tenant(self, monkeypatch):
        monkeypatch.delenv("AZURE_TENANT_ID", raising=False)
        monkeypatch.delenv("AZURE_CLIENT_ID", raising=False)
        monkeypatch.delenv("AZURE_CLIENT_SECRET", raising=False)
        from aegisap.identity.obo import OboTokenProvider
        with pytest.raises((ValueError, KeyError)):
            OboTokenProvider.from_env()

    def test_from_env_succeeds_with_vars(self, monkeypatch):
        monkeypatch.setenv("AZURE_TENANT_ID", "tenant-id")
        monkeypatch.setenv("AZURE_CLIENT_ID", "client-id")
        monkeypatch.setenv("AZURE_CLIENT_SECRET", "secret")
        from aegisap.identity.obo import OboTokenProvider
        provider = OboTokenProvider.from_env()
        assert provider is not None

    def test_exchange_returns_obo_result(self, monkeypatch):
        monkeypatch.setenv("AZURE_TENANT_ID", "tenant-id")
        monkeypatch.setenv("AZURE_CLIENT_ID", "client-id")
        monkeypatch.setenv("AZURE_CLIENT_SECRET", "secret")

        mock_token = {
            "access_token": "obo-token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "id_token_claims": {"oid": "user-oid-123"},
        }

        with patch("aegisap.identity.obo.ConfidentialClientApplication") as mock_app_cls:
            mock_app = MagicMock()
            mock_app.acquire_token_on_behalf_of.return_value = mock_token
            mock_app_cls.return_value = mock_app

            from aegisap.identity.obo import OboTokenProvider
            provider = OboTokenProvider.from_env()
            result = provider.exchange(
                "user-assertion-token", ["https://graph.microsoft.com/.default"])

        assert result.access_token == "obo-token"
        assert result.oid == "user-oid-123"

    def test_exchange_raises_on_error_response(self, monkeypatch):
        monkeypatch.setenv("AZURE_TENANT_ID", "tenant-id")
        monkeypatch.setenv("AZURE_CLIENT_ID", "client-id")
        monkeypatch.setenv("AZURE_CLIENT_SECRET", "secret")

        mock_error_response = {"error": "invalid_grant",
                               "error_description": "Bad request"}

        with patch("aegisap.identity.obo.ConfidentialClientApplication") as mock_app_cls:
            mock_app = MagicMock()
            mock_app.acquire_token_on_behalf_of.return_value = mock_error_response
            mock_app_cls.return_value = mock_app

            from aegisap.identity.obo import OboTokenProvider
            provider = OboTokenProvider.from_env()
            with pytest.raises(Exception, match="invalid_grant|OBO exchange failed"):
                provider.exchange(
                    "bad-token", ["https://graph.microsoft.com/.default"])
