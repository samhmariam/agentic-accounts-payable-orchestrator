"""tests/day12/test_bicep_policy_checker.py — tests for BicepPolicyChecker."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_ROOT = Path(__file__).resolve().parents[2]


def _make_arm_template(resources: list[dict]) -> dict:
    return {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "resources": resources,
    }


class TestBicepPolicyCheckerUnit:
    """Unit tests for BicepPolicyChecker — mock the subprocess call."""

    def _make_checker(self, tmp_path: Path):
        from aegisap.network.bicep_policy_checker import BicepPolicyChecker
        return BicepPolicyChecker(infra_root=tmp_path)

    def _write_bicep(self, tmp_path: Path, name: str = "main.bicep") -> Path:
        """Write a dummy bicep file so rglob finds it."""
        bf = tmp_path / name
        bf.write_text("// dummy bicep\n")
        return bf

    def test_passes_when_all_resources_disabled(self, tmp_path):
        self._write_bicep(tmp_path)
        arm = _make_arm_template([
            {"type": "Microsoft.CognitiveServices/accounts", "name": "my-openai",
             "properties": {"publicNetworkAccess": "Disabled"}},
        ])
        checker = self._make_checker(tmp_path)
        with patch.object(checker, "_compile_bicep", return_value=arm):
            result = checker.run()
        assert result.all_passed is True
        assert len(result.violations) == 0
        assert result.resources_checked == 1

    def test_fails_when_public_network_access_enabled(self, tmp_path):
        self._write_bicep(tmp_path)
        arm = _make_arm_template([
            {"type": "Microsoft.CognitiveServices/accounts", "name": "my-openai",
             "properties": {"publicNetworkAccess": "Enabled"}},
        ])
        checker = self._make_checker(tmp_path)
        with patch.object(checker, "_compile_bicep", return_value=arm):
            result = checker.run()
        assert result.all_passed is False
        assert len(result.violations) == 1
        assert "my-openai" in result.violations[0].resource

    def test_ignores_non_ai_resources(self, tmp_path):
        self._write_bicep(tmp_path)
        arm = _make_arm_template([
            {"type": "Microsoft.Web/sites", "name": "my-app",
             "properties": {"publicNetworkAccess": "Enabled"}},
        ])
        checker = self._make_checker(tmp_path)
        with patch.object(checker, "_compile_bicep", return_value=arm):
            result = checker.run()
        assert result.all_passed is True
        assert result.resources_checked == 0

    def test_no_bicep_files_returns_error(self, tmp_path):
        checker = self._make_checker(tmp_path)
        result = checker.run()
        assert result.all_passed is False
        assert result.error is not None
        assert "No *.bicep" in result.error

    def test_no_az_bicep_returns_failed_not_crash(self, tmp_path):
        """If az CLI is not installed, the checker should return a failed result gracefully."""
        self._write_bicep(tmp_path)
        checker = self._make_checker(tmp_path)
        # Simulate FileNotFoundError when calling subprocess
        with patch.object(checker, "_compile_bicep", side_effect=FileNotFoundError("az not found")):
            result = checker.run()
        assert result.all_passed is False
        assert result.error is not None

    def test_artifact_written_by_field(self, tmp_path):
        self._write_bicep(tmp_path)
        arm = _make_arm_template([])
        checker = self._make_checker(tmp_path)
        with patch.object(checker, "_compile_bicep", return_value=arm):
            result = checker.run()
        d = result.to_dict()
        assert d["written_by"] == "check_private_network_static"


class TestBicepPolicyCheckerIntegration:
    """Integration test — only runs if az CLI is available."""

    def test_gate_passes_with_valid_artifact(self, tmp_path):
        """gate_private_network_static should pass when artifact is correct."""
        artifact_path = _ROOT / "build" / "day12" / "static_bicep_analysis.json"
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(json.dumps({
            "written_by": "check_private_network_static",
            "all_passed": True,
            "resources_checked": 2,
            "violations": [],
        }))
        from aegisap.deploy.gates_v2 import gate_private_network_static
        result = gate_private_network_static()
        assert result.passed is True
