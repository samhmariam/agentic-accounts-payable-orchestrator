from __future__ import annotations

import logging
import uuid
from typing import Any

from aegisap.observability.context import WorkflowObservabilityContext
from aegisap.security.config import load_security_config
from aegisap.security.key_vault import get_secret_value

logger = logging.getLogger("aegisap.observability.langsmith")


def langsmith_enabled() -> bool:
    config = load_security_config()
    return bool(config.langsmith_project and (config.langsmith_api_key or config.key_vault_uri))


def ensure_langsmith_ids(context: WorkflowObservabilityContext) -> WorkflowObservabilityContext:
    if not context.langsmith_trace_id:
        context.langsmith_trace_id = str(uuid.uuid4())
    if not context.langsmith_run_id:
        context.langsmith_run_id = str(uuid.uuid4())
    return context


def build_langsmith_metadata(context: WorkflowObservabilityContext) -> dict[str, Any]:
    ensure_langsmith_ids(context)
    return {
        "workflow_run_id": context.workflow_run_id,
        "trace_id": context.trace_id,
        "azure_trace_id": context.azure_trace_id or context.trace_id,
        "thread_id_hash": context.hashed_thread_id,
        "case_id_hash": context.hashed_case_id,
        "checkpoint_id": context.checkpoint_id,
        "state_version": context.state_version,
        "plan_version": context.plan_version,
        "policy_version": context.policy_version,
        "environment": context.environment,
        "deployment_revision": context.deployment_revision,
    }


def publish_langsmith_run(
    *,
    context: WorkflowObservabilityContext,
    name: str,
    run_type: str,
    inputs: dict[str, Any] | None = None,
    outputs: dict[str, Any] | None = None,
    error: str | None = None,
    tags: list[str] | None = None,
) -> None:
    if not langsmith_enabled():
        return

    config = load_security_config()
    ensure_langsmith_ids(context)
    api_key = config.langsmith_api_key
    if not api_key and config.key_vault_uri:
        try:
            api_key = get_secret_value(config.langsmith_api_key_secret_name)
        except Exception as exc:  # pragma: no cover - best effort bridge
            logger.warning("langsmith_api_key_lookup_failed: %s", exc)
            return

    if not api_key:
        return

    try:
        from langsmith import Client

        client = Client(api_key=api_key, api_url=config.langsmith_endpoint or None)
        client.create_run(
            id=context.langsmith_run_id,
            trace_id=context.langsmith_trace_id,
            name=name,
            run_type=run_type,
            inputs=inputs or {},
            outputs=outputs or {},
            error=error,
            session_name=config.langsmith_project,
            tags=tags or ["day8", context.environment],
            extra={"metadata": build_langsmith_metadata(context)},
        )
    except Exception as exc:  # pragma: no cover - bridge must stay best effort
        logger.warning("langsmith_run_publish_failed: %s", exc)
