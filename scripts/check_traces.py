#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import time
from typing import Any

from langsmith import Client


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Poll Azure Monitor and LangSmith for correlated traces.")
    parser.add_argument("--workflow-run-id", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--azure-app-id", required=True)
    parser.add_argument("--langsmith-project", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument("--poll-interval-seconds", type=int, default=15)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    deadline = time.time() + args.timeout_seconds
    azure_hit: dict[str, Any] | None = None
    langsmith_hit: dict[str, Any] | None = None

    while time.time() < deadline and (azure_hit is None or langsmith_hit is None):
        if azure_hit is None:
            azure_hit = _query_azure(args.azure_app_id, args.workflow_run_id, args.revision)
        if langsmith_hit is None:
            langsmith_hit = _query_langsmith(args.langsmith_project, args.workflow_run_id, args.revision)
        if azure_hit is not None and langsmith_hit is not None:
            break
        time.sleep(args.poll_interval_seconds)

    if azure_hit is None or langsmith_hit is None:
        raise SystemExit(
            json.dumps(
                {
                    "status": "failed",
                    "azure_found": azure_hit is not None,
                    "langsmith_found": langsmith_hit is not None,
                },
                indent=2,
            )
        )
    print(json.dumps({"status": "ok", "azure": azure_hit, "langsmith": langsmith_hit}, indent=2))


def _query_azure(app_id: str, workflow_run_id: str, revision: str) -> dict[str, Any] | None:
    query = (
        "traces "
        f"| where tostring(customDimensions['aegis.workflow_run_id']) == '{workflow_run_id}' "
        f"or tostring(customDimensions['aegisap.workflow_run_id']) == '{workflow_run_id}' "
        f"| where tostring(customDimensions['aegisap.revision']) == '{revision}' "
        "| take 1"
    )
    result = subprocess.run(
        [
            "az",
            "monitor",
            "app-insights",
            "query",
            "--app",
            app_id,
            "--analytics-query",
            query,
            "-o",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    payload = json.loads(result.stdout)
    tables = payload.get("tables") or []
    if not tables or not tables[0].get("rows"):
        return None
    return {"workflow_run_id": workflow_run_id, "revision": revision}


def _query_langsmith(project_name: str, workflow_run_id: str, revision: str) -> dict[str, Any] | None:
    client = Client()
    for run in client.list_runs(project_name=project_name, is_root=True, limit=100):
        metadata = (((getattr(run, "extra", None) or {}).get("metadata")) or {})
        if metadata.get("workflow_run_id") == workflow_run_id and (
            metadata.get("deployment_revision") == revision or metadata.get("aegisap_revision") == revision
        ):
            return {"run_id": str(run.id), "workflow_run_id": workflow_run_id, "revision": revision}
    return None


if __name__ == "__main__":
    main()
