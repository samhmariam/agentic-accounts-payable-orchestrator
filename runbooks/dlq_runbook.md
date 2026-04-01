# DLQ Runbook — AegisAP Service Bus Dead-Letter Queue

**Version:** 1.0  
**Trigger:** Azure Monitor alert `ServiceBusDlqDepth > 10` OR `gate_dlq_drain_health` fails

---

## Step 1 — Assess the DLQ

```bash
# Get DLQ message count
az servicebus queue show \
  --name invoice-submissions \
  --namespace-name $SERVICE_BUS_NAMESPACE \
  --resource-group $AZURE_RESOURCE_GROUP \
  --query "properties.countDetails.deadLetterMessageCount"
```

---

## Step 2 — Drain the DLQ Automatically

```bash
python scripts/verify_webhook_reliability.py
```

This runs `DlqConsumer.drain()` with registered compensating actions:
- Non-transient messages → marked for human review in audit log
- Transient messages → re-queued to the main queue

Check the output: `build/day13/dlq_drain_report.json`

```bash
cat build/day13/dlq_drain_report.json | python -m json.tool
```

---

## Step 3 — Manual Triage (if automated drain insufficient)

```bash
# Peek at DLQ messages without consuming
az servicebus queue message peek \
  --queue-name "invoice-submissions/$DeadLetterQueue" \
  --namespace-name $SERVICE_BUS_NAMESPACE \
  --resource-group $AZURE_RESOURCE_GROUP
```

For each message, check the dead-letter reason:
- `MaxDeliveryCountExceeded` — check logs for processing errors
- `TTLExpiredException` — increase TTL or fix processing rate
- `schema_validation_failed` — fix upstream message schema

---

## Step 4 — Remediation Patterns

| Root Cause | Fix |
|---|---|
| Orchestrator crashing on certain payloads | Fix bug in LangGraph graph, redeploy, re-queue messages |
| Downstream API unavailable | Wait for recovery, re-queue messages after service restored |
| Schema mismatch | Fix sender schema, dead-letter as non-transient, notify sender |
| Rate limiting | Increase Service Bus throughput tier, add backpressure |

---

## Step 5 — Verify Gate Health

```bash
python scripts/check_all_gates_v2.py
```

`gate_dlq_drain_health` must pass before closing the incident.

---

## DLQ Depth Thresholds

| Depth | Action |
|---|---|
| 1-10 | Monitor, drain at next maintenance window |
| 11-50 | P2 incident, drain within 1 hour |
| 51-100 | P1 incident, pause invoice ingress, drain immediately |
| > 100 | P1, escalate to Engineering Director, pause all processing |
