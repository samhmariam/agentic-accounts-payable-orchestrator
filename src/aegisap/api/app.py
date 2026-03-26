from __future__ import annotations

import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request

from aegisap.api.models import Day1IntakeRequest, Day4RunRequest, Day5ResumeRequest
from aegisap.day_01.service import canonicalize_with_candidate, run_day_01_intake
from aegisap.day5.workflow.resume_service import ResumeTokenCodec
from aegisap.day5.workflow.training_runtime import create_day5_pause, load_thread_snapshot, resume_day5_case
from aegisap.observability import (
    bind_observability_context,
    get_observability_context,
    make_trace_context,
    reset_observability_context,
    start_workflow_span,
    update_observability_context,
)
from aegisap.observability.azure_monitor import configure_azure_monitor_exporter
from aegisap.observability.langsmith_bridge import ensure_langsmith_ids
from aegisap.observability.logging import configure_application_logging, log_structured
from aegisap.security.config import load_security_config
from aegisap.security.credentials import redact_credential_summary
from aegisap.security.key_vault import get_resume_token_secret
from aegisap.security.policy import validate_security_posture
from aegisap.training.postgres import build_store_from_env
from aegisap.training.labs import run_day4_case_artifact

logger = logging.getLogger("aegisap.api")


def _configure_observability() -> None:
    configure_application_logging()
    config = load_security_config()
    validate_security_posture(config)
    configure_azure_monitor_exporter(config)
    log_structured(logger, "security_runtime_started", **redact_credential_summary())


@asynccontextmanager
async def lifespan(app: FastAPI):
    _configure_observability()
    yield


app = FastAPI(title="AegisAP Training Runtime", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def add_request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = request_id
    trace_context = make_trace_context(
        request_id=request_id,
        traceparent=request.headers.get("traceparent"),
    )
    token = bind_observability_context(trace_context)
    request.state.observability = trace_context
    try:
        response = await call_next(request)
        current = getattr(request.state, "observability", None) or get_observability_context()
        response.headers["x-request-id"] = request_id
        response.headers["x-trace-id"] = current.trace_id or ""
        response.headers["x-workflow-run-id"] = current.workflow_run_id
        return response
    finally:
        reset_observability_context(token)


def _log(event: str, **fields: object) -> None:
    log_structured(logger, event, **fields)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/day1/intake")
async def day1_intake(request: Day1IntakeRequest, raw_request: Request) -> dict[str, object]:
    try:
        if request.candidate is not None:
            canonical = canonicalize_with_candidate(request.package, request.candidate)
            mode = "fixture"
        else:
            canonical = run_day_01_intake(request.package)
            mode = "live_azure_openai"
    except Exception as exc:  # pragma: no cover - API behavior test covers shape, not all branches
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _log(
        "day1_intake_completed",
        request_id=raw_request.state.request_id,
        message_id=request.package.message_id,
        invoice_number=canonical.invoice_number,
        mode=mode,
    )
    return {
        "mode": mode,
        "message_id": request.package.message_id,
        "canonical_invoice": canonical.model_dump(mode="json"),
        "correlation": (get_observability_context().to_public_dict() if get_observability_context() else None),
    }


@app.post("/api/day4/cases/run")
async def day4_run_case(request: Day4RunRequest, raw_request: Request) -> dict[str, object]:
    workflow_run_id = str(uuid.uuid4())
    with start_workflow_span(
        request_id=raw_request.state.request_id,
        workflow_run_id=workflow_run_id,
        case_id=request.case_facts.case_id,
        thread_id=request.thread_id or f"thread-{request.case_facts.case_id}",
    ) as workflow_context:
        token = bind_observability_context(workflow_context)
        try:
            ensure_langsmith_ids(workflow_context)
            raw_request.state.observability = workflow_context
            update_observability_context(
                case_id=request.case_facts.case_id,
                thread_id=request.thread_id or f"thread-{request.case_facts.case_id}",
            )
            artifact_path, artifact_payload, state = await run_day4_case_artifact(
                case_facts=request.case_facts,
                planner_mode=request.planner_mode,
                artifact_name=f"{request.case_facts.case_id}_api",
                include_day6_review=request.enable_day6_review,
                thread_id=request.thread_id or f"thread-{request.case_facts.case_id}",
                observability_context=workflow_context,
            )
        finally:
            reset_observability_context(token)
    response: dict[str, object] = {
        "artifact_path": str(artifact_path),
        "planner_mode": request.planner_mode,
        "validated_plan": artifact_payload["validated_plan"],
        "recommendation": state.recommendation,
        "escalation_package": state.escalation_package,
        "day6_review": artifact_payload["day6_review"],
        "correlation": workflow_context.to_public_dict(),
    }

    if request.persist_day5_handoff:
        token_secret = get_resume_token_secret()
        thread_id = request.thread_id or f"thread-{request.case_facts.case_id}"
        assigned_to = request.assigned_to or "controller@example.com"
        try:
            pause_payload = create_day5_pause(
                day4_state=state,
                thread_id=thread_id,
                assigned_to=assigned_to,
                store=build_store_from_env(),
                token_secret=token_secret,
                observability_context=workflow_context,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        response["day5_handoff"] = pause_payload
        _log(
            "day5_pause_created",
            request_id=raw_request.state.request_id,
            trace_id=workflow_context.trace_id,
            thread_id=thread_id,
            approval_task_id=pause_payload["approval_task_id"],
        )

    _log(
        "day4_case_completed",
        request_id=raw_request.state.request_id,
        trace_id=workflow_context.trace_id,
        case_id=request.case_facts.case_id,
        recommendation_ready=state.recommendation is not None,
        day6_outcome=(artifact_payload["day6_review"] or {}).get("outcome"),
    )
    return response


@app.get("/api/day5/threads/{thread_id}")
async def day5_thread(thread_id: str, raw_request: Request) -> dict[str, object]:
    try:
        workflow_context = make_trace_context(
            request_id=raw_request.state.request_id,
            thread_id=thread_id,
        )
        token = bind_observability_context(workflow_context)
        try:
            raw_request.state.observability = workflow_context
            snapshot = load_thread_snapshot(
                store=build_store_from_env(),
                thread_id=thread_id,
                observability_context=workflow_context,
            )
        finally:
            reset_observability_context(token)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    _log(
        "day5_thread_loaded",
        request_id=raw_request.state.request_id,
        trace_id=workflow_context.trace_id,
        thread_id=thread_id,
    )
    return snapshot


@app.post("/api/day5/approvals/{approval_task_id}/resume")
async def day5_resume(
    approval_task_id: str,
    request: Day5ResumeRequest,
    raw_request: Request,
) -> dict[str, object]:
    token_secret = get_resume_token_secret()
    token = ResumeTokenCodec(token_secret).decode(request.resume_token)
    if token.approval_task_id != approval_task_id:
        raise HTTPException(status_code=400, detail="approval_task_id does not match resume token")

    decision = {
        "status": request.decision.get("status", "approved"),
        "comment": request.decision.get("comment", ""),
        "approved_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        workflow_context = make_trace_context(
            request_id=raw_request.state.request_id,
            thread_id=token.thread_id,
            checkpoint_id=token.checkpoint_id,
        )
        token_handle = bind_observability_context(workflow_context)
        try:
            raw_request.state.observability = workflow_context
            resumed = resume_day5_case(
                store=build_store_from_env(),
                token_secret=token_secret,
                resume_token=request.resume_token,
                decision_payload=decision,
                resumed_by=request.resumed_by,
                observability_context=workflow_context,
            )
        finally:
            reset_observability_context(token_handle)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _log(
        "day5_resume_completed",
        request_id=raw_request.state.request_id,
        trace_id=workflow_context.trace_id,
        thread_id=resumed.thread_id,
        approval_task_id=approval_task_id,
    )
    return {
        "thread_id": resumed.thread_id,
        "thread_status": resumed.thread_status,
        "current_node": resumed.current_node,
        "approval_state": resumed.approval_state.model_dump(mode="json"),
        "review_task_state": resumed.review_task_state.model_dump(mode="json"),
        "review_outcome": resumed.review_outcome,
        "review_summary": resumed.review_summary,
        "payment_recommendation": resumed.payment_recommendation,
        "escalation_package": resumed.escalation_package,
        "side_effect_records": [record.model_dump(mode="json") for record in resumed.side_effect_records],
        "correlation": workflow_context.to_public_dict(),
    }
