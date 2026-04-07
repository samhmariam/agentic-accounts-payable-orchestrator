# Day 13 — Portal-First Integration Boundary

> **Portal mode:** `Operate`  
> **Intent:** inspect the live boundary and recovery surfaces before the contract is summarized by scripts or reports.

## Portal-First Outcome

You can point to the external boundary host, the Service Bus recovery surface,
and the monitoring evidence that proves failures are contained safely.

## Portal Mode

This is an integration-operations day. Treat the portal as the first source for
boundary truth, queue state, and recovery visibility.

## Azure Portal Path

1. Open the deployed boundary host, whether Azure Functions or Container Apps, and inspect ingress, auth, and identity.
2. Open Service Bus and inspect the queue and dead-letter count.
3. Open Application Insights or the relevant monitoring surface and inspect webhook handling, DLQ drain activity, and compensating-action traces.
4. If the MCP host is deployed, inspect the hosting resource and logs so the contract is tied to a live Azure surface.
5. Record any mismatch between the live recovery picture and the contract you intend to defend.

## What To Capture

- Boundary host name and auth surface.
- Queue or DLQ state from Service Bus.
- One monitoring view tied to webhook reliability or compensating action behavior.
- A short statement about whether the live Azure boundary matches the intended contract.

## Three-Surface Linkage

- `Portal`: inspect the boundary host, Service Bus queue and DLQ, monitoring, and MCP hosting surface directly in Azure.
- `Notebook`: open [day_13_integration_boundary_and_mcp.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_13_integration_boundary_and_mcp.py) and use the boundary and recovery sections to explain what that live Azure state means.
- `Automation`: run `scripts/verify_mcp_contract_integrity.py`, `scripts/verify_webhook_reliability.py`, and the Day 13 test path only after the live boundary story is understood.
- `Evidence`: the live Azure boundary, the notebook recovery narrative, and the Day 13 contract and DLQ reports should all describe the same safe integration posture.

## Handoff To Notebook

- Open [day_13_integration_boundary_and_mcp.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_13_integration_boundary_and_mcp.py).
- Use [DAY_13_INTEGRATION_AND_MCP.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_13_INTEGRATION_AND_MCP.md) and the Day 13 artifact templates to interpret the Azure evidence.

## Handoff To Automation

After the live boundary inspection, verify the contract and recovery path:

```bash
uv run python scripts/verify_mcp_contract_integrity.py
uv run python scripts/verify_webhook_reliability.py
uv run python -m pytest tests/day13 -q
```
