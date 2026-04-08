# Day 04 Bridge — Fail-Closed Planning

## Portal Signal

- The risky invoice trace shows missing PO plus changed bank details.
- The final routing outcome no longer matches the policy intent.

## Notebook Proof

- Use the overlay preview to prove the combined-risk slice.
- Confirm manual escalation and recommendation gating must fail closed.

## Production Codification

- `src/aegisap/day4/planning/policy_overlay.py`: codify risk derivation and mandatory task generation.
- `src/aegisap/day4/recommendation/recommendation_gate.py`: codify the terminal block on unsafe slices.

## Export To Production

- Which risk flags were missing or mishandled?
- Which notebook output proved the fail-closed expectation?
- Which file enforces the permanent gate?
