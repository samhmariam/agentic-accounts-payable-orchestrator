from __future__ import annotations

import os
import uuid
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Any

from aegisap.common.hashing import stable_sha256
from aegisap.security.config import load_security_config

_current_context: ContextVar["WorkflowObservabilityContext | None"] = ContextVar(
    "aegisap_observability_context",
    default=None,
)


def _hashed(value: str | None) -> str | None:
    if not value:
        return None
    return stable_sha256(value)[:16]


@dataclass(slots=True)
class WorkflowObservabilityContext:
    request_id: str
    workflow_run_id: str
    environment: str
    deployment_revision: str
    trace_id: str | None = None
    traceparent: str | None = None
    case_id: str | None = None
    thread_id: str | None = None
    checkpoint_id: str | None = None
    state_version: int | None = None
    plan_version: str | None = None
    policy_version: str | None = None
    actor_type: str | None = None
    outcome_type: str | None = None
    approval_status: str | None = None
    azure_trace_id: str | None = None
    langsmith_project: str | None = None
    langsmith_trace_id: str | None = None
    langsmith_run_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def hashed_case_id(self) -> str | None:
        return _hashed(self.case_id)

    @property
    def hashed_thread_id(self) -> str | None:
        return _hashed(self.thread_id)

    def to_public_dict(self) -> dict[str, str | None]:
        return {
            "workflow_run_id": self.workflow_run_id,
            "trace_id": self.trace_id,
            "checkpoint_id": self.checkpoint_id,
            "langsmith_trace_id": self.langsmith_trace_id,
        }

    def to_state_payload(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "workflow_run_id": self.workflow_run_id,
            "trace_id": self.trace_id,
            "traceparent": self.traceparent,
            "case_id_hash": self.hashed_case_id,
            "thread_id_hash": self.hashed_thread_id,
            "checkpoint_id": self.checkpoint_id,
            "state_version": self.state_version,
            "plan_version": self.plan_version,
            "policy_version": self.policy_version,
            "actor_type": self.actor_type,
            "outcome_type": self.outcome_type,
            "approval_status": self.approval_status,
            "environment": self.environment,
            "deployment_revision": self.deployment_revision,
            "azure_trace_id": self.azure_trace_id,
            "langsmith_project": self.langsmith_project,
            "langsmith_trace_id": self.langsmith_trace_id,
            "langsmith_run_id": self.langsmith_run_id,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_state_payload(
        cls,
        payload: dict[str, Any] | None,
        *,
        request_id: str | None = None,
        workflow_run_id: str | None = None,
        case_id: str | None = None,
        thread_id: str | None = None,
    ) -> "WorkflowObservabilityContext | None":
        if not payload:
            return None
        return cls(
            request_id=request_id or payload.get("request_id") or str(uuid.uuid4()),
            workflow_run_id=workflow_run_id or payload.get("workflow_run_id") or str(uuid.uuid4()),
            trace_id=payload.get("trace_id"),
            traceparent=payload.get("traceparent"),
            case_id=case_id,
            thread_id=thread_id,
            checkpoint_id=payload.get("checkpoint_id"),
            state_version=payload.get("state_version"),
            plan_version=payload.get("plan_version"),
            policy_version=payload.get("policy_version"),
            actor_type=payload.get("actor_type"),
            outcome_type=payload.get("outcome_type"),
            approval_status=payload.get("approval_status"),
            environment=payload.get("environment") or load_security_config().environment,
            deployment_revision=payload.get("deployment_revision")
            or load_security_config().deployment_revision,
            azure_trace_id=payload.get("azure_trace_id"),
            langsmith_project=payload.get("langsmith_project"),
            langsmith_trace_id=payload.get("langsmith_trace_id"),
            langsmith_run_id=payload.get("langsmith_run_id"),
            metadata=dict(payload.get("metadata") or {}),
        )


def make_workflow_observability_context(
    *,
    request_id: str,
    workflow_run_id: str | None = None,
    case_id: str | None = None,
    thread_id: str | None = None,
    checkpoint_id: str | None = None,
    traceparent: str | None = None,
) -> WorkflowObservabilityContext:
    config = load_security_config()
    return WorkflowObservabilityContext(
        request_id=request_id,
        workflow_run_id=workflow_run_id or os.getenv("AEGISAP_WORKFLOW_RUN_ID", "").strip() or str(uuid.uuid4()),
        traceparent=traceparent,
        case_id=case_id,
        thread_id=thread_id,
        checkpoint_id=checkpoint_id,
        environment=config.environment,
        deployment_revision=config.deployment_revision,
        langsmith_project=config.langsmith_project or None,
    )


def bind_observability_context(
    context: WorkflowObservabilityContext | None,
) -> Token[WorkflowObservabilityContext | None]:
    return _current_context.set(context)


def reset_observability_context(token: Token[WorkflowObservabilityContext | None]) -> None:
    _current_context.reset(token)


def get_observability_context() -> WorkflowObservabilityContext | None:
    return _current_context.get()


def update_observability_context(**changes: Any) -> WorkflowObservabilityContext | None:
    current = get_observability_context()
    if current is None:
        return None
    for key, value in changes.items():
        if hasattr(current, key):
            setattr(current, key, value)
        else:
            current.metadata[key] = value
    return current
