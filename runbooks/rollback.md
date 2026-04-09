# Rollback Runbook

This runbook treats an Azure Container Apps revision as the rollback unit.
Rollback is required when a new revision is operationally alive but fails Day 10
business-safety gates such as compliance accuracy, mandatory escalation recall,
structured refusal behavior, or replay safety.

Do not start with `git revert`. Restore live traffic to the last-known-good ACA
revision first, verify readiness, and only then decide whether a source-control
revert is also required.

## Inputs

- Azure subscription
- resource group
- container app name
- current bad revision name
- previous good revision name

## Identify the Active and Prior Revisions

```bash
az containerapp revision list \
  --resource-group <resource-group> \
  --name <container-app-name> \
  --output table
```

Choose the most recent previously healthy revision as the rollback target.

## Shift Live Traffic To The Prior Good Revision

```bash
az containerapp ingress traffic set \
  --resource-group <resource-group> \
  --name <container-app-name> \
  --revision-weight <previous-good-revision>=100 \
  -o json
```

Verify the routed revision identity:

```bash
az containerapp ingress traffic show \
  --resource-group <resource-group> \
  --name <container-app-name> \
  -o json
```

Deactivate the bad revision after traffic has moved:

```bash
az containerapp revision deactivate \
  --resource-group <resource-group> \
  --name <container-app-name> \
  --revision <bad-revision>
```

## Verification

After rollback, wait for replica readiness before you judge the data plane:

```bash
for attempt in 1 2 3 4 5; do
  if curl -sf https://<app-host>/health/ready; then
    break
  fi
  sleep $(( attempt * 5 ))
done
```

Then verify:

1. `GET /health/live`
2. `GET /health/ready`
3. `GET /version` and verify the expected prior SHA
4. run `scripts/smoke_test.py`
5. run `scripts/check_traces.py` for one workflow run

If the rollback revision fails readiness or safety checks, escalate immediately.

## Incident Notes

Capture:

- bad revision name and SHA
- rollback target revision name and SHA
- traffic-shift command and verification command
- failed gate or trigger condition
- time rollback started
- time rollback completed
- operator performing rollback

## Immediate Rollback Triggers

Rollback immediately if any of these happen in production:

- compliance decision accuracy drops below threshold
- mandatory-escalation recall drops below threshold
- any malicious case returns a non-structured refusal
- resume/replay creates duplicate side effects
- a required correlated trace is missing because the deployed revision is not
  emitting the expected telemetry contract
