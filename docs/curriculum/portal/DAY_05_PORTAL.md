# Day 05 — Portal-First Durable State

> **Portal mode:** `Inspect`  
> **Intent:** make checkpointing, persistence, and human approval dependencies visible in Azure before they disappear behind LangGraph helpers.

## Portal-First Outcome

You can point to the Azure resources that make pause, resume, and state recovery
possible and explain which parts of the safety story are infrastructure versus workflow design.

## Portal Mode

Inspect the state and identity dependencies. This is not a portal mutation day.

## Azure Portal Path

1. Open PostgreSQL Flexible Server and inspect the server, database, networking posture, and Microsoft Entra admin configuration.
2. Inspect the identity path that lets the runtime reach PostgreSQL without falling back to passwords.
3. Open Key Vault if the track uses residual secrets for resume-token helpers or external integrations.
4. If Container Apps or jobs exist, inspect the identity attached to the runtime surface that will later use the checkpoint store.
5. Note which parts of the pause/resume flow do not live in Azure: resume-token semantics, approval state, and replay safety rules.

## What To Capture

- PostgreSQL server name, auth model, and network posture.
- The identity that is allowed to reach the state store.
- A short dependency chain from `workflow pause` to `checkpoint exists` to `resume is safe`.

## Handoff To Notebook

- Open [day_5_multi_agent_orchestration.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_5_multi_agent_orchestration.py).
- Use [DAY_05_DURABLE_STATE_AND_RESUMPTION.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_05_DURABLE_STATE_AND_RESUMPTION.md) to connect the state store you inspected to the workflow contract.

## Handoff To Automation

After the portal pass, run the resumable workflow path:

```bash
uv run python scripts/run_day5_pause_resume.py
uv run python scripts/resume_day5_case.py
```
