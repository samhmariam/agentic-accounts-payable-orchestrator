from __future__ import annotations

import uuid
from datetime import datetime, timezone

from aegisap.audit.events import buffered_audit_events, build_audit_event
from aegisap.audit.writer import AuditWriter
from aegisap.day4.state.workflow_state import WorkflowState as Day4WorkflowState
from aegisap.day6.audit.decision_log import build_operator_summary
from aegisap.day6.graph.review_gate import run_day6_review_from_day4
from aegisap.day5.persistence.durable_state_store import DurableStateStore
from aegisap.day5.state.durable_models import HistoryMessage, ReviewTaskState, SideEffectRecord
from aegisap.day5.workflow.checkpoint_manager import CheckpointManager
from aegisap.day5.workflow.day4_handoff import bootstrap_durable_state_from_day4
from aegisap.day5.workflow.resume_service import ResumeService, ResumeTokenCodec
from aegisap.day5.workflow.side_effects import (
    IdempotentEffectRunner,
    build_audit_entry_effect_key,
    build_payment_recommendation_effect_key,
)
from aegisap.observability.context import WorkflowObservabilityContext
from aegisap.observability.langsmith_bridge import publish_langsmith_run
from aegisap.observability.metrics import record_business_event, record_resume_delay, record_workflow_run
from aegisap.observability.tracing import (
    add_span_event,
    business_outcome_attributes,
    node_span_attributes,
    set_span_attributes,
    start_observability_span,
)
from aegisap.security.config import load_security_config


def _review_missing_requirements(review_payload: dict) -> list[str]:
    requirements: list[str] = []
    evidence_assessment = review_payload.get("evidence_assessment", {})
    for check in evidence_assessment.get("mandatory_checks", []):
        requirements.extend(check.get("missing_evidence", []))
    return list(dict.fromkeys(requirements))


def _runtime_actor() -> tuple[str, str]:
    config = load_security_config()
    if config.credential_mode == "managed_identity":
        return "managed_identity", "runtime-api"
    return "system_job", "entra_developer_identity"


class Day5TrainingGraphRunner:
    def __init__(self, store: DurableStateStore) -> None:
        self._effects = IdempotentEffectRunner(store)
        self._audit = AuditWriter(store=store)

    def resume(self, *, state, approval_decision: dict):
        now = datetime.now(timezone.utc)
        comment = approval_decision.get("comment") or "No controller comment supplied."
        state.history_state.raw_messages.append(
            HistoryMessage(
                role="reviewer",
                content=f"Finance Controller decision: {approval_decision['status']}. {comment}",
                created_at=now,
                metadata={"approval_state": approval_decision["status"]},
            )
        )

        resumable_from = state.resume_metadata.resumable_from_checkpoint_id or f"checkpoint-{state.checkpoint_seq}"
        audit_payload = {
            "thread_id": state.thread_id,
            "decision": approval_decision["status"],
            "comment": comment,
        }
        actor_type, actor_id = _runtime_actor()
        audit_result = self._effects.run(
            effect_key=build_audit_entry_effect_key(
                thread_id=state.thread_id,
                checkpoint_seq=state.checkpoint_seq,
                audit_kind="approval_decision",
            ),
            thread_id=state.thread_id,
            checkpoint_id=resumable_from,
            effect_type="audit_entry",
            payload=audit_payload,
            apply_fn=lambda payload: {
                "audit_id": f"audit-{state.thread_id}-{state.checkpoint_seq}",
                "recorded_at": now.isoformat(),
                "payload": payload,
            },
        )
        state.side_effect_records.append(
            SideEffectRecord(
                effect_key=build_audit_entry_effect_key(
                    thread_id=state.thread_id,
                    checkpoint_seq=state.checkpoint_seq,
                    audit_kind="approval_decision",
                ),
                effect_type="audit_entry",
                status="deduplicated" if audit_result["deduplicated"] else "applied",
                created_at=now,
                result_ref=audit_result["result"]["audit_id"],
            )
        )

        if approval_decision["status"] == "approved" and state.payment_recommendation is not None:
            recommendation_result = self._effects.run(
                effect_key=build_payment_recommendation_effect_key(
                    thread_id=state.thread_id,
                    plan_version=state.plan_version,
                ),
                thread_id=state.thread_id,
                checkpoint_id=resumable_from,
                effect_type="payment_recommendation",
                payload=state.payment_recommendation,
                apply_fn=lambda payload: {
                    "recommendation_id": f"rec-{state.thread_id}",
                    "recorded_at": now.isoformat(),
                    "payload": payload,
                },
            )
            state.side_effect_records.append(
                SideEffectRecord(
                    effect_key=build_payment_recommendation_effect_key(
                        thread_id=state.thread_id,
                        plan_version=state.plan_version,
                    ),
                    effect_type="payment_recommendation",
                    status="deduplicated" if recommendation_result["deduplicated"] else "applied",
                    created_at=now,
                    result_ref=recommendation_result["result"]["recommendation_id"],
                )
            )
            state.payment_recommendation = {
                **state.payment_recommendation,
                "delivery": recommendation_result["result"],
            }
            self._audit.write(
                build_audit_event(
                    workflow_run_id=state.workflow_run_id,
                    thread_id=state.thread_id,
                    state_version=state.checkpoint_seq,
                    actor_type=actor_type,
                    actor_id=actor_id,
                    action_type="human_approval",
                    decision_outcome="approved",
                    approval_status="approved",
                    evidence_summary=(
                        f"Human approval recorded for thread {state.thread_id}. "
                        f"Comment: {comment}"
                    ),
                    evidence_refs=[state.approval_state.approval_task_id or "approval_task"],
                    policy_version=(state.review_outcome or {}).get("model_trace", {}).get("policy_version"),
                    planner_version=state.plan_version,
                    trace_id=approval_decision.get("trace_id"),
                    metadata={
                        "workflow_run_id": state.workflow_run_id,
                        "checkpoint_id": state.resume_metadata.resumable_from_checkpoint_id,
                    },
                )
            )
            self._audit.write(
                build_audit_event(
                    workflow_run_id=state.workflow_run_id,
                    thread_id=state.thread_id,
                    state_version=state.checkpoint_seq,
                    actor_type=actor_type,
                    actor_id=actor_id,
                    action_type="resume",
                    decision_outcome="completed",
                    approval_status="approved",
                    evidence_summary=f"Thread {state.thread_id} resumed and completed after approval.",
                    evidence_refs=[state.current_node],
                    policy_version=(state.review_outcome or {}).get("model_trace", {}).get("policy_version"),
                    planner_version=state.plan_version,
                    trace_id=approval_decision.get("trace_id"),
                    metadata={
                        "workflow_run_id": state.workflow_run_id,
                        "checkpoint_id": state.resume_metadata.resumable_from_checkpoint_id,
                    },
                )
            )
            state.thread_status = "completed"
            state.current_node = "payment_ready"
            return state

        state.escalation_package = {
            **(state.escalation_package or {}),
            "case_id": state.case_id,
            "status": "controller_rejected",
            "controller_comment": comment,
        }
        self._audit.write(
            build_audit_event(
                workflow_run_id=state.workflow_run_id,
                thread_id=state.thread_id,
                state_version=state.checkpoint_seq,
                actor_type=actor_type,
                actor_id=actor_id,
                action_type="human_approval",
                decision_outcome="rejected",
                approval_status=approval_decision["status"],
                evidence_summary=(
                    f"Human approval decision {approval_decision['status']} recorded for thread {state.thread_id}. "
                    f"Comment: {comment}"
                ),
                evidence_refs=[state.approval_state.approval_task_id or "approval_task"],
                policy_version=(state.review_outcome or {}).get("model_trace", {}).get("policy_version"),
                planner_version=state.plan_version,
                trace_id=approval_decision.get("trace_id"),
                metadata={
                    "workflow_run_id": state.workflow_run_id,
                    "checkpoint_id": state.resume_metadata.resumable_from_checkpoint_id,
                },
            )
        )
        self._audit.write(
            build_audit_event(
                workflow_run_id=state.workflow_run_id,
                thread_id=state.thread_id,
                state_version=state.checkpoint_seq,
                actor_type=actor_type,
                actor_id=actor_id,
                action_type="resume",
                decision_outcome="completed",
                approval_status=approval_decision["status"],
                evidence_summary=f"Thread {state.thread_id} resumed to manual review after controller rejection.",
                evidence_refs=[state.current_node],
                policy_version=(state.review_outcome or {}).get("model_trace", {}).get("policy_version"),
                planner_version=state.plan_version,
                trace_id=approval_decision.get("trace_id"),
                metadata={
                    "workflow_run_id": state.workflow_run_id,
                    "checkpoint_id": state.resume_metadata.resumable_from_checkpoint_id,
                },
            )
        )
        state.thread_status = "resumable"
        state.current_node = "manual_review_required"
        return state


def create_day5_pause(
    *,
    day4_state: Day4WorkflowState,
    thread_id: str,
    assigned_to: str,
    store: DurableStateStore,
    token_secret: str,
    observability_context: WorkflowObservabilityContext | None = None,
    trace_id: str | None = None,
) -> dict:
    checkpoint_manager = CheckpointManager(store)
    if observability_context is None and trace_id is not None:
        restored = WorkflowObservabilityContext.from_state_payload(
            day4_state.observability,
            workflow_run_id=day4_state.workflow_run_id,
            case_id=day4_state.case_facts.case_id,
            thread_id=thread_id,
        )
        observability_context = restored or WorkflowObservabilityContext(
            request_id="day5-pause",
            workflow_run_id=day4_state.workflow_run_id,
            trace_id=trace_id,
            case_id=day4_state.case_facts.case_id,
            thread_id=thread_id,
            environment=load_security_config().environment,
            deployment_revision=load_security_config().deployment_revision,
        )
        observability_context.trace_id = trace_id
        observability_context.azure_trace_id = trace_id
    with start_observability_span(
        "aegis.workflow.day5.persist_state",
        attributes=node_span_attributes(
            node_name="day5_persist_state",
            idempotent=False,
            checkpoint_saved=True,
        ),
    ):
        _review_input, review_outcome = run_day6_review_from_day4(
            day4_state,
            thread_id=thread_id,
            observability_context=observability_context,
        )
        review_payload = review_outcome.model_dump(mode="json")
        durable = bootstrap_durable_state_from_day4(
            day4_state,
            thread_id=thread_id,
            review_outcome=review_payload,
            review_summary=build_operator_summary(review_outcome),
        )
        if observability_context is not None:
            observability_context.thread_id = thread_id
            observability_context.checkpoint_id = durable.resume_metadata.resumable_from_checkpoint_id
            observability_context.plan_version = durable.plan_version
            observability_context.policy_version = review_payload.get("model_trace", {}).get("policy_version")
            observability_context.outcome_type = review_payload["outcome"]
            observability_context.approval_status = durable.approval_state.status
            durable.observability = observability_context.to_state_payload()

    if durable.thread_status not in {"awaiting_approval", "resumable", "quarantined"}:
        raise ValueError("Day 5 pause requires a Day 4 result that can be durably controlled.")

    checkpoint_id = str(uuid.uuid4())
    durable.resume_metadata.resumable_from_checkpoint_id = checkpoint_id
    if observability_context is not None:
        observability_context.checkpoint_id = checkpoint_id
        observability_context.state_version = durable.checkpoint_seq + 1
        durable.observability = observability_context.to_state_payload()

    approval_task_id: str | None = None
    review_task_id: str | None = None
    if durable.thread_status == "awaiting_approval":
        approval_task_id = str(uuid.uuid4())
        durable.approval_state.approval_task_id = approval_task_id
        durable.approval_state.assigned_to = assigned_to
    elif durable.thread_status == "resumable":
        review_task_id = str(uuid.uuid4())
        durable.review_task_state = ReviewTaskState(
            status="pending",
            review_task_id=review_task_id,
            assigned_to=assigned_to,
            requested_at=datetime.now(timezone.utc),
            missing_requirements=_review_missing_requirements(review_payload),
        )

    with store.connection() as conn:
        checkpoint_manager.save_checkpoint(
            state=durable,
            node_name=durable.current_node,
            is_interrupt_checkpoint=True,
            checkpoint_id=checkpoint_id,
            conn=conn,
        )
        if approval_task_id is not None:
            store.create_approval_task(
                thread_id=thread_id,
                checkpoint_id=checkpoint_id,
                assigned_to=assigned_to,
                approval_task_id=approval_task_id,
                conn=conn,
            )
        if review_task_id is not None:
            store.create_review_task(
                thread_id=thread_id,
                checkpoint_id=checkpoint_id,
                assigned_to=assigned_to,
                review_task_id=review_task_id,
                conn=conn,
            )
        conn.commit()

    actor_type, actor_id = _runtime_actor()
    buffered_events = [
        event.model_copy(
            update={
                "thread_id": thread_id,
                "state_version": durable.checkpoint_seq,
                "trace_id": observability_context.trace_id if observability_context else durable.observability.get("trace_id"),
                "workflow_run_id": durable.workflow_run_id,
                "metadata": {
                    **event.metadata,
                    "workflow_run_id": durable.workflow_run_id,
                    "checkpoint_id": checkpoint_id,
                },
            }
        )
        for event in buffered_audit_events(day4_state.artifacts)
    ]
    AuditWriter(store=store).write_many(
        buffered_events
        + [
            build_audit_event(
                workflow_run_id=durable.workflow_run_id,
                thread_id=thread_id,
                state_version=durable.checkpoint_seq,
                actor_type=actor_type,
                actor_id=actor_id,
                action_type=(
                    "payment_recommendation"
                    if review_payload["outcome"] == "approved_to_proceed"
                    else "refusal"
                ),
                decision_outcome=review_payload["outcome"],
                approval_status=durable.approval_state.status,
                evidence_summary=review_payload["decision_summary"],
                evidence_refs=[citation["evidence_id"] for citation in review_payload["citations"]],
                policy_version=review_payload.get("model_trace", {}).get("policy_version"),
                planner_version=durable.plan_version,
                error_code=(review_payload["reasons"][0]["code"] if review_payload["reasons"] else None),
                trace_id=observability_context.trace_id if observability_context else durable.observability.get("trace_id"),
                metadata={
                    "review_stage": review_payload["review_stage"],
                    "workflow_run_id": durable.workflow_run_id,
                    "checkpoint_id": checkpoint_id,
                },
            )
        ]
    )
    record_workflow_run(
        environment=load_security_config().environment,
        outcome=review_payload["outcome"],
        workflow_name=durable.workflow_name,
    )
    record_business_event(
        "workflow_pause_created",
        workflow_run_id=durable.workflow_run_id,
        approval_status=durable.approval_state.status,
    )
    set_span_attributes(
        business_outcome_attributes(
            recommendation_value_band="high" if day4_state.case_facts.invoice_amount_gbp >= 25_000 else "standard",
            final_decision_type=review_payload["outcome"],
            human_review_required=review_payload["outcome"] != "approved_to_proceed",
        )
    )

    resume_token: str | None = None
    if approval_task_id is not None:
        token_codec = ResumeTokenCodec(token_secret)
        resume_service = ResumeService(
            store=store,
            checkpoint_manager=checkpoint_manager,
            graph_runner=Day5TrainingGraphRunner(store),
            token_codec=token_codec,
        )
        resume_token = resume_service.create_resume_token(
            thread_id=thread_id,
            checkpoint_id=checkpoint_id,
            checkpoint_seq=durable.checkpoint_seq,
            approval_task_id=approval_task_id,
        )

    return {
        "thread_id": thread_id,
        "checkpoint_id": checkpoint_id,
        "checkpoint_seq": durable.checkpoint_seq,
        "approval_task_id": approval_task_id,
        "review_task_id": review_task_id,
        "assigned_to": assigned_to,
        "resume_token": resume_token,
        "review_outcome": review_payload,
        "review_summary": durable.review_summary,
        "state": durable.model_dump(mode="json"),
        "correlation": (
            observability_context.to_public_dict()
            if observability_context is not None
            else {
                "workflow_run_id": durable.workflow_run_id,
                "trace_id": durable.observability.get("trace_id"),
                "checkpoint_id": checkpoint_id,
                "langsmith_trace_id": durable.observability.get("langsmith_trace_id"),
            }
        ),
    }


def resume_day5_case(
    *,
    store: DurableStateStore,
    token_secret: str,
    resume_token: str,
    decision_payload: dict,
    resumed_by: str,
    observability_context: WorkflowObservabilityContext | None = None,
    trace_id: str | None = None,
):
    decision = {**decision_payload}
    if observability_context is not None and observability_context.trace_id is not None:
        decision["trace_id"] = observability_context.trace_id
    elif trace_id is not None:
        decision["trace_id"] = trace_id
    checkpoint_manager = CheckpointManager(store)
    service = ResumeService(
        store=store,
        checkpoint_manager=checkpoint_manager,
        graph_runner=Day5TrainingGraphRunner(store),
        token_codec=ResumeTokenCodec(token_secret),
    )
    resumed = service.resume_after_approval(
        resume_token=resume_token,
        decision_payload=decision,
        resumed_by=resumed_by,
    )
    if observability_context is not None:
        observability_context.workflow_run_id = resumed.workflow_run_id
        observability_context.thread_id = resumed.thread_id
        observability_context.checkpoint_id = resumed.resume_metadata.resumable_from_checkpoint_id
        observability_context.plan_version = resumed.plan_version
        observability_context.policy_version = (resumed.review_outcome or {}).get("model_trace", {}).get("policy_version")
        observability_context.approval_status = resumed.approval_state.status
        observability_context.outcome_type = (
            "completed" if resumed.thread_status == "completed" else resumed.thread_status
        )
        publish_langsmith_run(
            context=observability_context,
            name="aegis.workflow.day5.resume",
            run_type="chain",
            inputs={"approval_status": decision.get("status")},
            outputs={"thread_status": resumed.thread_status, "current_node": resumed.current_node},
            tags=["day5", "resume"],
        )
        if resumed.approval_state.requested_at is not None and resumed.approval_state.resolved_at is not None:
            duration_ms = int(
                (resumed.approval_state.resolved_at - resumed.approval_state.requested_at).total_seconds()
                * 1000
            )
            record_resume_delay(duration_ms, workflow_run_id=resumed.workflow_run_id)
    return resumed


def load_thread_snapshot(
    *,
    store: DurableStateStore,
    thread_id: str,
    observability_context: WorkflowObservabilityContext | None = None,
) -> dict:
    checkpoint_manager = CheckpointManager(store)
    loaded = checkpoint_manager.load_latest_checkpoint(thread_id)
    audit_events = store.list_audit_events(thread_id=thread_id, limit=20)
    if observability_context is not None:
        observability_context.workflow_run_id = loaded.state.workflow_run_id
        observability_context.thread_id = loaded.state.thread_id
        observability_context.checkpoint_id = loaded.checkpoint_id
    return {
        "thread_id": thread_id,
        "checkpoint_id": loaded.checkpoint_id,
        "current_node": loaded.state.current_node,
        "thread_status": loaded.state.thread_status,
        "approval_state": loaded.state.approval_state.model_dump(mode="json"),
        "review_task_state": loaded.state.review_task_state.model_dump(mode="json"),
        "review_outcome": loaded.state.review_outcome,
        "review_summary": loaded.state.review_summary,
        "payment_recommendation": loaded.state.payment_recommendation,
        "escalation_package": loaded.state.escalation_package,
        "audit_events": [item.payload_json for item in audit_events],
        "side_effect_records": [record.model_dump(mode="json") for record in loaded.state.side_effect_records],
        "state": loaded.state.model_dump(mode="json"),
        "correlation": (
            observability_context.to_public_dict()
            if observability_context is not None
            else {
                "workflow_run_id": loaded.state.workflow_run_id,
                "trace_id": loaded.state.observability.get("trace_id"),
                "checkpoint_id": loaded.checkpoint_id,
                "langsmith_trace_id": loaded.state.observability.get("langsmith_trace_id"),
            }
        ),
    }
