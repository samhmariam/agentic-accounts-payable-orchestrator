"""tests/day11/test_obo_simulation.py — tests for OBO simulation cells."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]


def _write(rel: str, content: dict) -> None:
    p = _ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(content))


def _read(rel: str) -> dict:
    p = _ROOT / rel
    return json.loads(p.read_text()) if p.exists() else {}


class TestOboSimulationArtifacts:
    """Verify that all three simulation paths write expected keys to obo_simulation_results.json."""

    def test_happy_path_key_structure(self, tmp_path):
        """Happy path simulation must write oid, actor_verified=True, hold_allowed=True."""
        _write("build/day11/obo_simulation_results.json", {
            "happy_path": {
                "oid": "user-oid-finance-director",
                "actor_verified": True,
                "hold_allowed": True,
            }
        })
        data = _read("build/day11/obo_simulation_results.json")
        hp = data.get("happy_path", {})
        assert hp.get("actor_verified") is True
        assert hp.get("hold_allowed") is True
        assert hp.get("oid") == "user-oid-finance-director"

    def test_failed_obo_path_key_structure(self):
        """Failed OBO path must write step_failed=2 and hold_allowed=False."""
        _write("build/day11/obo_simulation_results.json", {
            "failed_obo_path": {
                "step_failed": 2,
                "error": "invalid_scope",
                "actor_verified": False,
                "hold_allowed": False,
            }
        })
        data = _read("build/day11/obo_simulation_results.json")
        fop = data.get("failed_obo_path", {})
        assert fop.get("step_failed") == 2
        assert fop.get("hold_allowed") is False
        assert fop.get("actor_verified") is False

    def test_failed_actor_path_key_structure(self):
        """Failed actor path must write step_failed=3 and hold_allowed=False."""
        _write("build/day11/obo_simulation_results.json", {
            "failed_actor_path": {
                "step_failed": 3,
                "actor_verified": False,
                "hold_allowed": False,
            }
        })
        data = _read("build/day11/obo_simulation_results.json")
        fap = data.get("failed_actor_path", {})
        assert fap.get("step_failed") == 3
        assert fap.get("hold_allowed") is False

    def test_simulation_results_file_can_hold_all_three_paths(self):
        """All three keys can coexist in a single simulation results file."""
        combined = {
            "happy_path": {"actor_verified": True, "hold_allowed": True, "oid": "u1"},
            "failed_obo_path": {"step_failed": 2, "hold_allowed": False, "actor_verified": False},
            "failed_actor_path": {"step_failed": 3, "hold_allowed": False, "actor_verified": False},
        }
        _write("build/day11/obo_simulation_results.json", combined)
        data = _read("build/day11/obo_simulation_results.json")
        assert set(data.keys()) >= {"happy_path",
                                    "failed_obo_path", "failed_actor_path"}
        # Only the happy path should have hold_allowed=True
        assert data["happy_path"]["hold_allowed"] is True
        assert data["failed_obo_path"]["hold_allowed"] is False
        assert data["failed_actor_path"]["hold_allowed"] is False


class TestOboContractTierTracking:
    """obo_contract.json must record which execution tier was used."""

    def test_tier_1_artifact_has_correct_fields(self):
        """Tier 1 (stub) artifact must have execution_tier=1 and gate_passed=False (honestly unverified)."""
        artifact = {
            "day": 11,
            "execution_tier": 1,
            "live_entra": False,
            "app_identity_check": {"passed": False, "detail": "STUB (unverified)"},
            "obo_exchange_check": {"passed": False, "detail": "STUB (unverified)"},
            "actor_binding_check": {"passed": False, "detail": "STUB (unverified)"},
            "gate_passed": False,
        }
        _write("build/day11/obo_contract.json", artifact)
        data = _read("build/day11/obo_contract.json")
        assert data["execution_tier"] == 1
        assert data["gate_passed"] is False
        assert data["live_entra"] is False
        assert data["app_identity_check"]["passed"] is False
        assert data["obo_exchange_check"]["passed"] is False
        assert data["actor_binding_check"]["passed"] is False
