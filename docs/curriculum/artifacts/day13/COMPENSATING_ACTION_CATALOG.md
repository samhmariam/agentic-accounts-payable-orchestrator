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

## Acceptance Criteria

- Minimum 5 compensating actions
- Idempotency guarantee is specified per action (e.g., "safe to replay up to N times")
- Silent failure section is non-empty — if all actions are monitored, explain the monitoring mechanism
- Test coverage names a specific test for each action (not "unit tests cover this")
- Ownership has an individual role per action — not "the platform team"
