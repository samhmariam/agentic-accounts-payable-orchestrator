# Day 10 — Portal-First Release Readiness

> **Portal mode:** `Operate`  
> **Intent:** validate release state in Azure before trusting a green gate artifact.

## Portal-First Outcome

You can prove from Azure itself which revision is live, whether it is healthy,
and whether the release story matches the runtime truth.

## Portal Mode

Do not start with the gate runner. Start by checking the live release surface in
Container Apps and monitoring.

## Azure Portal Path

1. Open the Container App and inspect **Revisions** to identify the live, inactive, and candidate revisions.
2. Open **Ingress** and record the externally reachable URL and the revision receiving traffic.
3. Open Application Insights or the linked monitoring blade and check health for the candidate revision.
4. If a release was halted or rolled back, confirm the traffic shift is visible in Azure rather than only in local notes.
5. Compare the live Azure state to the story you expect the release envelope to tell.

## What To Capture

- Active revision name and traffic state.
- One health or monitoring view proving the active revision is or is not healthy.
- One discrepancy, if any, between portal truth and local release assumptions.

## Three-Surface Linkage

- `Portal`: inspect revisions, traffic, ingress, and health in Azure before you trust any gate output.
- `Notebook`: open [day_10_production_operations.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_10_production_operations.py) and use the release-evidence map to interpret what the live release state actually means.
- `Automation`: run `scripts/check_all_gates.py` and the Day 10 test path only after the Azure release picture is already understood.
- `Evidence`: the portal release state, the notebook release judgment, and `build/day10/release_envelope.json` should all say the same go, hold, or rollback story.

## Handoff To Notebook

- Open [day_10_production_operations.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_10_production_operations.py).
- Use [DAY_10_DEPLOYMENT_AND_ACCEPTANCE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_10_DEPLOYMENT_AND_ACCEPTANCE.md) to connect Azure release state to CAB and gate evidence.

## Handoff To Automation

Only after the portal check should you trust the shared release tooling:

```bash
uv run python scripts/check_all_gates.py --out build/day10/release_envelope.json
uv run python -m pytest tests/day10 tests/api/test_app.py -q
```
