# COMPENSATING ACTION CATALOG

<!-- CAPSTONE_B: This artifact applies to both AP and claims intake transfer domain -->

## Purpose

Enumerate every compensating action in the system's async reliability design —
so that failure modes have explicit, tested responses rather than implicit handling.

## Required Headings

1. Compensating action inventory (action ID, trigger condition, compensating action, idempotency guarantee, blast radius if action fails)
2. Silent failure detection — which compensating actions might fail without raising an alert and how that is caught
3. Ordering guarantees — which compensating actions must fire in a specific order and why
4. Test coverage — for each compensating action, what test verifies it fires correctly
5. Ownership — who is accountable for each compensating action being implemented and maintained

## Guiding Questions

- Which compensating action has the highest blast radius if it fires incorrectly?
- Which compensating action is most likely to fail silently in production?
- If compensating actions A and B both fire for the same failure, is there a conflict?
- Who would investigate a compensating action failure at 03:00 on a Sunday?

## Structural Example — Compensating Action Rows

| Action ID | Trigger condition | Compensating action | Idempotency guarantee | Blast radius if action fails |
|---|---|---|---|---|
| CA-01 | Service Bus handler exceeds max retries on invoice extraction | Move message to DLQ and create analyst review task | Safe to replay task creation once because task key is deterministic | Exception workload becomes invisible and misses SLA |
| CA-02 | Duplicate payment-hold event received | Ignore duplicate and append audit log entry only | Safe to replay indefinitely because natural key is event ID | Duplicate downstream holds or confused finance analyst |
| CA-03 | Claims adjudication enrichment timeout | Persist partial case with `external_data_pending` state and schedule retry | Safe to replay up to 3 times with same case ID | Claim remains stuck without visibility into missing dependency |
| CA-04 | MCP tool invocation fails after mutation side effect begins | Issue compensating reversal command and notify operator | Safe once; second replay is a no-op because reversal token is single-use | External system remains in mismatched state with AegisAP |
| CA-05 | OBO token exchange fails after boundary validation | Reject request and write actor-bound audit event for manual replay | Safe to replay request after auth repair because no business mutation occurred | Unauthorized work is attempted without traceable actor context |

## Anti-Patterns To Avoid

- Do not use "retry" as the entire compensating action if business state already changed.
- Do not claim idempotency without saying what key or state makes it safe.
- Do not leave night/weekend ownership implicit for high-blast-radius actions.

## Acceptance Criteria

- Minimum 5 compensating actions
- Idempotency guarantee is specified per action (e.g., "safe to replay up to N times")
- Silent failure section is non-empty — if all actions are monitored, explain the monitoring mechanism
- Test coverage names a specific test for each action (not "unit tests cover this")
- Ownership has an individual role per action — not "the platform team"
