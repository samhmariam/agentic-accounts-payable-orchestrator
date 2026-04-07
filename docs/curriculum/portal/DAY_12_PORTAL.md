# Day 12 — Portal-First Private Networking

> **Portal mode:** `Inspect`  
> **Intent:** prove the data plane is really private from Azure state before trusting static analysis or notebook claims.

## Portal-First Outcome

You can show public access is disabled, private endpoints are approved, and the
approved DNS and VNET path exists for the services that matter.

## Portal Mode

This is a posture-verification day. Use the portal as the ground truth for the
network state, then compare it with the repo’s static and live probes.

## Azure Portal Path

1. Open Foundry, Azure AI Search, Storage, and PostgreSQL resource blades and confirm **Public network access** is disabled.
2. Inspect **Private endpoint connections** on each service and confirm the state is approved.
3. Open **Private DNS zones** and inspect the VNET links that make private resolution possible.
4. Open the Container Apps environment and inspect networking to confirm VNET injection and no accidental public fallback.
5. Note any service whose network posture looks different from the intended private-only model.

## What To Capture

- Public-access posture for each critical service.
- One approved private endpoint connection per critical dependency.
- One DNS or VNET linkage proving why the private path should work.

## Three-Surface Linkage

- `Portal`: inspect public access, private endpoints, DNS, and networking directly in Azure so private-only posture is concrete.
- `Notebook`: open [day_12_private_networking_constraints.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_12_private_networking_constraints.py) and use the static-versus-live sections to explain why intent proof and live posture proof are different.
- `Automation`: run `scripts/check_private_network_static.py`, `scripts/verify_private_network_posture.py`, and the Day 12 test path after the Azure network story is already visible.
- `Evidence`: portal posture, notebook reasoning, and `build/day12/static_bicep_analysis.json` plus `build/day12/private_network_posture.json` should all support the same private-only claim.

## Handoff To Notebook

- Open [day_12_private_networking_constraints.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_12_private_networking_constraints.py).
- Use [DAY_12_PRIVATE_NETWORKING.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_12_PRIVATE_NETWORKING.md) and the Day 12 artifact templates to interpret the network evidence.

## Handoff To Automation

After the portal posture check, run the repo’s intent and live probes:

```bash
uv run python scripts/check_private_network_static.py --json
uv run python scripts/verify_private_network_posture.py
uv run python -m pytest tests/day12 -q
```
