# Day 09 Bridge — Routing And Cost Control

## Portal Signal

- Application Insights shows risky work staying on the light tier.
- Cost pressure is visible, but safety routing has drifted.

## Notebook Proof

- Use the routing, cache, and budget preview.
- Prove the risky slice must escalate even when cheaper routing looks attractive.

## Production Codification

- `src/aegisap/routing/routing_policy.py`: codify risk-aware tier selection.
- `src/aegisap/cache/cache_policy.py`: codify any required cache bypass.
- `src/aegisap/cost/budget_gate.py`: codify budget framing without weakening safety.

## Export To Production

- Which telemetry proved the wrong tier choice?
- Which notebook output showed the correct routing rule?
- Which policy file makes the safety override durable?
