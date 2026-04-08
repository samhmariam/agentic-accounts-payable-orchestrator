# Day 02 Bridge — Resilience Controls

## Portal Signal

- Azure Monitor or Application Insights shows real `429` pressure.
- The protected path is retrying or queueing incorrectly.

## Notebook Proof

- Use the retry and backpressure previews to prove the safe behavior.
- Separate idempotent retry logic from protected-path queueing logic.

## Production Codification

- `src/aegisap/observability/retry_policy.py`: codify bounded retry behavior.
- `src/aegisap/resilience/backpressure.py`: codify queue-or-block behavior for saturated protected paths.

## Export To Production

- Which signal proved quota pressure was real?
- Which rule decides retry versus queue?
- Which file makes that decision durable?
