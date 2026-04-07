# Day 14 — Portal-First Elite Operations

> **Portal mode:** `Operate`  
> **Intent:** make the final rollout and incident decisions from Azure evidence first, then use repo automation to formalize that judgment.

## Portal-First Outcome

You can defend the final canary, rollback, residency, and trace-correlation story
from Azure state without leaning on notebook prose or local reports alone.

## Portal Mode

This is the strongest `Operate` day in the curriculum. Azure is the first source
of truth for the decision; scripts and artifacts come second.

## Azure Portal Path

1. Open the Container App and inspect **Revisions** and traffic weights so the canary or stable state is visible.
2. Open Application Insights or Log Analytics and locate the candidate workflow run and deployment revision in live telemetry.
3. Inspect the AI resources and confirm location and private-network posture align with the claims you are about to make.
4. Cross-check the final evidence pack against portal truth: traffic, traces, location, and network posture must all agree.
5. Decide whether the Azure evidence supports continue, hold, or rollback before running the final reporting scripts.

## What To Capture

- Canary or stable traffic state from Azure.
- One telemetry view linking the revision to a real workflow run.
- One location or networking proof point tied to the release decision.
- A one-sentence go/no-go judgment made before consulting the final generated report.

## Three-Surface Linkage

- `Portal`: inspect canary traffic, telemetry, residency, and network posture in Azure before any final script runs.
- `Notebook`: open [day_14_breaking_changes_elite_ops.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_14_breaking_changes_elite_ops.py) and use the drill, canary, rollback, residency, and trace sections to interpret the Azure evidence.
- `Automation`: run the Day 14 verification and reporting scripts only after you already have an Azure-first operating judgment.
- `Evidence`: the portal decision, notebook reasoning, and the Day 14 verification reports should all align before the final CTO report is treated as trustworthy.

## Handoff To Notebook

- Open [day_14_breaking_changes_elite_ops.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_14_breaking_changes_elite_ops.py).
- Use [DAY_14_BREAKING_CHANGES.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_14_BREAKING_CHANGES.md) and the Day 14 artifact templates to turn Azure evidence into executive communication.

## Handoff To Automation

After making the Azure-first judgment, write the formal evidence with the repo:

```bash
uv run python scripts/verify_canary_regression.py
uv run python scripts/verify_trace_correlation.py
uv run python scripts/verify_private_network_static.py
uv run python scripts/generate_cto_trace_report.py
uv run python -m pytest tests/day14 -q
```
