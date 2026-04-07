# Day 09 — Portal-First Telemetry And Cost

> **Portal mode:** `Operate`  
> **Intent:** use live Azure telemetry and scale evidence before the notebook or scripts summarize it for you.

## Portal-First Outcome

You can inspect a real workflow run in Azure, connect its telemetry to routing or
cost decisions, and then explain how the repo captures the same story in artifacts.

## Portal Mode

Day 9 is a live-evidence day. Prefer operator-facing Azure views before derived
reports or notebook explanations.

## Azure Portal Path

1. Open Application Insights and inspect one workflow run using **Transaction search** or **Distributed tracing**.
2. Open **Metrics** and check latency, failure rate, throughput, or cost-adjacent signals.
3. Open the linked Log Analytics workspace and run one of the KQL patterns from the notebook.
4. Inspect Container App metrics and scale charts so cost and routing stay connected to real demand signals.
5. Record where the evidence contradicts intuition or a local assumption.

## What To Capture

- One trace view for a real workflow run.
- One KQL result you can explain in operator language.
- One scale or metrics view tied to routing, latency, or cache behavior.
- A short statement about whether the live telemetry supports the Day 9 routing story.

## Handoff To Notebook

- Open [day_9_scaling_monitoring_cost.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_9_scaling_monitoring_cost.py).
- Use [DAY_09_COST_SPEED_ROUTING_CACHING_AND_OPTIMISATION.md](/workspaces/agentic-accounts-payable-orchestrator/docs/day9/DAY_09_COST_SPEED_ROUTING_CACHING_AND_OPTIMISATION.md) to turn the Azure signals into cost and routing decisions.

## Handoff To Automation

Once you can read the Azure evidence directly, use the repo’s reporting path:

```bash
uv run python -m pytest tests/day9 -q
python -m json.tool build/day9/routing_report.json
```
