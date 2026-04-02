#!/usr/bin/env python3
"""
scripts/verify_private_network_posture.py
-----------------------------------------
Runs NetworkPostureProbe against configured AI service hostnames and writes:
    build/day12/private_network_posture.json   (always)
    build/day12/external_sink_disabled.json    (only if all_passed=True)

Required for gate_private_network_posture (live staging gate).

Environment variables:
    AEGISAP_AI_HOSTNAMES  Comma-separated hostnames to probe
                          e.g. myopenai.openai.azure.com,mysearch.search.windows.net
                          Falls back to individual AZURE_*_ENDPOINT vars.
    AEGISAP_CORRELATION_ID  Optional correlation ID.
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

BUILD_DIR = _ROOT / "build" / "day12"


def main() -> int:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    correlation_id = os.environ.get(
        "AEGISAP_CORRELATION_ID", str(uuid.uuid4()))

    hostnames_raw = os.environ.get("AEGISAP_AI_HOSTNAMES", "")
    sink_path = BUILD_DIR / "external_sink_disabled.json"

    if not hostnames_raw:
        print("TRAINING_ONLY: no AEGISAP_AI_HOSTNAMES set — writing preview artifact")
        posture = {
            "correlation_id": correlation_id,
            "all_passed": False,
            "training_artifact": True,
            "authoritative_evidence": False,
            "execution_tier": 1,
            "written_by": "verify_private_network_posture",
            "services": [],
            "note": "TRAINING_ONLY: no hostnames configured",
        }
        (BUILD_DIR / "private_network_posture.json").write_text(json.dumps(posture, indent=2))
        if sink_path.exists():
            sink_path.unlink()
        print(f"Wrote training preview to {BUILD_DIR / 'private_network_posture.json'}")
        return 0

    try:
        from aegisap.network.private_endpoint_probe import NetworkPostureProbe
    except ImportError as exc:
        print(
            f"ERROR: could not import NetworkPostureProbe: {exc}", file=sys.stderr)
        return 1

    probe = NetworkPostureProbe.from_env()
    result = probe.run()
    probe.write_artifacts(result)

    posture_path = BUILD_DIR / "private_network_posture.json"
    posture = json.loads(posture_path.read_text())
    posture["correlation_id"] = correlation_id
    posture_path.write_text(json.dumps(posture, indent=2))

    if result.all_passed and sink_path.exists():
        sink = json.loads(sink_path.read_text())
        sink["correlation_id"] = correlation_id
        sink_path.write_text(json.dumps(sink, indent=2))

    print(f"Probe complete: all_passed={result.all_passed}")
    for svc in result.services:
        status = "PASS" if svc.passed else "FAIL"
        print(f"  [{status}] {svc.hostname}: dns_private={svc.dns_private}, "
              f"public_reachable={svc.public_reachable}")

    if not result.all_passed:
        print("FAIL: one or more services did not pass the private network posture check.",
              file=sys.stderr)
        return 1

    print("OK: all services have private endpoints and public access is disabled.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
