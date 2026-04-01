#!/usr/bin/env python3
"""
scripts/verify_webhook_reliability.py
--------------------------------------
Drains the Service Bus Dead-Letter Queue and runs compensating actions.
Writes:
    build/day13/dlq_drain_report.json

Environment variables:
    AZURE_SERVICE_BUS_CONNECTION_STRING  OR
    AZURE_SERVICE_BUS_NAMESPACE          (for MI-based auth)
    AEGISAP_DLQ_QUEUE_NAME               Queue name (default: invoice-submissions)
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


async def _run() -> int:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    correlation_id = os.environ.get(
        "AEGISAP_CORRELATION_ID", str(uuid.uuid4()))

    sb_conn = os.environ.get("AZURE_SERVICE_BUS_CONNECTION_STRING", "")
    sb_namespace = os.environ.get("AZURE_SERVICE_BUS_NAMESPACE", "")

    if not sb_conn and not sb_namespace:
        print("STUB: no Service Bus connection configured — writing empty DLQ report")
        report = {
            "correlation_id": correlation_id,
            "drained": 0,
            "transient_count": 0,
            "non_transient_count": 0,
            "all_handled": True,
            "messages": [],
            "note": "STUB: no AZURE_SERVICE_BUS_CONNECTION_STRING or AZURE_SERVICE_BUS_NAMESPACE",
        }
        _write(report)
        return 0

    try:
        from aegisap.integration.dlq_consumer import DlqConsumer
        from aegisap.integration.compensating_action import CompensatingActionRunner
    except ImportError as exc:
        print(
            f"ERROR: could not import integration modules: {exc}", file=sys.stderr)
        return 1

    runner = CompensatingActionRunner()

    @runner.register("non_transient")
    async def _mark_for_review(message_id: str, payload: dict) -> dict:
        invoice_id = payload.get("invoice_id", message_id)
        print(f"  Compensating: marking {invoice_id} for human review")
        return {"action": "marked_for_review", "invoice_id": invoice_id}

    consumer = DlqConsumer.from_env()
    report = await consumer.drain(compensating_runner=runner)
    report_dict = report.to_dict()
    report_dict["correlation_id"] = correlation_id
    _write(report_dict)

    print(f"DLQ drain complete: drained={report_dict.get('drained', 0)}, "
          f"all_handled={report_dict.get('all_handled', False)}")

    if not report_dict.get("all_handled", False):
        print("FAIL: not all DLQ messages were handled.", file=sys.stderr)
        return 1
    return 0


def _write(report: dict) -> None:
    path = BUILD_DIR / "dlq_drain_report.json"
    path.write_text(json.dumps(report, indent=2))
    print(f"Wrote {path}")


def main() -> int:
    return asyncio.run(_run())


if __name__ == "__main__":
    sys.exit(main())
