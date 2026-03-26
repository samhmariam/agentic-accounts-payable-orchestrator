from __future__ import annotations

from datetime import datetime, timezone

from aegisap.day4.execution.task_contracts import WorkerTaskInput, validate_task_result_against_contract
from aegisap.day4.execution.task_registry import TaskRegistry
from aegisap.day4.planning.plan_types import ExecutionPlan, PlanTask, TaskLedgerEntry, TaskResult
from aegisap.day4.state.workflow_state import WorkflowState


async def execute_plan(*, state: WorkflowState, plan: ExecutionPlan, registry: TaskRegistry) -> WorkflowState:
    pending = {task.task_id: task for task in plan.tasks}
    _initialise_ledger(state, plan)
    _refresh_eligibility_state(state, plan)

    if _escalation_is_mandatory(plan):
        state.planning.escalation_status = "triggered"
        state.eligibility.blocking_conditions.extend(
            [
                condition
                for condition in plan.global_stop_conditions
                if condition in {"missing_po_and_bank_change_require_manual_review", "combined_risk_requires_manual_review"}
            ]
        )
        manual_task = next((task for task in plan.tasks if task.task_type == "manual_escalation_package"), None)
        if manual_task is not None:
            await _execute_single_task(state=state, plan=plan, task=manual_task, registry=registry)
            pending.pop(manual_task.task_id, None)
        _mark_remaining_tasks(state, pending.values())
        state.planning.plan_status = "completed"
        _refresh_eligibility_state(state, plan)
        return state

    while pending:
        _refresh_eligibility_state(state, plan)
        ready_tasks = [task for task in pending.values() if _is_ready(task, state.task_ledger) and _preconditions_met(task, state)]

        if not ready_tasks:
            state.planning.plan_status = "blocked"
            if "no_ready_tasks_remaining" not in state.eligibility.blocking_conditions:
                state.eligibility.blocking_conditions.append("no_ready_tasks_remaining")
            _mark_remaining_tasks(state, pending.values())
            _refresh_eligibility_state(state, plan)
            return state

        manual_ready_task = next((task for task in ready_tasks if task.task_type == "manual_escalation_package"), None)
        task = manual_ready_task or ready_tasks[0]

        await _execute_single_task(state=state, plan=plan, task=task, registry=registry)
        pending.pop(task.task_id, None)
        _refresh_eligibility_state(state, plan)

        if state.planning.escalation_status == "triggered":
            manual_task = next((candidate for candidate in pending.values() if candidate.task_type == "manual_escalation_package"), None)
            if manual_task is not None and _is_ready(manual_task, state.task_ledger) and _preconditions_met(manual_task, state):
                continue
            _mark_remaining_tasks(state, pending.values())
            break

        if any(condition in state.eligibility.blocking_conditions for condition in plan.global_stop_conditions):
            _mark_remaining_tasks(state, pending.values())
            break

    state.planning.plan_status = "completed"
    _refresh_eligibility_state(state, plan)
    return state


def _initialise_ledger(state: WorkflowState, plan: ExecutionPlan) -> None:
    if state.task_ledger:
        return

    entries = [
        TaskLedgerEntry(
            task_id=task.task_id,
            task_type=task.task_type,
            owner_agent=task.owner_agent,
            status="pending",
            depends_on=task.depends_on,
        )
        for task in plan.tasks
    ]
    state.task_ledger.extend(entries)


def _is_ready(task: PlanTask, ledger: list[TaskLedgerEntry]) -> bool:
    completed_task_ids = {entry.task_id for entry in ledger if entry.status == "completed"}
    return all(dep in completed_task_ids for dep in task.depends_on)


def _preconditions_met(task: PlanTask, state: WorkflowState) -> bool:
    return all(_precondition_satisfied(precondition, state) for precondition in task.preconditions)


async def _execute_single_task(
    *,
    state: WorkflowState,
    plan: ExecutionPlan,
    task: PlanTask,
    registry: TaskRegistry,
) -> None:
    _mark_running(state.task_ledger, task.task_id)
    state.planning.active_task_ids = [task.task_id]
    state.planning.plan_status = "executing"

    executor = registry.get(task.task_type)
    result = await executor.execute(
        WorkerTaskInput(
            task_id=task.task_id,
            case_id=state.case_facts.case_id,
            workflow_state=state,
            task_inputs=task.inputs,
            required_evidence=task.required_evidence,
            expected_outputs=task.expected_outputs,
        )
    )
    result = _normalise_result_for_contract(task, result)
    _apply_task_result(state, task, result)
    state.planning.active_task_ids = []
    _refresh_eligibility_state(state, plan)


def _normalise_result_for_contract(task: PlanTask, result: TaskResult) -> TaskResult:
    errors = validate_task_result_against_contract(task.task_type, result)
    if not errors and result.confidence >= task.min_confidence:
        return result

    blocking_reason = "task_contract_violation" if errors else "confidence_threshold_not_met"
    status = "escalated" if task.on_failure == "escalate" else "blocked"
    return TaskResult(
        task_id=result.task_id,
        status=status,
        confidence=result.confidence,
        outputs={**result.outputs},
        blocking_reason=blocking_reason,
        evidence_refs=result.evidence_refs,
    )


def _mark_running(ledger: list[TaskLedgerEntry], task_id: str) -> None:
    entry = next((item for item in ledger if item.task_id == task_id), None)
    if entry is None:
        return

    entry.status = "running"
    entry.started_at = _now_iso()


def _apply_task_result(state: WorkflowState, task: PlanTask, result: TaskResult) -> None:
    entry = next((item for item in state.task_ledger if item.task_id == task.task_id), None)
    if entry is None:
        raise ValueError(f"missing_ledger_entry_for_task:{task.task_id}")

    entry.status = result.status
    entry.completed_at = _now_iso()
    entry.confidence = result.confidence
    entry.outputs = result.outputs
    entry.blocking_reason = result.blocking_reason
    entry.result_ref = f"artifact:{task.task_id}"
    state.artifacts[task.task_id] = {
        "outputs": result.outputs,
        "evidence_refs": [ref.model_dump() for ref in result.evidence_refs or []],
    }

    if result.status == "completed" and task.task_id not in state.planning.completed_task_ids:
        state.planning.completed_task_ids.append(task.task_id)

    if result.status in {"blocked", "failed"} and task.task_id not in state.planning.blocked_task_ids:
        state.planning.blocked_task_ids.append(task.task_id)
        if result.blocking_reason:
            state.eligibility.blocking_conditions.append(result.blocking_reason)

    if result.status == "escalated":
        state.planning.escalation_status = "triggered"
        if task.task_id not in state.planning.blocked_task_ids:
            state.planning.blocked_task_ids.append(task.task_id)
        if result.blocking_reason:
            state.eligibility.blocking_conditions.append(result.blocking_reason)

    if task.task_type == "manual_escalation_package":
        state.planning.escalation_status = "triggered"

    if task.stop_if_missing and result.blocking_reason:
        for evidence_name in task.required_evidence or ["required_evidence"]:
            if evidence_name not in state.eligibility.missing_evidence:
                state.eligibility.missing_evidence.append(evidence_name)


def _refresh_eligibility_state(state: WorkflowState, plan: ExecutionPlan) -> None:
    unmet_preconditions = [
        precondition
        for precondition in plan.global_preconditions
        if not _precondition_satisfied(precondition, state)
    ]
    state.eligibility.unmet_preconditions = unmet_preconditions

    approval_entry = _entry_for_task_type(state, "threshold_approval_check")
    derived_approvals = plan.required_approvals[:]
    if approval_entry and approval_entry.outputs:
        derived_approvals.extend(approval_entry.outputs.get("required_approvals", []))
    state.eligibility.required_approvals = list(dict.fromkeys(derived_approvals))
    state.eligibility.blocking_conditions = list(dict.fromkeys(state.eligibility.blocking_conditions))
    state.eligibility.missing_evidence = list(dict.fromkeys(state.eligibility.missing_evidence))
    state.eligibility.irreversible_actions_allowed = False


def _precondition_satisfied(precondition: str, state: WorkflowState) -> bool:
    if precondition == "po_verified_or_waived":
        po_entry = _entry_for_task_type(state, "po_match_verification")
        waiver_entry = _entry_for_task_type(state, "po_waiver_check")
        po_passed = bool(po_entry and po_entry.outputs and po_entry.outputs.get("po_match_status") == "pass")
        waiver_present = bool(waiver_entry and waiver_entry.outputs and waiver_entry.outputs.get("waiver_present"))
        return po_passed or waiver_present

    if precondition == "bank_change_authoritatively_verified":
        if not state.case_facts.bank_details_changed:
            return True
        bank_entry = _entry_for_task_type(state, "vendor_bank_verification")
        return bool(bank_entry and bank_entry.outputs and bank_entry.outputs.get("bank_change_verified") is True)

    if precondition == "approval_route_defined_for_threshold_case":
        if not state.eligibility.required_approvals and state.case_facts.invoice_amount_gbp < (
            state.case_facts.amount_approval_threshold_gbp or 25_000
        ):
            return True
        approval_entry = _entry_for_task_type(state, "threshold_approval_check")
        return bool(approval_entry and approval_entry.outputs and approval_entry.outputs.get("approval_path_defined"))

    return True


def _entry_for_task_type(state: WorkflowState, task_type: str) -> TaskLedgerEntry | None:
    return next((item for item in state.task_ledger if item.task_type == task_type), None)


def _escalation_is_mandatory(plan: ExecutionPlan) -> bool:
    forced_stop_conditions = {
        "missing_po_and_bank_change_require_manual_review",
        "combined_risk_requires_manual_review",
    }
    return any(condition in forced_stop_conditions for condition in plan.global_stop_conditions)


def _mark_remaining_tasks(state: WorkflowState, tasks: list[PlanTask] | object) -> None:
    for task in tasks:
        entry = next((item for item in state.task_ledger if item.task_id == task.task_id), None)
        if entry is not None and entry.status == "pending":
            entry.status = "skipped"


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
