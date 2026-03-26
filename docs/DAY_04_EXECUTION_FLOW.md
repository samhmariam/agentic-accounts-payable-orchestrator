# Day 4 - Execution Flow

## Flow

```text
case_facts
-> derive_policy_overlay
-> request_execution_plan_payload
-> parse_execution_plan
-> validate_execution_plan
-> execute_plan
-> evaluate_recommendation_gate
-> compose_recommendation | compose_escalation_package
```

## Execution Semantics

- The planner returns raw JSON only.
- Parsing and validation are deterministic and can reject the plan before any recommendation work begins.
- The executor is serial by design for inspectability.
- Worker outputs are validated against task contracts before they are accepted into state.
- Recommendation generation is a final gated step, not a task side effect.

## Stop Conditions

Execution exits early when any of these become true:

- a mandatory escalation path is active
- a stop condition is triggered
- no ready tasks remain
- the recommendation gate can already prove the case is ineligible

Forced-escalation scenarios can still execute `manual_escalation_package`, but downstream recommendation work is skipped.
