# Day 0 - Azure Bootstrap

Day 0 establishes the Azure substrate that every later lab assumes. The default
goal is a keyless developer experience built on `DefaultAzureCredential`.

## Tracks

- `core`: Azure OpenAI, Azure AI Search, Blob Storage
- `full`: core services plus Azure Database for PostgreSQL, Key Vault,
  Application Insights, ACR, Container Apps environment, and managed identity

## Recommended Sequence

1. Open the repo in the devcontainer.
2. Run `az login`.
3. Select the subscription with `az account set --subscription <subscription-id>`.
4. Copy the relevant parameter file:

```bash
cp infra/core.bicepparam.example infra/core.bicepparam
```

or

```bash
cp infra/full.bicepparam.example infra/full.bicepparam
```

5. Provision the target track:

```powershell
pwsh ./scripts/provision-core.ps1 `
  -SubscriptionId <subscription-id> `
  -ResourceGroup <resource-group> `
  -Location <azure-region>
```

or

```powershell
pwsh ./scripts/provision-full.ps1 `
  -SubscriptionId <subscription-id> `
  -ResourceGroup <resource-group> `
  -Location <azure-region>
```

6. Load the generated state:

```bash
source ./scripts/setup-env.sh core
```

or

```bash
source ./scripts/setup-env.sh full
```

7. Verify:

```bash
uv run python scripts/verify_env.py --track core
```

or

```bash
uv run python scripts/verify_env.py --track full
```

## Roles to Expect

- Runtime app identity: `Cognitive Services OpenAI User`,
  `Search Index Data Reader`, `Storage Blob Data Reader`, `Key Vault Secrets User`
- Pull or secret-reference identity: `AcrPull`, `Key Vault Secrets User`
- Search admin identity scaffold: `Search Service Contributor`,
  `Search Index Data Contributor`
- Developer principal: bootstrap contributor roles for Day 0 setup and index seeding

## Troubleshooting

- If Azure OpenAI returns `DeploymentNotFound`, confirm the deployment name in
  the `.bicepparam` file and rerun provisioning.
- If Search returns `403`, confirm the search data-plane roles were assigned on
  the service resource.
- If PostgreSQL verification fails, confirm Microsoft Entra admin setup and the
  `AZURE_POSTGRES_USER` principal.

## Handoff to Day 1

After Day 0 succeeds, the learner should have:

- a reachable Azure OpenAI chat deployment
- a reachable Azure AI Search service and index
- a reachable Blob container
- on the full track, a reachable Azure PostgreSQL database for Day 5

From there, move to [Day 1](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_01.md).
