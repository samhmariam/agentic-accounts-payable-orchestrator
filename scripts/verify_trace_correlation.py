#!/usr/bin/env python3
"""
scripts/verify_trace_correlation.py
-----------------------------------
Generates build/day14/trace_correlation_report.json.

Modes:
- Training preview: if no live trace inputs are configured, derive a preview from
  build artifacts and mark it training-only.
- Authoritative mode: if APP Insights/LangSmith trace arguments are configured,
  verify cross-sink correlation via scripts/check_traces.py and write an
  authoritative report.

Environment variables for authoritative mode:
    AEGISAP_WORKFLOW_RUN_ID
    AEGISAP_DEPLOYMENT_REVISION
    AEGISAP_AZURE_APP_ID
    AEGISAP_LANGSMITH_PROJECT

Optional:
    AEGISAP_CORRELATION_ID
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

BUILD_DIR = _ROOT / "build" / "day14"


def main() -> int:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    correlation_id = os.environ.get("AEGISAP_CORRELATION_ID", str(uuid.uuid4()))

    workflow_run_id = os.environ.get("AEGISAP_WORKFLOW_RUN_ID", "")
    revision = os.environ.get("AEGISAP_DEPLOYMENT_REVISION", "")
    azure_app_id = os.environ.get("AEGISAP_AZURE_APP_ID", "")
    langsmith_project = os.environ.get("AEGISAP_LANGSMITH_PROJECT", "")

    if workflow_run_id and revision and azure_app_id and langsmith_project:
        return _run_authoritative(
            correlation_id=correlation_id,
            workflow_run_id=workflow_run_id,
            revision=revision,
            azure_app_id=azure_app_id,
            langsmith_project=langsmith_project,
        )

    return _run_training_preview(correlation_id=correlation_id)


def _run_training_preview(*, correlation_id: str) -> int:
    from aegisap.traceability.correlation import TraceCorrelator

    correlator = TraceCorrelator.from_build_artifacts()
    report = correlator.run().to_dict()
    report.update(
        {
            "correlation_id": correlation_id,
            "training_artifact": True,
            "authoritative_evidence": False,
            "execution_tier": 1,
            "note": (
                "TRAINING_ONLY: derived from local build artifacts. "
                "Provide live trace inputs for authoritative cross-sink verification."
            ),
        }
    )
    _write(report)
    print("Wrote training-only trace correlation preview.")
    return 0


def _run_authoritative(
    *,
    correlation_id: str,
    workflow_run_id: str,
    revision: str,
    azure_app_id: str,
    langsmith_project: str,
) -> int:
    cmd = [
        sys.executable,
        str(_ROOT / "scripts" / "check_traces.py"),
        "--workflow-run-id",
        workflow_run_id,
        "--revision",
        revision,
        "--azure-app-id",
        azure_app_id,
        "--langsmith-project",
        langsmith_project,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        report = {
            "correlation_id": correlation_id,
            "total_traces": 0,
            "correlated": 0,
            "uncorrelated": 1,
            "dual_sink_required": True,
            "dual_sink_satisfied": False,
            "passed": False,
            "details": [{"issue": "check_traces_failed", "stderr": result.stderr.strip()}],
            "training_artifact": False,
            "authoritative_evidence": True,
            "execution_tier": 2,
            "note": "LIVE_TRACE_CHECK_FAILED",
        }
        _write(report)
        print(result.stderr.strip(), file=sys.stderr)
        return 1

    parsed = json.loads(result.stdout)
    report = {
        "correlation_id": correlation_id,
        "workflow_run_id": workflow_run_id,
        "revision": revision,
        "total_traces": 2,
        "correlated": 2,
        "uncorrelated": 0,
        "dual_sink_required": True,
        "dual_sink_satisfied": True,
        "passed": True,
        "details": [parsed],
        "training_artifact": False,
        "authoritative_evidence": True,
        "execution_tier": 2,
        "note": "LIVE_CROSS_SINK_VERIFIED",
    }
    (_ROOT / "build" / "day14" / "log_analytics_sink_verified.json").write_text(
        json.dumps(
            {
                "correlation_id": correlation_id,
                "workflow_run_id": workflow_run_id,
                "revision": revision,
                "verified": True,
                "written_by": "verify_trace_correlation",
            },
            indent=2,
        )
    )
    _write(report)
    print("OK: authoritative trace correlation verified across Azure + LangSmith.")
    return 0


def _write(report: dict) -> None:
    path = BUILD_DIR / "trace_correlation_report.json"
    path.write_text(json.dumps(report, indent=2))
    print(f"Wrote {path}")


if __name__ == "__main__":
    sys.exit(main())
