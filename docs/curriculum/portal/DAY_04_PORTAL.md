# Day 04 — Portal-First Boundary Ownership

> **Portal mode:** `Inspect`  
> **Intent:** distinguish what Azure owns from what the application owns before the planner and policy overlay are hidden behind code.

## Portal-First Outcome

You can name which Day 4 concerns are handled by Azure services and which remain
application-level responsibilities such as schema validation, planning, and fail-closed policy.

## Portal Mode

Day 4 is not a portal build day. It is a portal boundary day: inspect the cloud
surfaces, then identify what Azure does not do for you.

## Azure Portal Path

1. Open the Foundry resource and inspect the model deployment that backs the extraction or planning surface.
2. Open Azure AI Search and inspect the retrieval surface that feeds the planner.
3. If runtime hosting exists, open the application host and note what Azure can show you about invocation, identity, and configuration.
4. Write down which Day 4 controls do not appear anywhere in the portal: canonicalization, policy precedence, refusal logic, and risk classification.
5. Compare the portal-visible resources to the notebook's planner and policy sections so you can see the application boundary clearly.

## What To Capture

- A two-column list: `Azure-managed surface` versus `application-owned control`.
- One example of a failure Azure can detect for you and one failure only the application can prevent.
- The model deployment name and search resource used by the planner path.

## Handoff To Notebook

- Open [day_4_single_agent_loops.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_4_single_agent_loops.py).
- Use [DAY_04_EXECUTION_FLOW.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_04_EXECUTION_FLOW.md) to connect the portal surfaces to the policy overlay and fail-closed plan flow.

## Handoff To Automation

Once the control split is clear, rebuild the flow through the repo:

```bash
uv run python scripts/run_day4_case.py --planner-mode fixture
```
