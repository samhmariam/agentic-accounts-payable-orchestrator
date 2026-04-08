#!/usr/bin/env python3
"""
scripts/verify_webhook_reliability.py
--------------------------------------
Drains the Service Bus Dead-Letter Queue and runs compensating actions.
Writes:
    build/day13/dlq_drain_report.json
    build/day13/webhook_reliability_report.json

Environment variables:
    AZURE_SERVICEBUS_NAMESPACE_FQDN      Namespace FQDN for MI-based auth
    AZURE_SERVICEBUS_QUEUE_NAME          Queue name
    AEGISAP_CORRELATION_ID               Optional correlation ID
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

BUILD_DIR = _ROOT / "build" / "day13"


def _run() -> int:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    correlation_id = os.environ.get(
        "AEGISAP_CORRELATION_ID", str(uuid.uuid4()))

    sb_namespace = os.environ.get("AZURE_SERVICEBUS_NAMESPACE_FQDN", "")
    sb_queue = os.environ.get("AZURE_SERVICEBUS_QUEUE_NAME", "")

    if not sb_namespace or not sb_queue:
        print("TRAINING_ONLY: no Service Bus namespace/queue configured — writing preview reports")
        dlq_report = {
            "correlation_id": correlation_id,
            "total": 0,
            "retried": 0,
            "archived": 0,
            "error_count": 0,
            "errors": [],
            "training_artifact": True,
            "authoritative_evidence": False,
            "execution_tier": 1,
            "note": "TRAINING_ONLY: no AZURE_SERVICEBUS_NAMESPACE_FQDN or AZURE_SERVICEBUS_QUEUE_NAME",
        }
        reliability_report = {
            "correlation_id": correlation_id,
            "all_handled": True,
            "unhandled_count": 0,
            "checked_webhooks": [],
            "training_artifact": True,
            "authoritative_evidence": False,
            "execution_tier": 1,
            "note": "TRAINING_ONLY: no Service Bus namespace/queue configured",
        }
        _write("dlq_drain_report.json", dlq_report)
        _write("webhook_reliability_report.json", reliability_report)
        return 0

    try:
        from aegisap.integration.dlq_consumer import DlqConsumer
    except ImportError as exc:
        print(
            f"ERROR: could not import integration modules: {exc}", file=sys.stderr)
        return 1

    consumer = DlqConsumer.from_env()
    report = asyncio.run(consumer.drain())
    report_dict = report.to_dict()
    report_dict.update(
        {
            "correlation_id": correlation_id,
            "training_artifact": False,
            "authoritative_evidence": True,
            "execution_tier": 2,
            "note": "LIVE_DLQ_DRAIN",
        }
    )
    reliability_report = {
        "correlation_id": correlation_id,
        "all_handled": report_dict.get("error_count", 0) == 0,
        "unhandled_count": report_dict.get("error_count", 0),
        "checked_webhooks": [sb_queue],
        "training_artifact": False,
        "authoritative_evidence": True,
        "execution_tier": 2,
        "note": "LIVE_DLQ_DRAIN",
    }
    _write("dlq_drain_report.json", report_dict)
    _write("webhook_reliability_report.json", reliability_report)

    print(f"DLQ drain complete: total={report_dict.get('total', 0)}, "
          f"errors={report_dict.get('error_count', 0)}")

    if not reliability_report["all_handled"]:
        print("FAIL: not all DLQ messages were handled.", file=sys.stderr)
        return 1
    return 0


def _write(filename: str, report: dict) -> None:
    path = BUILD_DIR / filename
    path.write_text(json.dumps(report, indent=2))
    print(f"Wrote {path}")


def main() -> int:
    return _run()


if __name__ == "__main__":
    sys.exit(main())
