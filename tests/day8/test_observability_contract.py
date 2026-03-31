from __future__ import annotations

from aegisap.observability.context import make_workflow_observability_context
from aegisap.observability.tracing import business_outcome_attributes, node_span_attributes, root_span_attributes


def test_root_span_attributes_hash_case_and_thread_identifiers() -> None:
    context = make_workflow_observability_context(
        request_id="req-1",
        workflow_run_id="wf-1",
        case_id="case-raw-123",
        thread_id="thread-raw-456",
    )
    context.plan_version = "day4"
    context.policy_version = "policy-v1"
    context.outcome_type = "approved_to_proceed"
    attrs = root_span_attributes(context)

    assert attrs["aegis.workflow_run_id"] == "wf-1"
    assert attrs["aegis.case_id"] != "case-raw-123"
    assert attrs["aegis.thread_id"] != "thread-raw-456"
    assert attrs["aegis.plan_version"] == "day4"
    assert attrs["aegis.policy_version"] == "policy-v1"


def test_root_span_attributes_include_training_checkpoint_metadata_when_present() -> None:
    context = make_workflow_observability_context(
        request_id="req-2",
        workflow_run_id="wf-2",
        case_id="case-2",
        thread_id="thread-2",
    )
    context.metadata["checkpoint_phase"] = "day8_trace_extension"
    context.metadata["checkpoint_span"] = "day8.eval_guardrail"

    attrs = root_span_attributes(context)

    assert attrs["aegis.checkpoint_phase"] == "day8_trace_extension"
    assert attrs["aegis.checkpoint_span"] == "day8.eval_guardrail"


def test_node_and_business_outcome_attribute_sets_match_day8_contract() -> None:
    node_attrs = node_span_attributes(
        node_name="vendor_history_check",
        node_attempt=2,
        retry_count=1,
        idempotent=True,
        failure_class="dependency_failure",
        evidence_count=3,
        checkpoint_loaded=False,
        checkpoint_saved=True,
        prompt_revision="day4",
        model_name="gpt-4.1",
        retrieval_index_version="day3-v1",
    )
    outcome_attrs = business_outcome_attributes(
        recommendation_value_band="high",
        vendor_risk_status="low",
        po_match_status="pass",
        human_review_required=False,
        final_decision_type="recommendation_ready",
    )

    assert node_attrs["aegis.node_name"] == "vendor_history_check"
    assert node_attrs["aegis.retry_count"] == 1
    assert node_attrs["aegis.retrieval_index_version"] == "day3-v1"
    assert outcome_attrs["aegis.recommendation_value_band"] == "high"
    assert outcome_attrs["aegis.final_decision_type"] == "recommendation_ready"
