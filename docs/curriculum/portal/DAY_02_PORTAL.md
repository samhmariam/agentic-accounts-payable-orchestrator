# Day 02 — Portal-First Architecture Grounding

> **Portal mode:** `Inspect`  
> **Intent:** derive architecture and NFR thinking from the actual Azure topology rather than from diagrams alone.

## Portal-First Outcome

You can use the live Azure estate to justify scope boundaries, ownership
boundaries, and at least one zero-tolerance NFR before writing architecture artifacts.

## Portal Mode

Use the portal as an architecture evidence source. The goal is not to create
resources but to observe topology, ownership, region placement, and IAM surfaces.

## Azure Portal Path

1. Open the resource group overview and record the resource names, locations, and tags.
2. Inspect the deployment history so you can distinguish declared infrastructure from ad hoc portal changes.
3. Open **Access control (IAM)** on two different resources and compare who owns runtime access versus admin access.
4. Inspect the networking, diagnostics, and identity blades of the most important resources and note which settings are likely to become release gates later.
5. If a resource is missing for a planned capability, note it as a scope or dependency finding rather than hand-waving it away.

## What To Capture

- A resource-to-responsibility mapping you can reuse in the Day 2 architecture discussion.
- At least one NFR inferred from portal state, such as region consistency, identity isolation, or missing diagnostics.
- A list of decisions that are already constrained by the current Azure topology.

## Handoff To Notebook

- Open [day_2_requirements_architecture.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_2_requirements_architecture.py).
- Use [DAY_02.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_02.md) and the Day 2 artifact templates in `docs/curriculum/artifacts/day02/` to turn the portal observations into architecture decisions.

## Handoff To Automation

Day 2 is notebook-led and artifact-led rather than script-led. After the portal
pass, use the notebook and write the Day 2 artifacts in
`docs/curriculum/artifacts/day02/`.
