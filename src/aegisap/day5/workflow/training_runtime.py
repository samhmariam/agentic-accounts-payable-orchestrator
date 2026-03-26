from __future__ import annotations

import uuid
from datetime import datetime, timezone

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


def _review_missing_requirements(review_payload: dict) -> list[str]:
    requirements: list[str] = []
    evidence_assessment = review_payload.get("evidence_assessment", {})
    for check in evidence_assessment.get("mandatory_checks", []):
        requirements.extend(check.get("missing_evidence", []))
    return list(dict.fromkeys(requirements))


class Day5TrainingGraphRunner:
    def __init__(self, store: DurableStateStore) -> None:
        self._effects = IdempotentEffectRunner(store)

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
            state.thread_status = "completed"
            state.current_node = "payment_ready"
            return state

        state.escalation_package = {
            **(state.escalation_package or {}),
            "case_id": state.case_id,
            "status": "controller_rejected",
            "controller_comment": comment,
        }
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
) -> dict:
    checkpoint_manager = CheckpointManager(store)
    _review_input, review_outcome = run_day6_review_from_day4(day4_state, thread_id=thread_id)
    review_payload = review_outcome.model_dump(mode="json")
    durable = bootstrap_durable_state_from_day4(
        day4_state,
        thread_id=thread_id,
        review_outcome=review_payload,
        review_summary=build_operator_summary(review_outcome),
    )

    if durable.thread_status not in {"awaiting_approval", "resumable", "quarantined"}:
        raise ValueError("Day 5 pause requires a Day 4 result that can be durably controlled.")

    checkpoint_id = str(uuid.uuid4())
    durable.resume_metadata.resumable_from_checkpoint_id = checkpoint_id

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
    }


def resume_day5_case(
    *,
    store: DurableStateStore,
    token_secret: str,
    resume_token: str,
    decision_payload: dict,
    resumed_by: str,
):
    checkpoint_manager = CheckpointManager(store)
    service = ResumeService(
        store=store,
        checkpoint_manager=checkpoint_manager,
        graph_runner=Day5TrainingGraphRunner(store),
        token_codec=ResumeTokenCodec(token_secret),
    )
    return service.resume_after_approval(
        resume_token=resume_token,
        decision_payload=decision_payload,
        resumed_by=resumed_by,
    )


def load_thread_snapshot(*, store: DurableStateStore, thread_id: str) -> dict:
    checkpoint_manager = CheckpointManager(store)
    loaded = checkpoint_manager.load_latest_checkpoint(thread_id)
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
        "side_effect_records": [record.model_dump(mode="json") for record in loaded.state.side_effect_records],
        "state": loaded.state.model_dump(mode="json"),
    }
