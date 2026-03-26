# Latency Budgets

- Total workflow median: 5s machine time
- Total workflow p95: 12s machine time
- Day 4 planning p95: 4s
- Day 4 task worker p95: 1.5s per task
- Day 6 review p95: 1s
- Checkpoint save/load p95: 400ms
- Audit write p95: 250ms
- Approval wait is tracked separately from machine execution latency

## Separate These Clocks

- active machine time
- dependency wait time
- human wait time
- telemetry ingestion lag
