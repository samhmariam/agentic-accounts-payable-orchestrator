from __future__ import annotations

import json
import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request

from aegisap.api.models import Day1IntakeRequest, Day4RunRequest, Day5ResumeRequest
from aegisap.day_01.service import canonicalize_with_candidate, run_day_01_intake
from aegisap.day5.workflow.resume_service import ResumeTokenCodec
from aegisap.day5.workflow.training_runtime import create_day5_pause, load_thread_snapshot, resume_day5_case
from aegisap.training.postgres import build_store_from_env
from aegisap.training.labs import run_day4_case_artifact

logger = logging.getLogger("aegisap.api")


def _configure_observability() -> None:
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "").strip()
    if not connection_string:
        return
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(connection_string=connection_string)
    except Exception as exc:  # pragma: no cover - defensive startup guard
        logger.warning("azure_monitor_configuration_failed: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _configure_observability()
    yield


app = FastAPI(title="AegisAP Training Runtime", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def add_request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response


def _log(event: str, **fields: object) -> None:
    logger.info("%s %s", event, json.dumps(fields, sort_keys=True, default=str))


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
    }


@app.post("/api/day4/cases/run")
async def day4_run_case(request: Day4RunRequest, raw_request: Request) -> dict[str, object]:
    artifact_path, artifact_payload, state = await run_day4_case_artifact(
        case_facts=request.case_facts,
        planner_mode=request.planner_mode,
        artifact_name=f"{request.case_facts.case_id}_api",
        include_day6_review=request.enable_day6_review,
        thread_id=request.thread_id or f"thread-{request.case_facts.case_id}",
    )
    response: dict[str, object] = {
        "artifact_path": str(artifact_path),
        "planner_mode": request.planner_mode,
        "validated_plan": artifact_payload["validated_plan"],
        "recommendation": state.recommendation,
        "escalation_package": state.escalation_package,
        "day6_review": artifact_payload["day6_review"],
    }

    if request.persist_day5_handoff:
        token_secret = os.getenv("AEGISAP_RESUME_TOKEN_SECRET", "dev-only-resume-secret")
        thread_id = request.thread_id or f"thread-{request.case_facts.case_id}"
        assigned_to = request.assigned_to or "controller@example.com"
        try:
            pause_payload = create_day5_pause(
                day4_state=state,
                thread_id=thread_id,
                assigned_to=assigned_to,
                store=build_store_from_env(),
                token_secret=token_secret,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        response["day5_handoff"] = pause_payload
        _log(
            "day5_pause_created",
            request_id=raw_request.state.request_id,
            thread_id=thread_id,
            approval_task_id=pause_payload["approval_task_id"],
        )

    _log(
        "day4_case_completed",
        request_id=raw_request.state.request_id,
        case_id=request.case_facts.case_id,
        recommendation_ready=state.recommendation is not None,
        day6_outcome=(artifact_payload["day6_review"] or {}).get("outcome"),
    )
    return response


@app.get("/api/day5/threads/{thread_id}")
async def day5_thread(thread_id: str, raw_request: Request) -> dict[str, object]:
    try:
        snapshot = load_thread_snapshot(store=build_store_from_env(), thread_id=thread_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    _log("day5_thread_loaded", request_id=raw_request.state.request_id, thread_id=thread_id)
    return snapshot


@app.post("/api/day5/approvals/{approval_task_id}/resume")
async def day5_resume(
    approval_task_id: str,
    request: Day5ResumeRequest,
    raw_request: Request,
) -> dict[str, object]:
    token_secret = os.getenv("AEGISAP_RESUME_TOKEN_SECRET", "dev-only-resume-secret")
    token = ResumeTokenCodec(token_secret).decode(request.resume_token)
    if token.approval_task_id != approval_task_id:
        raise HTTPException(status_code=400, detail="approval_task_id does not match resume token")

    decision = {
        "status": request.decision.get("status", "approved"),
        "comment": request.decision.get("comment", ""),
        "approved_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        resumed = resume_day5_case(
            store=build_store_from_env(),
            token_secret=token_secret,
            resume_token=request.resume_token,
            decision_payload=decision,
            resumed_by=request.resumed_by,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _log(
        "day5_resume_completed",
        request_id=raw_request.state.request_id,
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
    }
