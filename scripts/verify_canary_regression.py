#!/usr/bin/env python3
"""
scripts/verify_canary_regression.py
-----------------------------------
Generates build/day14/canary_regression_report.json.

Modes:
- Training preview: if no live canary metrics are configured, write a
  training-only preview artifact.
- Authoritative mode: if the required canary metric inputs are configured,
  compare the candidate revision against the baseline and write
  authoritative promotion evidence.

Environment variables for authoritative mode:
    AEGISAP_CANARY_REVISION
    AEGISAP_STABLE_REVISION
    AEGISAP_CANARY_F1
    AEGISAP_ERROR_RATE_CANARY
    AEGISAP_ERROR_RATE_STABLE

Optional:
    AEGISAP_BASELINE_F1
    AEGISAP_CANARY_MAX_ERROR_RATE         default: 0.005
    AEGISAP_CANARY_REGRESSIONS            comma-separated
    AEGISAP_CANARY_PROMOTED               true/false
    AEGISAP_CANARY_ROLLED_BACK            true/false
    AEGISAP_CORRELATION_ID
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = _ROOT / "build" / "day14"


def main() -> int:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    required = [
        "AEGISAP_CANARY_REVISION",
        "AEGISAP_STABLE_REVISION",
        "AEGISAP_CANARY_F1",
        "AEGISAP_ERROR_RATE_CANARY",
        "AEGISAP_ERROR_RATE_STABLE",
    ]
    if all(os.environ.get(key, "").strip() for key in required):
        return _run_authoritative()
    return _run_training_preview()


def _run_training_preview() -> int:
    report = {
        "correlation_id": os.environ.get("AEGISAP_CORRELATION_ID", str(uuid.uuid4())),
        "canary_revision": os.environ.get("AEGISAP_CANARY_REVISION", "aegisap-canary-stub"),
        "stable_revision": os.environ.get("AEGISAP_STABLE_REVISION", "aegisap-stable-stub"),
        "baseline_f1": _load_baseline_f1(),
        "canary_f1": 0.93,
        "f1_delta": round(0.93 - _load_baseline_f1(), 4),
        "error_rate_stable": 0.002,
        "error_rate_canary": 0.002,
        "max_error_rate": _load_max_error_rate(),
        "regressions": [],
        "promoted": False,
        "rolled_back": False,
        "passed": False,
        "promotion_gate_passed": False,
        "training_artifact": True,
        "authoritative_evidence": False,
        "execution_tier": 1,
        "written_by": "verify_canary_regression",
        "note": (
            "TRAINING_ONLY: canary artifact scaffold only. Provide live canary metrics "
            "to produce authoritative promotion evidence."
        ),
    }
    _write(report)
    print("TRAINING_ONLY: wrote preview canary regression artifact.")
    return 0


def _run_authoritative() -> int:
    baseline_f1 = _load_baseline_f1()
    canary_f1 = float(os.environ["AEGISAP_CANARY_F1"])
    error_rate_canary = float(os.environ["AEGISAP_ERROR_RATE_CANARY"])
    error_rate_stable = float(os.environ["AEGISAP_ERROR_RATE_STABLE"])
    max_error_rate = _load_max_error_rate()
    regressions = _load_regressions()

    if canary_f1 < baseline_f1:
        regressions.append(
            f"f1_below_baseline:{canary_f1:.4f}<{baseline_f1:.4f}"
        )
    if error_rate_canary > max_error_rate:
        regressions.append(
            f"error_rate_above_threshold:{error_rate_canary:.4f}>{max_error_rate:.4f}"
        )

    promoted = _parse_bool("AEGISAP_CANARY_PROMOTED", default=not regressions)
    rolled_back = _parse_bool("AEGISAP_CANARY_ROLLED_BACK", default=bool(regressions))
    passed = not regressions

    report = {
        "correlation_id": os.environ.get("AEGISAP_CORRELATION_ID", str(uuid.uuid4())),
        "canary_revision": os.environ["AEGISAP_CANARY_REVISION"],
        "stable_revision": os.environ["AEGISAP_STABLE_REVISION"],
        "baseline_f1": baseline_f1,
        "canary_f1": canary_f1,
        "f1_delta": round(canary_f1 - baseline_f1, 4),
        "error_rate_stable": error_rate_stable,
        "error_rate_canary": error_rate_canary,
        "max_error_rate": max_error_rate,
        "regressions": regressions,
        "promoted": promoted,
        "rolled_back": rolled_back,
        "passed": passed,
        "promotion_gate_passed": passed,
        "training_artifact": False,
        "authoritative_evidence": True,
        "execution_tier": 2,
        "written_by": "verify_canary_regression",
        "note": "LIVE_CANARY_EVIDENCE",
    }
    _write(report)
    if passed:
        print("OK: authoritative canary regression evidence written.")
        return 0
    print("FAIL: canary regressions detected.", file=sys.stderr)
    return 1


def _load_baseline_f1() -> float:
    override = os.environ.get("AEGISAP_BASELINE_F1", "").strip()
    if override:
        return float(override)

    path = _ROOT / "build" / "day8" / "regression_baseline.json"
    if not path.exists():
        return 0.92
    try:
        payload = json.loads(path.read_text())
        if isinstance(payload.get("scores"), dict):
            scores = payload["scores"]
            for key in ("faithfulness", "compliance_decision_accuracy", "mandatory_escalation_recall"):
                if key in scores:
                    return float(scores[key])
        if "accuracy" in payload:
            return float(payload["accuracy"])
    except Exception:
        pass
    return 0.92


def _load_max_error_rate() -> float:
    raw = os.environ.get("AEGISAP_CANARY_MAX_ERROR_RATE", "").strip()
    return float(raw) if raw else 0.005


def _load_regressions() -> list[str]:
    raw = os.environ.get("AEGISAP_CANARY_REGRESSIONS", "").strip()
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def _parse_bool(name: str, *, default: bool) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "y", "on"}


def _write(report: dict) -> None:
    path = BUILD_DIR / "canary_regression_report.json"
    path.write_text(json.dumps(report, indent=2))
    print(f"Wrote {path}")


if __name__ == "__main__":
    sys.exit(main())
