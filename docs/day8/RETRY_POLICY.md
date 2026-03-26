# Retry Policy

- Retry idempotent reads and transport-safe model calls only.
- Do not generically retry audit writes, checkpoint writes, or other
  non-idempotent mutations.
- Retry only transient classes such as 429, 5xx, quota throttle, connection
  reset, and short timeouts.
- Stop retrying when the remaining node budget is too small to complete useful
  work.
- Use capped exponential backoff with jitter.
- Record retry reason, dependency, failure class, and attempt number in spans
  and metrics.
