# Day 06 — Portal-First Data Authority

> **Portal mode:** `Inspect`  
> **Intent:** understand data authority as real Azure service choices before the notebook turns it into a conceptual pyramid.

## Portal-First Outcome

You can map each data-authority tier to a real Azure surface and explain why one
service is authoritative, canonical, operational, or analytical.

## Portal Mode

Use live resources where they exist. If ADF, Cosmos DB, or Azure ML are not
provisioned in the training tenant, use the portal create blades as a design
walkthrough without actually deploying them.

## Azure Portal Path

1. Open PostgreSQL, Storage, and Azure AI Search and classify them by authority level in the system.
2. If Cosmos DB is available, inspect its consistency, network, backup, and identity settings.
3. If Azure Data Factory is available, inspect pipeline monitor or create-blade settings that affect identity, linked services, and scheduling.
4. If Azure ML or MLflow hosting is available, inspect the workspace or tracking surface that would hold model-evaluation evidence.
5. Note where the Azure service boundary stops and where the application decides which tier wins during conflict.

## What To Capture

- A four-tier authority map using real or planned Azure services.
- One example of a service that should never override a higher-authority source.
- One identity or networking setting that matters for governed data access.

## Handoff To Notebook

- Open [day_6_data_ml_integration.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_6_data_ml_integration.py).
- Use [DAY_06_REFLECTION_AND_GRACEFUL_REFUSAL.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_06_REFLECTION_AND_GRACEFUL_REFUSAL.md) and the Day 6 artifact templates to interpret the authority pyramid.

## Handoff To Automation

After the portal classification exercise, rebuild the Day 6 flow:

```bash
uv run python scripts/run_day6_case.py
```
