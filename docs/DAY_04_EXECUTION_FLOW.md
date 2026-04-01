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

---

## FDE Rubric — Day 4 (100 points)

| Dimension | Points |
|---|---|
| Extraction correctness | 25 |
| Policy over model precedence | 25 |
| Reversible / irreversible reasoning | 20 |
| Test quality | 15 |
| Defense quality | 15 |

**Pass bar: 80.  Elite bar: 90.**

## Oral Defense Prompts

1. Which action in your risk register did you classify as irreversible and what deterministic policy prevents the model from triggering it?
2. If the policy overlay fails open instead of closed, what is the blast radius across financial controls and who absorbs the liability?
3. Who must approve a change to the policy precedence rules, and what test evidence would the approver require before accepting the change?

## Artifact Scaffolds

- `docs/curriculum/artifacts/day04/ACTION_RISK_REGISTER.md`
- `docs/curriculum/artifacts/day04/POLICY_PRECEDENCE.md`
- `docs/curriculum/artifacts/day04/FAIL_CLOSED_TEST_CASES.json`
