"""tests/day11/test_actor_verification.py — unit tests for ActorVerifier"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestActorVerifier:
    def test_verify_returns_member_true_when_in_group(self, monkeypatch):
        monkeypatch.setenv("AEGISAP_APPROVER_GROUP_ID", "group-id-001")

        group_id = "group-id-001"
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "value": [{"id": group_id}]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("aegisap.identity.actor_verifier.requests.get", return_value=mock_response):
            with patch("aegisap.identity.actor_verifier.DefaultAzureCredential") as mock_cred_cls:
                mock_cred = MagicMock()
                mock_token = MagicMock()
                mock_token.token = "graph-access-token"
                mock_cred.get_token.return_value = mock_token
                mock_cred_cls.return_value = mock_cred

                from aegisap.identity.actor_verifier import ActorVerifier
                verifier = ActorVerifier.from_env()
                result = verifier.verify("user-oid-123")

        assert result.is_member is True
        assert result.group_id == group_id

    def test_verify_returns_member_false_when_not_in_group(self, monkeypatch):
        monkeypatch.setenv("AEGISAP_APPROVER_GROUP_ID", "group-id-001")

        mock_response = MagicMock()
        mock_response.json.return_value = {"value": []}
        mock_response.raise_for_status = MagicMock()

        with patch("aegisap.identity.actor_verifier.requests.get", return_value=mock_response):
            with patch("aegisap.identity.actor_verifier.DefaultAzureCredential") as mock_cred_cls:
                mock_cred = MagicMock()
                mock_token = MagicMock()
                mock_token.token = "graph-access-token"
                mock_cred.get_token.return_value = mock_token
                mock_cred_cls.return_value = mock_cred

                from aegisap.identity.actor_verifier import ActorVerifier
                verifier = ActorVerifier.from_env()
                result = verifier.verify("outsider-oid")

        assert result.is_member is False

    def test_from_env_requires_group_id(self, monkeypatch):
        monkeypatch.delenv("AEGISAP_APPROVER_GROUP_ID", raising=False)
        from aegisap.identity.actor_verifier import ActorVerifier
        with pytest.raises((ValueError, KeyError)):
            ActorVerifier.from_env()
