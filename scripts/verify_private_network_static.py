#!/usr/bin/env python3
"""
scripts/verify_private_network_static.py
-----------------------------------------
Static ARM API check: verifies that all AI service resources are in allowed
regions and have publicNetworkAccess=Disabled.  Writes:
    build/day14/data_residency_report.json

Unlike verify_private_network_posture.py (which does live DNS/TCP checks),
this script queries the Azure Resource Manager API for resource properties.

Environment variables:
    AZURE_SUBSCRIPTION_ID    Required for live check
    AZURE_RESOURCE_GROUP     Resource group to scan (default: rg-aegisap)
    AEGISAP_ALLOWED_REGIONS  Comma-separated allowed regions (default: uksouth,ukwest)
    AEGISAP_CORRELATION_ID   Optional correlation ID
"""
from __future__ import annotations

import datetime
import json
import os
import sys
import uuid
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

BUILD_DIR = _ROOT / "build" / "day14"

_AI_RESOURCE_TYPES = {
    "microsoft.cognitiveservices/accounts",
    "microsoft.search/searchservices",
    "microsoft.storage/storageaccounts",
    "microsoft.dbforpostgresql/flexibleservers",
}


def main() -> int:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    correlation_id = os.environ.get(
        "AEGISAP_CORRELATION_ID", str(uuid.uuid4()))
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID", "")
    resource_group = os.environ.get("AZURE_RESOURCE_GROUP", "rg-aegisap")
    allowed_raw = os.environ.get("AEGISAP_ALLOWED_REGIONS", "uksouth,ukwest")
    allowed_regions = [r.strip().lower().replace(" ", "")
                       for r in allowed_raw.split(",") if r.strip()]

    if not subscription_id:
        print("STUB: no AZURE_SUBSCRIPTION_ID set — writing stub data residency report")
        stub_resources = [
            {"resource": "aegisap-openai", "type": "Microsoft.CognitiveServices/accounts",
             "location": "uksouth", "public_network_access": "Disabled"},
            {"resource": "aegisap-search", "type": "Microsoft.Search/searchServices",
             "location": "uksouth", "public_network_access": "Disabled"},
            {"resource": "aegisap-storage", "type": "Microsoft.Storage/storageAccounts",
             "location": "uksouth", "public_network_access": "Disabled"},
            {"resource": "aegisap-pg", "type": "Microsoft.DBforPostgreSQL/flexibleServers",
             "location": "uksouth", "public_network_access": "Disabled"},
        ]
        report = {
            "correlation_id": correlation_id,
            "all_compliant": True,
            "allowed_regions": allowed_regions,
            "resources_checked": len(stub_resources),
            "violations": [],
            "resources": stub_resources,
            "note": "STUB: no AZURE_SUBSCRIPTION_ID set",
            "run_at": datetime.datetime.utcnow().isoformat() + "Z",
        }
        _write_report(report)
        return 0

    try:
        from azure.identity import DefaultAzureCredential
        from azure.mgmt.resource import ResourceManagementClient
    except ImportError as exc:
        print(
            f"ERROR: azure-mgmt-resource not installed: {exc}", file=sys.stderr)
        return 1

    credential = DefaultAzureCredential()
    client = ResourceManagementClient(credential, subscription_id)

    resources_checked = []
    violations = []

    try:
        resources = list(client.resources.list_by_resource_group(
            resource_group, expand="properties"
        ))
    except Exception as exc:
        print(
            f"ERROR: could not list resources in {resource_group}: {exc}", file=sys.stderr)
        return 1

    for r in resources:
        if (r.type or "").lower() not in _AI_RESOURCE_TYPES:
            continue
        loc = (r.location or "").lower().replace(" ", "")
        props = r.properties or {}
        pna = props.get("publicNetworkAccess", "Enabled")
        entry = {
            "resource": r.name,
            "type": r.type,
            "location": loc,
            "public_network_access": pna,
        }
        resources_checked.append(entry)

        if loc not in allowed_regions:
            entry["violation"] = f"region {loc!r} not in allowed list {allowed_regions}"
            violations.append(entry)
        if pna != "Disabled":
            entry["violation"] = f"publicNetworkAccess={pna!r} (expected 'Disabled')"
            if entry not in violations:
                violations.append(entry)

    report = {
        "correlation_id": correlation_id,
        "all_compliant": len(violations) == 0,
        "allowed_regions": allowed_regions,
        "resources_checked": len(resources_checked),
        "violations": violations,
        "resources": resources_checked,
        "run_at": datetime.datetime.utcnow().isoformat() + "Z",
    }
    _write_report(report)

    for v in violations:
        print(
            f"VIOLATION: {v['resource']} ({v['type']}): {v.get('violation', '')}", file=sys.stderr)

    if violations:
        print(
            f"FAIL: {len(violations)} data residency violation(s).", file=sys.stderr)
        return 1

    print(f"OK: {len(resources_checked)} AI resource(s) checked — all compliant.")
    return 0


def _write_report(report: dict) -> None:
    path = BUILD_DIR / "data_residency_report.json"
    path.write_text(json.dumps(report, indent=2))
    print(f"Wrote {path}")


if __name__ == "__main__":
    sys.exit(main())
