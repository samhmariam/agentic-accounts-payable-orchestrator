# Day 4 - Explicit Planning

## Summary

Day 4 moves AegisAP from agent-driven sequencing to a plan-driven control plane under `aegisap.day4`.

The workflow now follows this shape:

```text
compile case facts -> derive policy overlay -> request plan payload
-> parse + validate plan -> execute planned tasks serially
-> evaluate recommendation gate -> recommend or escalate
```

The planner is a controller, not a recommender. It produces a typed execution plan that can be rejected before any recommendation work is allowed to continue.

## Design Rules

1. Plan first, act second.
2. The plan is strict Pydantic data, not prose.
3. Deterministic policy overlays outrank planner judgment.
4. Recommendation eligibility is explicit.
5. Planner or execution failures fail closed into escalation.

## Day 3 Baseline

`aegisap.day3` remains the frozen behavioral baseline. Day 4 reuses Day 3 specialists behind typed worker contracts, but it does not change the Day 3 graph or decision logic.

## Day 4 State

Day 4 state adds inspectable planning, eligibility, and task-ledger sections:

```json
{
  "planning": {
    "requires_explicit_plan": true,
    "plan_status": "not_started",
    "plan_id": null,
    "plan_version": "day4",
    "planner_input_snapshot": {},
    "validated": false,
    "validation_errors": [],
    "active_task_ids": [],
    "completed_task_ids": [],
    "blocked_task_ids": [],
    "escalation_status": "none"
  },
  "eligibility": {
    "recommendation_allowed": false,
    "unmet_preconditions": [],
    "missing_evidence": [],
    "required_approvals": [],
    "blocking_conditions": [],
    "irreversible_actions_allowed": false
  },
  "task_ledger": []
}
```

## Plan Shape

The execution plan is normalized to `snake_case` and contains:

```json
{
  "plan_id": "plan_case_001",
  "case_id": "case_001",
  "goal": "Determine whether payment recommendation is eligible",
  "case_risk_flags": ["high_value", "missing_po", "bank_details_changed"],
  "planning_rationale": "Structured rationale only.",
  "tasks": [
    {
      "task_id": "vendor_bank_verification",
      "task_type": "vendor_bank_verification",
      "owner_agent": "vendor_risk_verifier",
      "depends_on": [],
      "inputs": {
        "case_id": "case_001",
        "invoice_id": "inv_001"
      },
      "required_evidence": ["supplier_master_record", "bank_change_request_evidence"],
      "expected_outputs": [
        "bank_change_verified",
        "authoritative_source_checked",
        "risk_level",
        "confidence"
      ],
      "preconditions": [],
      "stop_if_missing": true,
      "min_confidence": 0.9,
      "on_failure": "escalate",
      "action_class": "reversible"
    }
  ],
  "global_preconditions": [
    "po_verified_or_waived",
    "bank_change_authoritatively_verified",
    "approval_route_defined_for_threshold_case"
  ],
  "global_stop_conditions": [
    "missing_required_po_evidence",
    "unverified_bank_change",
    "combined_risk_requires_manual_review"
  ],
  "escalation_triggers": [
    "missing_po",
    "bank_details_changed",
    "high_value_invoice",
    "combined_risk_flags_present"
  ],
  "escalation_route": {
    "queue": "finance_ops_manual_review",
    "owners": ["ap_manager", "vendor_master_team", "controller"]
  },
  "escalation_reason_template": "Escalate immediately when mandatory controls remain unresolved.",
  "required_approvals": ["ap_manager", "controller"],
  "recommendation_gate": {
    "all_mandatory_tasks_completed": true,
    "required_evidence_present": true,
    "no_unresolved_blockers": true,
    "confidence_thresholds_met": true,
    "required_approvals_identified": true,
    "mandatory_escalations_resolved_or_triggered": true,
    "po_condition_satisfied": true,
    "bank_change_verification_satisfied": true,
    "approval_path_satisfied": true
  },
  "action_classification": {
    "current_stage": "reversible",
    "irreversible_actions_allowed": false
  }
}
```

## Policy Overlay

The deterministic overlay compiles normalized case facts into mandatory controls before planner output is trusted.

Hard rules currently enforced:

- Missing PO adds PO verification or waiver tasks and blocks recommendation until resolved.
- Changed bank details add authoritative bank verification and escalate on failure.
- Threshold cases add approval-path checks and required approvals.
- Missing PO plus changed bank details force manual escalation.
- High value plus missing PO plus changed bank details force combined-risk escalation.

## Execution Model

Execution stays intentionally serial in Day 4. The executor:

1. initializes the task ledger
2. runs ready tasks whose dependencies and preconditions are satisfied
3. validates worker outputs against typed task contracts
4. records outputs, confidence, blockers, and evidence refs
5. stops when escalation becomes mandatory, a stop condition triggers, or no ready work remains

Mandatory escalation cases can execute the manual escalation task and skip downstream recommendation work.

## Recommendation Gate

A recommendation is only allowed when the gate can prove all of the following:

- mandatory tasks are completed
- required evidence is present
- confidence thresholds are met
- required approvals are identified
- PO, bank-change, and approval-path preconditions are satisfied
- no unresolved blockers remain
- no mandatory escalation path remains active

If any of those checks fail, the workflow composes an escalation package instead of falling through to recommendation generation.

## Testing

Day 4 coverage includes:

- strict schema validation
- policy-overlay derivation
- validator rejection of omitted mandatory controls
- malformed planner output failing closed
- serial executor behavior
- recommendation gate behavior
- fixture-driven integration tests for clean path, missing PO, bank change, high value plus missing PO, and combined-risk scenarios

The primary exit check remains the high-value, missing-PO, changed-bank-details case. The expected outcome is manual review with no recommendation package.
