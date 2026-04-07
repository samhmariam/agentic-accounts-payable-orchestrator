# Day 08 — Portal-First Deployment Surfaces

> **Portal mode:** `Operate`  
> **Intent:** inspect the deployed platform in Azure before you let scripts or IaC outputs speak for it.

## Portal-First Outcome

You can validate the live deployment, identity, and secret surfaces in Azure and
then explain how the repo abstracts those same checks.

## Portal Mode

Day 8 is an operations day, not a portal hotfix day. Inspect the live estate and
use the portal as evidence, not as the source of configuration changes.

## Azure Portal Path

1. Open the resource group and inspect **Deployments** to connect Bicep history to live state.
2. Open the Container App and inspect **Revisions**, **Ingress**, and **Identity**.
3. Open **Access control (IAM)** on Foundry, Azure AI Search, Storage, and Key Vault and compare the runtime identity to the release or developer identities.
4. Open Key Vault and confirm only residual secrets are stored there, not public endpoints or configuration values.
5. Note any mismatch between portal state and the infrastructure story you expect from Day 8.

## What To Capture

- Deployment history entry that corresponds to the current environment.
- Container App revision, ingress, and identity state.
- One least-privilege role chain from runtime identity to Azure dependency.
- One example of configuration that should not be stored in Key Vault.

## Three-Surface Linkage

- `Portal`: inspect deployments, Container App revisions, IAM, and Key Vault so the live platform is visible in Azure first.
- `Notebook`: open [day_8_cicd_iac_deployment.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_8_cicd_iac_deployment.py) and use the IaC, identity, and release sections to explain why that Azure state is safe.
- `Automation`: use `scripts/verify_env.py`, `scripts/provision-full.ps1`, `scripts/deploy_container_app.ps1`, and the Day 8 test path after the platform model is already clear.
- `Evidence`: portal deployment history, notebook reasoning, and `build/day8/deployment_design.json` plus `build/day8/regression_baseline.json` should reinforce the same deployment contract.

## Handoff To Notebook

- Open [day_8_cicd_iac_deployment.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_8_cicd_iac_deployment.py).
- Use [DAY_08_IAC_IDENTITY_RELEASE_OWNERSHIP.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_08_IAC_IDENTITY_RELEASE_OWNERSHIP.md) to connect Azure state to release ownership and drift control.

## Handoff To Automation

Use the automation only after you can defend the live platform from the portal:

```bash
uv run python scripts/verify_env.py --track full
pwsh ./scripts/provision-full.ps1 -SubscriptionId "$AZURE_SUBSCRIPTION_ID" -ResourceGroup "$AZURE_RESOURCE_GROUP" -Location "$AZURE_LOCATION"
pwsh ./scripts/deploy_container_app.ps1 -EnvironmentName staging
uv run python -m pytest tests/day8 -q
```
