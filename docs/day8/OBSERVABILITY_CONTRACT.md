# Observability Contract

## Root Span

- Name: `aegis.workflow.run`
- Required attributes:
  - `aegis.workflow_run_id`
  - `aegis.thread_id`
  - `aegis.case_id`
  - `aegis.state_version`
  - `aegis.plan_version`
  - `aegis.policy_version`
  - `aegis.environment`
  - `aegis.deployment_revision`
  - `aegis.actor_type`
  - `aegis.outcome_type`
  - `aegis.approval_status`

## Node Spans

- Use `task.<task_type>` for Day 4 tasks.
- Use `aegis.workflow.day4.plan`, `aegis.workflow.day4.execute`,
  `aegis.workflow.day6.review`, `aegis.workflow.day5.persist_state`,
  `aegis.workflow.day5.resume`, and `aegis.workflow.audit_write` for major
  runtime boundaries.
- Required node attributes:
  - `aegis.node_name`
  - `aegis.node_attempt`
  - `aegis.retry_count`
  - `aegis.idempotent`
  - `aegis.failure_class`
  - `aegis.evidence_count`
  - `aegis.checkpoint_loaded`
  - `aegis.checkpoint_saved`
  - `aegis.prompt_revision`
  - `aegis.model_name`
  - `aegis.retrieval_index_version`

## Business Outcome Attributes

- `aegis.recommendation_value_band`
- `aegis.vendor_risk_status`
- `aegis.po_match_status`
- `aegis.human_review_required`
- `aegis.final_decision_type`

## Event Names

- `retry_scheduled`
- `retry_aborted`
- `fallback_used`
- `checkpoint_restored`
- `cache_hit`
- `cache_miss`
- `evidence_insufficient`
- `policy_refusal`
- `human_review_escalated`
- `timeout_budget_exhausted`

Each event carries typed attrs for `error_class`, `attempt_number`,
`backoff_ms`, `remaining_budget_ms`, `dependency_name`, and
`decision_reason_code`.
