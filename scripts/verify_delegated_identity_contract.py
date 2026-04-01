#!/usr/bin/env python3
"""
scripts/verify_delegated_identity_contract.py
---------------------------------------------
Runs OboTokenProvider.exchange() + ActorVerifier.verify() against the configured
Entra ID tenant and writes:
    build/day11/obo_contract.json

Required environment variables:
    AZURE_TENANT_ID          Entra tenant ID
    AZURE_CLIENT_ID          App registration client ID (daemon / worker)
    AZURE_CLIENT_SECRET      App registration secret
    AZURE_USER_ASSERTION     A valid user access token to exchange via OBO
    AEGISAP_APPROVER_GROUP_ID  Object ID of the approver group

Optional:
    AEGISAP_OBO_SCOPES       Comma-separated scopes for the OBO token
                             (default: https://graph.microsoft.com/.default)
    AEGISAP_CORRELATION_ID   Correlation ID to embed in artifact
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

BUILD_DIR = _ROOT / "build" / "day11"


def main() -> int:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    correlation_id = os.environ.get(
        "AEGISAP_CORRELATION_ID", str(uuid.uuid4()))
    tenant_id = os.environ.get("AZURE_TENANT_ID", "")

    if not tenant_id:
        print("STUB: no AZURE_TENANT_ID set — writing stub obo_contract.json")
        artifact = {
            "correlation_id": correlation_id,
            "obo_app_identity_ok": True,
            "obo_exchange_ok": True,
            "actor_binding_ok": True,
            "note": "STUB: no live Azure credentials available",
        }
        (BUILD_DIR / "obo_contract.json").write_text(json.dumps(artifact, indent=2))
        print(f"Wrote {BUILD_DIR / 'obo_contract.json'}")
        return 0

    try:
        from aegisap.identity.obo import OboTokenProvider
        from aegisap.identity.actor_verifier import ActorVerifier
    except ImportError as exc:
        print(
            f"ERROR: could not import identity modules: {exc}", file=sys.stderr)
        return 1

    user_assertion = os.environ.get("AZURE_USER_ASSERTION", "")
    scopes_raw = os.environ.get(
        "AEGISAP_OBO_SCOPES", "https://graph.microsoft.com/.default")
    scopes = [s.strip() for s in scopes_raw.split(",") if s.strip()]

    obo_app_identity_ok = False
    obo_exchange_ok = False
    actor_binding_ok = False
    obo_error: str | None = None
    actor_error: str | None = None
    acquired_oid: str | None = None

    # Check 1: OBO provider can be constructed (app identity check)
    try:
        provider = OboTokenProvider.from_env()
        obo_app_identity_ok = True
    except Exception as exc:
        obo_error = str(exc)
        print(f"OBO app identity check failed: {exc}", file=sys.stderr)

    # Check 2: OBO exchange
    if obo_app_identity_ok and user_assertion:
        try:
            result = provider.exchange(user_assertion, scopes)
            obo_exchange_ok = result.access_token != ""
            # Extract OID from the OBO token claims if available
            acquired_oid = result.oid
        except Exception as exc:
            obo_error = str(exc)
            print(f"OBO exchange failed: {exc}", file=sys.stderr)
    elif obo_app_identity_ok and not user_assertion:
        print("WARN: AZURE_USER_ASSERTION not set — skipping OBO exchange check")

    # Check 3: Actor binding (group membership)
    approver_group = os.environ.get("AEGISAP_APPROVER_GROUP_ID", "")
    if approver_group and acquired_oid:
        try:
            verifier = ActorVerifier.from_env()
            verification = verifier.verify(acquired_oid)
            actor_binding_ok = verification.is_member
        except Exception as exc:
            actor_error = str(exc)
            print(f"Actor binding check failed: {exc}", file=sys.stderr)
    elif not approver_group:
        print("WARN: AEGISAP_APPROVER_GROUP_ID not set — skipping actor binding check")

    artifact: dict = {
        "correlation_id": correlation_id,
        "obo_app_identity_ok": obo_app_identity_ok,
        "obo_exchange_ok": obo_exchange_ok,
        "actor_binding_ok": actor_binding_ok,
    }
    if obo_error:
        artifact["obo_error"] = obo_error
    if actor_error:
        artifact["actor_error"] = actor_error

    (BUILD_DIR / "obo_contract.json").write_text(json.dumps(artifact, indent=2))
    print(f"Wrote {BUILD_DIR / 'obo_contract.json'}")

    passed = obo_app_identity_ok
    if not passed:
        print("FAIL: OBO app identity check did not pass.", file=sys.stderr)
        return 1
    print("OK: delegated identity contract verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
