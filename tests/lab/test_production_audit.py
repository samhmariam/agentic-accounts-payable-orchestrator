from __future__ import annotations

import json
from pathlib import Path

from aegisap.lab import audit


def test_run_production_audit_writes_preview_when_resource_group_missing(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("AZURE_RESOURCE_GROUP", raising=False)
    out_path = tmp_path / "production_audit.json"

    payload = audit.run_production_audit(out_path=out_path)

    assert out_path.exists()
    assert payload["training_artifact"] is True
    assert payload["authoritative_evidence"] is False
    assert payload["checks"] == []


def test_run_production_audit_day_preview_includes_relevant_constraints(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("AZURE_RESOURCE_GROUP", raising=False)

    payload = audit.run_production_audit(day="12", out_path=tmp_path / "production_audit_day12.json")

    assert payload["day"] == "12"
    assert "no_public_endpoints" in payload["relevant_constraints"]
    assert "private_dns_resolution" in payload["relevant_constraints"]


def test_run_production_audit_reports_live_passes(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AZURE_RESOURCE_GROUP", "rg-aegisap")
    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://search-demo.search.windows.net")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://openai-demo.openai.azure.com/")
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_URL", "https://storageacct.blob.core.windows.net")
    monkeypatch.setenv("AZURE_KEY_VAULT_URI", "https://vault-demo.vault.azure.net/")

    def fake_run_az_json(*args: str):
        if args[:3] == ("search", "service", "show"):
            return {"publicNetworkAccess": "Disabled", "disableLocalAuth": True}
        if args[:3] == ("cognitiveservices", "account", "show"):
            return {"properties": {"publicNetworkAccess": "Disabled"}}
        if args[:3] == ("storage", "account", "show"):
            return {
                "publicNetworkAccess": "Disabled",
                "allowBlobPublicAccess": False,
                "networkRuleSet": {"defaultAction": "Deny"},
            }
        if args[:2] == ("keyvault", "show"):
            return {
                "properties": {
                    "publicNetworkAccess": "Disabled",
                    "networkAcls": {"defaultAction": "Deny"},
                }
            }
        raise AssertionError(f"Unexpected az invocation: {args}")

    monkeypatch.setattr(audit, "_run_az_json", fake_run_az_json)
    out_path = tmp_path / "production_audit.json"

    payload = audit.run_production_audit(out_path=out_path)

    assert out_path.exists()
    assert payload["training_artifact"] is False
    assert payload["authoritative_evidence"] is True
    assert payload["all_passed"] is True
    assert all(check["status"] == audit.PASS for check in payload["checks"])

    saved = json.loads(out_path.read_text(encoding="utf-8"))
    assert saved["all_passed"] is True


def test_run_production_audit_day_uses_constraint_specific_checks(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AZURE_RESOURCE_GROUP", "rg-aegisap")
    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://search-demo.search.windows.net")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://openai-demo.openai.azure.com/")
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_URL", "https://storageacct.blob.core.windows.net")
    monkeypatch.setenv("AZURE_KEY_VAULT_URI", "https://vault-demo.vault.azure.net/")

    def fake_run_az_json(*args: str):
        if args[:3] == ("search", "service", "show"):
            return {"publicNetworkAccess": "Disabled", "disableLocalAuth": True}
        if args[:3] == ("cognitiveservices", "account", "show"):
            return {"properties": {"publicNetworkAccess": "Disabled"}}
        if args[:3] == ("storage", "account", "show"):
            return {
                "publicNetworkAccess": "Disabled",
                "allowBlobPublicAccess": False,
                "networkRuleSet": {"defaultAction": "Deny"},
            }
        if args[:2] == ("keyvault", "show"):
            return {
                "properties": {
                    "publicNetworkAccess": "Disabled",
                    "networkAcls": {"defaultAction": "Deny"},
                }
            }
        raise AssertionError(f"Unexpected az invocation: {args}")

    monkeypatch.setattr(audit, "_run_az_json", fake_run_az_json)

    payload = audit.run_production_audit(day="08", out_path=tmp_path / "production_audit_day08.json")

    check_names = {check["check"] for check in payload["checks"]}
    assert payload["all_passed"] is True
    assert {"search_posture", "openai_posture", "storage_posture", "key_vault_posture"} <= check_names
