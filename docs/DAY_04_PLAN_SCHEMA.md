# Day 4 - Plan Schema

## Top Level

`ExecutionPlan` is the primary Day 4 artifact. All fields are strict and `snake_case`.

- `plan_id`
- `case_id`
- `goal`
- `case_risk_flags`
- `planning_rationale`
- `tasks`
- `global_preconditions`
- `global_stop_conditions`
- `escalation_triggers`
- `escalation_route`
- `escalation_reason_template`
- `required_approvals`
- `recommendation_gate`
- `action_classification`

## Task Shape

Each task is typed, dependency-aware, and executable:

```json
{
  "task_id": "po_match_verification",
  "task_type": "po_match_verification",
  "owner_agent": "po_match_agent",
  "depends_on": ["policy_retrieval"],
  "inputs": {
    "case_id": "case_001",
    "invoice_id": "inv_001"
  },
  "required_evidence": ["po_number"],
  "expected_outputs": [
    "po_match_status",
    "matched_fields",
    "missing_fields",
    "mismatch_flags",
    "confidence"
  ],
  "preconditions": [],
  "stop_if_missing": true,
  "min_confidence": 0.9,
  "on_failure": "block",
  "action_class": "reversible"
}
```

## Gate Shape

The recommendation gate encodes explicit unlock conditions:

```json
{
  "all_mandatory_tasks_completed": true,
  "required_evidence_present": true,
  "no_unresolved_blockers": true,
  "confidence_thresholds_met": true,
  "required_approvals_identified": true,
  "mandatory_escalations_resolved_or_triggered": true,
  "po_condition_satisfied": true,
  "bank_change_verification_satisfied": true,
  "approval_path_satisfied": true
}
```

## Escalation Metadata

Escalation is encoded directly in the plan:

```json
{
  "escalation_route": {
    "queue": "finance_ops_manual_review",
    "owners": ["ap_manager", "vendor_master_team"]
  },
  "escalation_reason_template": "Escalate for manual review when mandatory controls remain unresolved."
}
```

## Day 4 Constraint

All tasks and the plan-level action classification remain reversible in Day 4. `irreversible_actions_allowed` must stay `false`.
