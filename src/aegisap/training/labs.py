from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from aegisap.day_01.models import CanonicalInvoice, ExtractedInvoiceCandidate, InvoicePackageInput
from aegisap.day_01.service import canonicalize_with_candidate, run_day_01_intake
from aegisap.day2.config import HIGH_VALUE_THRESHOLD, KNOWN_VENDORS, ROUTE_PRECEDENCE
from aegisap.day2.graph import build_graph
from aegisap.day2.state import WorkflowState as Day2WorkflowState
from aegisap.day2.state import make_initial_state
from aegisap.day3.graph import run_day3_workflow
from aegisap.day3.retrieval.interfaces import RetrievalConfig, build_retrieval_config
from aegisap.day4.execution.task_registry import create_default_task_registry
from aegisap.day4.graph.day4_explicit_planning_graph import run_day4_explicit_planning_case
from aegisap.day4.planning.azure_openai_planner import AzureOpenAIPlannerClient
from aegisap.day4.planning.plan_schema import parse_execution_plan
from aegisap.day4.planning.plan_types import CaseFacts, ExecutionPlan
from aegisap.day4.planning.plan_validator import validate_execution_plan
from aegisap.day4.planning.planner_agent import ModelClient, coerce_json
from aegisap.day4.planning.planner_prompt import build_planner_prompt
from aegisap.day4.planning.policy_overlay import derive_policy_overlay
from aegisap.day4.recommendation.escalation_composer import compose_escalation_package
from aegisap.day4.recommendation.recommendation_composer import compose_recommendation
from aegisap.day4.recommendation.recommendation_gate import evaluate_recommendation_gate
from aegisap.day4.state.workflow_state import WorkflowState as Day4WorkflowState
from aegisap.day4.state.workflow_state import create_initial_workflow_state
from aegisap.training.artifacts import build_root, load_json, write_json_artifact
from aegisap.training.day4_plans import build_training_plan


def _serialize(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "as_dict"):
        return value.as_dict()
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    return value


def load_invoice_package(path: str | Path) -> InvoicePackageInput:
    return InvoicePackageInput.model_validate(load_json(path))


def load_candidate(path: str | Path) -> ExtractedInvoiceCandidate:
    return ExtractedInvoiceCandidate.model_validate(load_json(path))


def load_case_facts(path: str | Path) -> CaseFacts:
    payload = load_json(path)
    if "case_facts" in payload:
        payload = payload["case_facts"]
    return CaseFacts.model_validate(payload)


def _write_day_artifact(day: str, name: str, payload: dict[str, Any]) -> Path:
    artifact_dir = build_root(day)
    return write_json_artifact(artifact_dir / f"{name}.json", payload)


def run_day1_fixture(
    *,
    package_path: str | Path,
    candidate_path: str | Path,
    artifact_name: str = "golden_thread_day1",
) -> tuple[Path, dict[str, Any]]:
    package = load_invoice_package(package_path)
    candidate = load_candidate(candidate_path)
    canonical = canonicalize_with_candidate(package, candidate)
    payload = _day1_payload(
        package=package,
        canonical=canonical,
        mode="fixture",
        package_source=str(package_path),
        candidate_source=str(candidate_path),
    )
    return _write_day_artifact("day1", artifact_name, payload), payload


def run_day1_live(
    *,
    package_path: str | Path,
    artifact_name: str = "golden_thread_day1_live",
) -> tuple[Path, dict[str, Any]]:
    package = load_invoice_package(package_path)
    canonical = run_day_01_intake(package)
    payload = _day1_payload(
        package=package,
        canonical=canonical,
        mode="live_azure_openai",
        package_source=str(package_path),
        candidate_source=None,
    )
    return _write_day_artifact("day1", artifact_name, payload), payload


def _day1_payload(
    *,
    package: InvoicePackageInput,
    canonical: CanonicalInvoice,
    mode: str,
    package_source: str,
    candidate_source: str | None,
) -> dict[str, Any]:
    return {
        "day": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "package_source": package_source,
        "candidate_source": candidate_source,
        "message_id": package.message_id,
        "canonical_invoice": canonical.model_dump(mode="json"),
    }


def run_day2_from_day1_artifact(
    *,
    artifact_path: str | Path,
    known_vendor: bool | None = None,
    artifact_name: str = "golden_thread_day2",
) -> tuple[Path, dict[str, Any]]:
    payload = load_json(artifact_path)
    invoice = CanonicalInvoice.model_validate_json(json.dumps(payload["canonical_invoice"]))
    message_id = payload["message_id"]
    state = make_initial_state(
        invoice,
        package_id=message_id,
        known_vendor=_resolve_known_vendor(invoice.supplier_name, known_vendor),
        high_value_threshold=HIGH_VALUE_THRESHOLD,
        route_precedence=ROUTE_PRECEDENCE,
    )
    result = build_graph().invoke(state)
    if not isinstance(result, Day2WorkflowState):
        result = Day2WorkflowState.model_validate(result)

    artifact_payload = {
        "day": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_day1_artifact": str(artifact_path),
        "workflow_state": result.model_dump(mode="json"),
    }
    return _write_day_artifact("day2", artifact_name, artifact_payload), artifact_payload


def _resolve_known_vendor(supplier_name: str, known_vendor: bool | None) -> bool:
    if known_vendor is not None:
        return known_vendor
    return supplier_name in KNOWN_VENDORS


def run_day3_case_artifact(
    *,
    invoice: dict[str, Any],
    retrieval_mode: Literal["fixture", "azure_search_live", "pgvector_fixture"] = "azure_search_live",
    retrieval_config: RetrievalConfig | None = None,
    artifact_name: str = "golden_thread_day3",
) -> tuple[Path, dict[str, Any]]:
    config = retrieval_config or build_retrieval_config(retrieval_mode)
    state = run_day3_workflow(invoice, retrieval_mode=retrieval_mode, retrieval_config=config)
    payload = {
        "day": 3,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "retrieval_mode": retrieval_mode,
        "invoice": invoice,
        "workflow_state": {
            "workflow_id": state.workflow_id,
            "case_id": state.case_id,
            "status": state.status,
            "current_node": state.current_node,
            "branch_history": state.branch_history,
            "retrieval_context": {
                bucket: [_serialize(item) for item in items]
                for bucket, items in state.retrieval_context.items()
            },
            "agent_findings": _serialize(state.agent_findings),
            "eval_scores": state.eval_scores,
            "telemetry": state.telemetry,
        },
    }
    return _write_day_artifact("day3", artifact_name, payload), payload


class StaticPlanModel(ModelClient):
    def __init__(self, plan: ExecutionPlan) -> None:
        self.plan = plan

    async def invoke(self, prompt: str) -> str:
        return json.dumps(self.plan.model_dump(mode="json"))


async def run_day4_case_artifact(
    *,
    case_facts: CaseFacts,
    planner_mode: Literal["fixture", "azure_openai"] = "azure_openai",
    artifact_name: str = "golden_thread_day4",
) -> tuple[Path, dict[str, Any], Day4WorkflowState]:
    if planner_mode == "fixture":
        plan = build_training_plan(case_facts, plan_id=f"plan_{case_facts.case_id}")
        state = await run_day4_explicit_planning_case(
            case_facts=case_facts,
            model=StaticPlanModel(plan),
            registry=create_default_task_registry(),
        )
        raw_plan_text = json.dumps(plan.model_dump(mode="json"), indent=2)
        parsed_plan = plan
    else:
        state, raw_plan_text, parsed_plan = await _run_day4_live(case_facts)

    payload = {
        "day": 4,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "planner_mode": planner_mode,
        "raw_planner_payload": raw_plan_text,
        "validated_plan": parsed_plan.model_dump(mode="json") if parsed_plan is not None else None,
        "workflow_state": state.model_dump(mode="json"),
        "recommendation": state.recommendation,
        "escalation_package": state.escalation_package,
    }
    return _write_day_artifact("day4", artifact_name, payload), payload, state


async def _run_day4_live(case_facts: CaseFacts) -> tuple[Day4WorkflowState, str, ExecutionPlan]:
    overlay = derive_policy_overlay(case_facts)
    prompt = build_planner_prompt(case_facts=case_facts, policy_overlay=overlay)
    model = AzureOpenAIPlannerClient()
    raw_plan_text = await model.invoke(prompt)
    parsed = parse_execution_plan(coerce_json(raw_plan_text))

    state = create_initial_workflow_state(case_facts)
    state.planning.planner_input_snapshot = {
        "case_facts": case_facts.model_dump(),
        "policy_overlay": overlay.model_dump(),
    }
    state.plan = parsed
    state.planning.plan_id = parsed.plan_id
    state.planning.plan_status = "created"
    validation = validate_execution_plan(parsed, overlay)
    if not validation.valid:
        state.planning.plan_status = "rejected"
        state.planning.validation_errors = validation.errors
        state.escalation_package = {
            "case_id": case_facts.case_id,
            "plan_id": parsed.plan_id,
            "status": "plan_rejected",
            "reasons": validation.errors,
        }
        return state, raw_plan_text, parsed

    state.planning.plan_status = "validated"
    state.planning.validated = True
    state = await run_day4_explicit_planning_case(
        case_facts=case_facts,
        model=StaticPlanModel(parsed),
        registry=create_default_task_registry(),
    )
    return state, raw_plan_text, parsed
