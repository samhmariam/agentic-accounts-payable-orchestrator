# Day 00 — Portal Investigation for the Bootstrap Incident

> **Portal mode:** `Configure`  
> **Intent:** use the Azure control plane as evidence while recovering the Day 0 bootstrap contract.

## Portal-First Outcome

You can point to the Day 0 Azure resources in the portal, explain why each
exists, and describe which exact Bicep or script step later recreates it.

## Portal Mode

Use Day 0 to inspect the smallest possible training substrate while recovering
the state-file and verification contract. For repeatability, Bicep remains the
source of truth.

## Azure Portal Path

1. Select the correct subscription and create or inspect the training resource group.
2. Create or inspect the Microsoft Foundry resource and confirm `kind = AIServices`, managed identity, and project-management support are enabled.
3. Open the model deployment surface and create or inspect the OpenAI-compatible deployment the repo expects.
4. Create or inspect the Azure AI Search service and confirm the region and pricing tier match the training plan.
5. Create or inspect the Storage account and blob container used for training fixtures or supporting state.
6. On the `full` track, inspect Key Vault, PostgreSQL Flexible Server, ACR, Container Apps environment, and Application Insights so later days are not abstract names.
7. Open **Access control (IAM)** on the Foundry and Search resources and identify which roles belong to the developer bootstrap identity and which belong to the runtime identity.

## What To Capture

- Resource group name, region, and tag set.
- Foundry resource identity settings and deployment name.
- Search service name, endpoint, and data-plane access model.
- Storage account and container names.
- On the `full` track, one screenshot or note per added service showing its purpose and identity boundary.

## Three-Surface Linkage

- `Portal`: manually create or inspect the Day 0 resource group, Foundry account, deployment, Search service, Storage account, and the `full` track resources so the Azure control plane is concrete before automation.
- `Notebook or middle surface`: Day 0 is currently doc-led, not notebook-led. Use [DAY_00_AZURE_BOOTSTRAP.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_00_AZURE_BOOTSTRAP.md) as the interpretation layer that explains what each Azure step means and why the repo provisions it that way.
- `Automation`: run `scripts/provision-core.ps1` or `scripts/provision-full.ps1`, then `scripts/setup-env.sh`, then `scripts/verify_env.py`.
- `Evidence`: the live portal estate, `.day0/core.json` or `.day0/full.json`, and the verification output should all describe the same Azure substrate.

## Handoff To Notebook

- Day 0 does not begin with a notebook. Start with [DAY_00_AZURE_BOOTSTRAP.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_00_AZURE_BOOTSTRAP.md).
- Use [DAY_00_TRAINEE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainee/DAY_00_TRAINEE.md) and [DAY_00_TRAINER.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainer/DAY_00_TRAINER.md) to connect the portal work to identity, IaC, and zero-secret runtime principles.

## Handoff To Automation

Use the repo only after you can name the resources and roles manually:

```bash
pwsh ./scripts/provision-core.ps1 -SubscriptionId <subscription-id> -ResourceGroup <resource-group> -Location <azure-region>
source ./scripts/setup-env.sh core
uv run python scripts/verify_env.py --track core
```

For the `full` track, use `scripts/provision-full.ps1`, `scripts/setup-env.sh full`,
and `uv run python scripts/verify_env.py --track full`.
