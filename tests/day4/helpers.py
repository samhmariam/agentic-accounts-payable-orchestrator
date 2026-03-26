from __future__ import annotations

import json
from pathlib import Path

from aegisap.common.paths import repo_root
from aegisap.day4.execution.task_contracts import get_task_contract
from aegisap.day4.planning.plan_types import (
    ActionClassification,
    CaseFacts,
    ExecutionPlan,
    PlanTask,
    RecommendationGate,
)
from aegisap.day4.planning.policy_overlay import derive_policy_overlay


def day4_fixture_path(name: str) -> Path:
    return repo_root(__file__) / "fixtures" / "day4" / f"{name}.json"


def load_day4_fixture(name: str) -> dict:
    return json.loads(day4_fixture_path(name).read_text(encoding="utf-8"))


def load_case_facts(name: str) -> CaseFacts:
    fixture = load_day4_fixture(name)
    return CaseFacts.model_validate(fixture["case_facts"])


def build_safe_plan(case_facts: CaseFacts, *, plan_id: str = "plan_day4") -> ExecutionPlan:
    overlay = derive_policy_overlay(case_facts)
    tasks: list[PlanTask] = []
    completed_dependencies: list[str] = []

    for task_type in overlay.mandatory_task_types:
        contract = get_task_contract(task_type)
        task_id = task_type

        depends_on: list[str]
        if task_type == "policy_retrieval":
            depends_on = []
        elif task_type == "manual_escalation_package":
            depends_on = []
        elif task_type == "payment_recommendation_draft":
            depends_on = [task.task_id for task in tasks if task.task_type != "manual_escalation_package"]
        else:
            depends_on = ["policy_retrieval"] if "policy_retrieval" in completed_dependencies else []

        tasks.append(
            PlanTask(
                task_id=task_id,
                task_type=task_type,
                owner_agent=contract.owner_agent,
                depends_on=depends_on,
                inputs={"case_id": case_facts.case_id, "invoice_id": case_facts.invoice_id},
                required_evidence=_required_evidence(task_type),
                expected_outputs=contract.expected_output_fields,
                preconditions=[],
                stop_if_missing=task_type in {
                    "po_match_verification",
                    "po_waiver_check",
                    "vendor_bank_verification",
                },
                min_confidence=0.9 if task_type in {"po_match_verification", "vendor_bank_verification"} else 0.8,
                on_failure="escalate" if task_type in {"vendor_bank_verification", "manual_escalation_package"} else "block",
                action_class="reversible",
            )
        )
        completed_dependencies.append(task_id)

    return ExecutionPlan(
        plan_id=plan_id,
        case_id=case_facts.case_id,
        goal="Determine whether payment recommendation is eligible",
        case_risk_flags=overlay.risk_flags,
        planning_rationale="Deterministic test plan aligned to the policy overlay.",
        tasks=tasks,
        global_preconditions=overlay.global_preconditions,
        global_stop_conditions=overlay.global_stop_conditions,
        escalation_triggers=overlay.escalation_triggers,
        escalation_route=overlay.escalation_route,
        escalation_reason_template=overlay.escalation_reason_template,
        required_approvals=overlay.required_approvals,
        recommendation_gate=RecommendationGate(
            all_mandatory_tasks_completed=True,
            required_evidence_present=True,
            no_unresolved_blockers=True,
            confidence_thresholds_met=True,
            required_approvals_identified=True,
            mandatory_escalations_resolved_or_triggered=True,
            po_condition_satisfied=True,
            bank_change_verification_satisfied=True,
            approval_path_satisfied=True,
        ),
        action_classification=ActionClassification(
            current_stage="reversible",
            irreversible_actions_allowed=False,
        ),
    )


def _required_evidence(task_type: str) -> list[str]:
    mapping = {
        "policy_retrieval": ["policy:controls"],
        "po_match_verification": ["po_number"],
        "po_waiver_check": ["po_waiver"],
        "vendor_history_check": ["supplier_master_record"],
        "vendor_bank_verification": ["supplier_master_record", "bank_change_request_evidence"],
        "threshold_approval_check": ["policy:approval-thresholds"],
        "manual_escalation_package": ["case_summary"],
        "payment_recommendation_draft": [],
    }
    return mapping[task_type]
