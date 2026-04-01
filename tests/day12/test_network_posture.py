"""tests/day12/test_network_posture.py — unit tests for NetworkPostureProbe"""
from __future__ import annotations

import json
import socket
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestNetworkPostureProbe:
    def test_from_env_uses_hostnames_var(self, monkeypatch, tmp_path):
        monkeypatch.setenv("AEGISAP_AI_HOSTNAMES", "openai.local,search.local")
        from aegisap.network.private_endpoint_probe import NetworkPostureProbe
        probe = NetworkPostureProbe.from_env()
        assert "openai.local" in probe.hostnames
        assert "search.local" in probe.hostnames

    def test_private_ip_detection(self):
        from aegisap.network.private_endpoint_probe import NetworkPostureProbe
        probe = NetworkPostureProbe(hostnames=["dummy.local"])
        assert probe._is_private("10.0.1.4") is True
        assert probe._is_private("172.16.0.1") is True
        assert probe._is_private("192.168.1.1") is True
        assert probe._is_private("20.55.0.1") is False
        assert probe._is_private("13.107.4.50") is False

    def test_run_marks_passed_when_dns_private_and_not_reachable(self, monkeypatch):
        monkeypatch.setenv("AEGISAP_AI_HOSTNAMES", "myopenai.openai.azure.com")

        from aegisap.network.private_endpoint_probe import NetworkPostureProbe

        with patch.object(NetworkPostureProbe, "_resolve_ip", return_value="10.0.1.4"):
            with patch.object(NetworkPostureProbe, "_is_public_reachable", return_value=False):
                probe = NetworkPostureProbe.from_env()
                result = probe.run()

        assert result.all_passed is True
        assert result.services[0].dns_private is True
        assert result.services[0].public_reachable is False
        assert result.services[0].passed is True

    def test_run_marks_failed_when_dns_public(self, monkeypatch):
        monkeypatch.setenv("AEGISAP_AI_HOSTNAMES", "myopenai.openai.azure.com")

        from aegisap.network.private_endpoint_probe import NetworkPostureProbe

        with patch.object(NetworkPostureProbe, "_resolve_ip", return_value="20.55.0.1"):
            with patch.object(NetworkPostureProbe, "_is_public_reachable", return_value=True):
                probe = NetworkPostureProbe.from_env()
                result = probe.run()

        assert result.all_passed is False
        assert result.services[0].passed is False

    def test_write_artifacts_creates_both_files_when_passed(self, monkeypatch, tmp_path):
        monkeypatch.setenv("AEGISAP_AI_HOSTNAMES", "myopenai.openai.azure.com")

        from aegisap.network.private_endpoint_probe import NetworkPostureProbe, PostureResult, ServicePosture

        probe = NetworkPostureProbe(hostnames=["myopenai.openai.azure.com"])
        svc = ServicePosture(
            hostname="myopenai.openai.azure.com",
            dns_private=True,
            dns_ip="10.0.1.4",
            public_reachable=False,
            passed=True,
            detail="DNS → 10.0.1.4 (private); public not reachable.",
        )
        result = PostureResult(all_passed=True, services=[svc])

        with patch("aegisap.network.private_endpoint_probe._BUILD_DIR", tmp_path):
            probe.write_artifacts(result)

        assert (tmp_path / "private_network_posture.json").exists()
        assert (tmp_path / "external_sink_disabled.json").exists()
        sink = json.loads(
            (tmp_path / "external_sink_disabled.json").read_text())
        assert sink["written_by"] == "verify_private_network_posture"

    def test_write_artifacts_no_sink_file_when_failed(self, monkeypatch, tmp_path):
        monkeypatch.setenv("AEGISAP_AI_HOSTNAMES", "myopenai.openai.azure.com")

        from aegisap.network.private_endpoint_probe import NetworkPostureProbe, PostureResult, ServicePosture

        probe = NetworkPostureProbe(hostnames=["myopenai.openai.azure.com"])
        svc = ServicePosture(
            hostname="myopenai.openai.azure.com",
            dns_private=False,
            dns_ip="20.55.0.1",
            public_reachable=True,
            passed=False,
            detail="DNS → 20.55.0.1 (public); public reachable.",
        )
        result = PostureResult(all_passed=False, services=[svc])

        with patch("aegisap.network.private_endpoint_probe._BUILD_DIR", tmp_path):
            probe.write_artifacts(result)

        assert (tmp_path / "private_network_posture.json").exists()
        assert not (tmp_path / "external_sink_disabled.json").exists()
