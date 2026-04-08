# Customer Escalation: Day 2 Quota Storm

The AP orchestrator is falling over during a bulk reprocessing event. We are seeing repeated `429` throttle errors from Azure OpenAI, and the protected planning path is not queuing safely when capacity is saturated.

Security does not want us to widen privileges or disable controls. Operations wants a concrete software fix today.

What I need from engineering:

- reproduce the 429 behavior under the current resilience policy
- repair retry and backpressure behavior without making side effects unsafe
- show the updated code, the passing resilience tests, and the NFR or ADR evidence that explains the fix
