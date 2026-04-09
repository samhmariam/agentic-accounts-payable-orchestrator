# Rollback Runbook — AegisAP

**Version:** 1.0  
**Applies to:** All AegisAP ACA revisions (worker, api)  
**On-call:** Consult incident_response_runbook.md for escalation path

---

## Prerequisites

- Azure CLI authenticated with at least `Contributor` on the ACA resource group
- Access to Azure Container Registry (AcrPull on the registry)
- `AZURE_RESOURCE_GROUP` set in your shell

---

## Step 1 — Identify the Failing Revision

```bash
az containerapp revision list \
  --name aegisap-worker \
  --resource-group $AZURE_RESOURCE_GROUP \
  --query "[].{name:name, active:properties.active, traffic:properties.trafficWeight, created:properties.createdTime}" \
  -o table
```

Note the revision names for **canary** (new, failing) and **stable** (previous, known-good).

---

## Step 2 — Redirect All Traffic to Stable

```bash
# Replace <STABLE_REVISION> with the known-good revision name
az containerapp ingress traffic set \
  --name aegisap-worker \
  --resource-group $AZURE_RESOURCE_GROUP \
  --revision-weight <STABLE_REVISION>=100 \
  -o json
```

Verify:

```bash
az containerapp ingress traffic show \
  --name aegisap-worker \
  --resource-group $AZURE_RESOURCE_GROUP \
  -o json
```

Do not move to source-control recovery yet. First prove the control-plane change
has propagated and the stable revision is the only production target.

---

## Step 3 — Deactivate the Failing Revision

```bash
az containerapp revision deactivate \
  --name aegisap-worker \
  --resource-group $AZURE_RESOURCE_GROUP \
  --revision <CANARY_REVISION>
```

---

## Step 4 — Wait For Readiness Then Verify Recovery

Traffic movement is a control-plane event. Replica readiness is a data-plane
event and may lag behind routing. Use retry/backoff before you treat early 503s
as rollback failure.

```bash
for attempt in 1 2 3 4 5; do
  if curl -sf https://aegisap.example/health/ready; then
    echo "Ready on attempt $attempt"
    break
  fi
  sleep $(( attempt * 5 ))
done
```

Run all gates to confirm the stable revision is passing:

```bash
python scripts/check_all_gates_v2.py
```

All 17 gates must pass before closing the incident.

---

## Step 5 — Post-Incident

Only after traffic is restored and readiness is confirmed should you decide
whether `git revert` or a fix-forward PR is required.

1. File an incident report with timeline and root cause.
2. Update `evals/failure_drills/` if a new failure mode was encountered.
3. Re-run `notebooks/day_14_breaking_changes_elite_ops.py` to update the CTO trace report.

---

## Rollback Decision Criteria

| Signal | Action |
|---|---|
| Error rate > 5 % on canary | Immediate rollback — no waiting |
| F1 delta < -0.05 | Immediate rollback |
| P99 latency > 10 s | Rollback + performance investigation |
| Any gate_* failure in production | Rollback + incident declaration |
| DLQ depth > 100 messages | Pause ingress, drain DLQ, investigate |
