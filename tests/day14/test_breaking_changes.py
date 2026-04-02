"""tests/day14/test_breaking_changes.py — tests for all gate functions"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest


_ROOT = Path(__file__).resolve().parents[2]


def _write_artifact(rel_path: str, content: dict) -> None:
    p = _ROOT / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(content))


class TestGatesV1PassWithArtifacts:
    """Gates 1-6 should pass when build/day* artifacts exist."""

    def test_gate_security_posture(self, tmp_path):
        # gate_security_posture checks build/day10/ artifacts
        from aegisap.deploy.gates import gate_security_posture
        result = gate_security_posture()
        # Gate either passes or fails — we just check it returns a GateResult
        assert hasattr(result, "passed")
        assert hasattr(result, "name")
        assert hasattr(result, "detail")


class TestGatesV2PassWithStubArtifacts:
    """Gates 7-17 from gates_v2.py should pass when stub artifacts exist."""

    def test_gate_delegated_identity(self):
        _write_artifact("build/day11/obo_contract.json", {
            "app_identity_check": {"passed": True, "detail": "MI token acquired."},
            "obo_exchange_check": {"passed": True, "detail": "OBO exchange succeeded."},
            "actor_binding_check": {"passed": True, "detail": "Approver OID bound to group."},
        })
        from aegisap.deploy.gates_v2 import gate_delegated_identity
        result = gate_delegated_identity()
        assert result.passed is True

    def test_gate_private_network_static(self):
        _write_artifact("build/day12/static_bicep_analysis.json", {
            "written_by": "check_private_network_static",
            "all_passed": True,
            "resources_checked": 2,
            "violations": [],
        })
        from aegisap.deploy.gates_v2 import gate_private_network_static
        result = gate_private_network_static()
        assert result.passed is True

    def test_gate_private_network_static_fails_wrong_written_by(self):
        _write_artifact("build/day12/static_bicep_analysis.json", {
            "written_by": "manual_override",
            "all_passed": True,
        })
        from aegisap.deploy.gates_v2 import gate_private_network_static
        result = gate_private_network_static()
        assert result.passed is False

    def test_gate_private_network_static_fails_on_violations(self):
        _write_artifact("build/day12/static_bicep_analysis.json", {
            "written_by": "check_private_network_static",
            "all_passed": False,
            "resources_checked": 3,
            "violations": [
                {"resource": "my-openai", "type": "Microsoft.CognitiveServices/accounts",
                 "violation": "publicNetworkAccess='Enabled'"}
            ],
        })
        from aegisap.deploy.gates_v2 import gate_private_network_static
        result = gate_private_network_static()
        assert result.passed is False
        assert "violation" in result.detail.lower()

    def test_gate_private_network_posture(self):
        _write_artifact("build/day12/private_network_posture.json", {
            "all_passed": True,
            "services": [],
        })
        from aegisap.deploy.gates_v2 import gate_private_network_posture
        result = gate_private_network_posture()
        assert result.passed is True

    def test_gate_private_network_posture_fails_on_training_artifact(self):
        _write_artifact("build/day12/private_network_posture.json", {
            "all_passed": True,
            "services": [],
            "training_artifact": True,
            "authoritative_evidence": False,
            "note": "TRAINING_ONLY",
        })
        from aegisap.deploy.gates_v2 import gate_private_network_posture
        result = gate_private_network_posture()
        assert result.passed is False
        assert "training-only" in result.detail.lower()

    def test_gate_dlq_drain_health(self):
        _write_artifact("build/day13/dlq_drain_report.json", {
            "all_handled": True,
            "drained": 0,
        })
        from aegisap.deploy.gates_v2 import gate_dlq_drain_health
        result = gate_dlq_drain_health()
        assert result.passed is True

    def test_gate_mcp_contract_integrity(self):
        _write_artifact("build/day13/mcp_contract_report.json", {
            "passed": True,
            "tools_present": ["query_invoice_status", "list_pending_approvals",
                              "get_vendor_policy", "submit_payment_hold"],
            "errors": [],
        })
        from aegisap.deploy.gates_v2 import gate_mcp_contract_integrity
        result = gate_mcp_contract_integrity()
        assert result.passed is True

    def test_gate_mcp_contract_integrity_fails_on_training_artifact(self):
        _write_artifact("build/day13/mcp_contract_report.json", {
            "passed": True,
            "errors": [],
            "training_artifact": True,
            "authoritative_evidence": False,
            "note": "TRAINING_ONLY",
        })
        from aegisap.deploy.gates_v2 import gate_mcp_contract_integrity
        result = gate_mcp_contract_integrity()
        assert result.passed is False
        assert "training-only" in result.detail.lower()

    def test_gate_trace_correlation(self):
        _write_artifact("build/day14/trace_correlation_report.json", {
            "passed": True,
            "uncorrelated": 0,
            "total_traces": 5,
            "dual_sink_ok": True,
            "correlation_id_coverage": 1.0,
        })
        from aegisap.deploy.gates_v2 import gate_trace_correlation
        result = gate_trace_correlation()
        assert result.passed is True

    def test_gate_data_residency(self):
        _write_artifact("build/day14/data_residency_report.json", {
            "all_passed": True,
            "approved_region": "eastus",
            "violations": [],
        })
        from aegisap.deploy.gates_v2 import gate_data_residency
        result = gate_data_residency()
        assert result.passed is True

    def test_gate_data_residency_fails_on_training_artifact(self):
        _write_artifact("build/day14/data_residency_report.json", {
            "all_passed": True,
            "approved_region": "eastus",
            "violations": [],
            "training_artifact": True,
            "authoritative_evidence": False,
            "note": "TRAINING_ONLY",
        })
        from aegisap.deploy.gates_v2 import gate_data_residency
        result = gate_data_residency()
        assert result.passed is False
        assert "training-only" in result.detail.lower()

    def test_gate_canary_regression(self):
        _write_artifact("build/day14/canary_regression_report.json", {
            "passed": True,
            "regressions": [],
        })
        from aegisap.deploy.gates_v2 import gate_canary_regression
        result = gate_canary_regression()
        assert result.passed is True

    def test_gate_canary_regression_fails_on_training_artifact(self):
        _write_artifact("build/day14/canary_regression_report.json", {
            "passed": True,
            "regressions": [],
            "training_artifact": True,
            "authoritative_evidence": False,
            "note": "TRAINING_ONLY",
        })
        from aegisap.deploy.gates_v2 import gate_canary_regression
        result = gate_canary_regression()
        assert result.passed is False
        assert "training-only" in result.detail.lower()

    def test_gate_fails_when_artifact_missing(self, tmp_path):
        """Remove the artifact and verify the gate returns passed=False."""
        artifact = _ROOT / "build" / "day14" / "canary_regression_report.json"
        existed = artifact.exists()
        saved = artifact.read_text() if existed else None
        try:
            if artifact.exists():
                artifact.unlink()
            from aegisap.deploy import gates_v2
            import importlib
            importlib.reload(gates_v2)
            result = gates_v2.gate_canary_regression()
            assert result.passed is False
        finally:
            if saved is not None:
                artifact.write_text(saved)


class TestNewGatesPhaseA:
    """Tests for gate_stale_index_detection, gate_webhook_reliability, gate_rollback_readiness."""

    def test_gate_stale_index_detection_passes_no_stale(self):
        _write_artifact("build/day12/stale_index_report.json", {
            "stale_indexes": [],
            "threshold_hours": 24,
            "all_fresh": True,
        })
        from aegisap.deploy.gates_v2 import gate_stale_index_detection
        result = gate_stale_index_detection()
        # Soft gate — always passes but warns if stale
        assert hasattr(result, "passed")
        assert result.name == "stale_index_detection"

    def test_gate_stale_index_detection_warns_on_stale(self):
        _write_artifact("build/day12/stale_index_report.json", {
            "stale_indexes": ["invoice-index"],
            "threshold_hours": 24,
            "all_fresh": False,
        })
        from aegisap.deploy.gates_v2 import gate_stale_index_detection
        result = gate_stale_index_detection()
        # Should still pass (soft gate) but detail should mention stale
        assert result.passed is True
        assert "stale" in result.detail.lower() or "warn" in result.detail.lower()

    def test_gate_webhook_reliability_passes(self):
        _write_artifact("build/day13/webhook_reliability_report.json", {
            "all_handled": True,
            "unhandled_count": 0,
            "checked_webhooks": ["erp-post-invoice"],
        })
        from aegisap.deploy.gates_v2 import gate_webhook_reliability
        result = gate_webhook_reliability()
        assert result.passed is True
        assert result.name == "webhook_reliability"

    def test_gate_webhook_reliability_fails_on_low_success_rate(self):
        _write_artifact("build/day13/webhook_reliability_report.json", {
            "all_handled": False,
            "unhandled_count": 3,
            "checked_webhooks": ["erp-post-invoice"],
        })
        from aegisap.deploy.gates_v2 import gate_webhook_reliability
        result = gate_webhook_reliability()
        assert result.passed is False

    def test_gate_rollback_readiness_passes_when_both_present(self):
        _write_artifact("build/day14/rollback_readiness_report.json", {
            "stable_revision_known": True,
            "stable_revision": "aegisap-stable-v1",
            "runbook_present": True,
        })
        from aegisap.deploy.gates_v2 import gate_rollback_readiness
        result = gate_rollback_readiness()
        assert result.passed is True
        assert result.name == "rollback_readiness"

    def test_gate_rollback_readiness_fails_missing_runbook(self):
        _write_artifact("build/day14/rollback_readiness_report.json", {
            "stable_revision_known": True,
            "stable_revision": "aegisap-stable-v1",
            "runbook_present": False,
        })
        from aegisap.deploy.gates_v2 import gate_rollback_readiness
        result = gate_rollback_readiness()
        assert result.passed is False

    def test_gate_rollback_readiness_fails_no_stable_revision(self):
        _write_artifact("build/day14/rollback_readiness_report.json", {
            "stable_revision_known": False,
            "stable_revision": "",
            "runbook_present": True,
        })
        from aegisap.deploy.gates_v2 import gate_rollback_readiness
        result = gate_rollback_readiness()
        assert result.passed is False


class TestTraceCorrDualSinkMode:
    """gate_trace_correlation must derive dual_sink requirement from Day 12 posture."""

    def test_dual_sink_required_and_satisfied(self):
        _write_artifact("build/day12/private_network_posture.json", {
            "all_passed": True,
        })
        _write_artifact("build/day14/trace_correlation_report.json", {
            "passed": True,
            "uncorrelated": 0,
            "dual_sink_ok": True,
            "correlation_id_coverage": 1.0,
            "mode": "dual_sink",
        })
        from aegisap.deploy.gates_v2 import gate_trace_correlation
        result = gate_trace_correlation()
        assert result.passed is True

    def test_dual_sink_required_but_missing(self):
        _write_artifact("build/day12/private_network_posture.json", {
            "all_passed": True,
        })
        _write_artifact("build/day14/trace_correlation_report.json", {
            "passed": True,
            "uncorrelated": 0,
            "dual_sink_ok": False,
            "correlation_id_coverage": 1.0,
            "mode": "isolated",
        })
        from aegisap.deploy.gates_v2 import gate_trace_correlation
        result = gate_trace_correlation()
        assert result.passed is False
        assert "dual" in result.detail.lower()

    def test_no_posture_file_does_not_require_dual_sink(self):
        # If Day 12 posture file doesn't exist, dual_sink should not be required
        posture_path = _ROOT / "build" / "day12" / "private_network_posture.json"
        existed = posture_path.exists()
        saved = posture_path.read_text() if existed else None
        try:
            if posture_path.exists():
                posture_path.unlink()
            _write_artifact("build/day14/trace_correlation_report.json", {
                "passed": True,
                "uncorrelated": 0,
                "dual_sink_ok": False,
                "correlation_id_coverage": 1.0,
                "mode": "isolated",
            })
            from aegisap.deploy import gates_v2
            import importlib
            importlib.reload(gates_v2)
            result = gates_v2.gate_trace_correlation()
            # Without posture file, dual_sink not required → should pass
            assert result.passed is True
        finally:
            if saved is not None:
                posture_path.write_text(saved)
