from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree

from aegisap.day4.state.workflow_state import create_initial_workflow_state
from aegisap.day4.planning.plan_types import CaseFacts
from aegisap.day5.workflow.day4_handoff import bootstrap_durable_state_from_day4


def test_day4_to_day5_handoff_preserves_day9_fields() -> None:
    case_facts = CaseFacts(
        case_id="case-1",
        invoice_id="inv-1",
        supplier_id="vendor-1",
        supplier_name="Contoso",
        supplier_exists=True,
        invoice_amount_gbp=12000,
        invoice_currency="GBP",
        po_present=True,
        bank_details_changed=False,
    )
    state = create_initial_workflow_state(case_facts, workflow_run_id="wf-1")
    state.task_class = "plan"
    state.risk_flags = ["clean_path"]
    state.routing_decision = {"reason": "plan_selected_strong_model"}
    state.model_deployment = "gpt-4.1"
    state.cache_hit = False
    state.workflow_cost_estimate = 0.012
    state.cost_ledger = [{"task_class": "plan", "estimated_cost": 0.012}]

    durable = bootstrap_durable_state_from_day4(state, thread_id="thread-1")

    assert durable.task_class == "plan"
    assert durable.routing_decision["reason"] == "plan_selected_strong_model"
    assert durable.workflow_cost_estimate == 0.012
    assert durable.cost_ledger[0]["task_class"] == "plan"


def test_day9_dataset_contains_required_slices() -> None:
    path = Path("data/day9/eval/day9_routing_cases.jsonl")
    required = {
        "clean_routine_invoices",
        "missing_po",
        "new_vendor",
        "bank_details_changed",
        "contradictory_vat_evidence",
        "cross_border_multi_currency",
        "retrieval_ambiguity",
        "human_review_required",
    }
    slices: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        payload = json.loads(line)
        slices.update(payload["slices"])

    assert required.issubset(slices)


def test_apim_policy_assets_are_well_formed_xml() -> None:
    for path in (
        Path("infra/apim/policies/semantic-cache.xml"),
        Path("infra/apim/policies/token-metrics.xml"),
        Path("infra/apim/policies/rate-limit.xml"),
    ):
        root = ElementTree.fromstring(path.read_text(encoding="utf-8"))
        assert root.tag == "policies"
