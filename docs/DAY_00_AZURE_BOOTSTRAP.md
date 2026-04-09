# Day 0 - Azure Bootstrap

Primary learner entrypoint: `modules/day_00_bootstrap/README.md`.

Day 0 now begins as a bootstrap incident. Start with:

```bash
uv run aegisap-lab incident start --day 00 --track core
```

or

```bash
uv run aegisap-lab incident start --day 00 --track full
```

Use the portal guide in
[docs/curriculum/portal/DAY_00_PORTAL.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/portal/DAY_00_PORTAL.md)
as an evidence surface inside that incident flow, then return here for the
repeatable, declarative repair path.

## Tracks

- `core`: Microsoft Foundry, Azure AI Search, Blob Storage
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

## Three-Surface Linkage

Use Day 0 as one explicit chain:

1. `Incident first`: start the Day 00 incident for the chosen track.
2. `Portal second`: complete the Day 0 portal walkthrough so the control plane is visible and named.
3. `Middle surface third`: use this bootstrap doc to interpret what those Azure objects mean, which roles matter, and how the repo models them declaratively.
4. `Automation fourth`: run `scripts/provision-core.ps1` or `scripts/provision-full.ps1`, then `scripts/setup-env.sh`, then `scripts/verify_env.py`.
5. `Evidence last`: compare the live portal estate, `.day0/core.json` or `.day0/full.json`, and the verification output. They should all describe the same Foundry-first environment.

## Roles to Expect

- Developer bootstrap identity: `Cognitive Services User` on the Foundry
  resource, `Search Service Contributor`, `Search Index Data Contributor`,
  `Storage Blob Data Contributor`
- Runtime app identity: `Cognitive Services OpenAI User` on the Foundry
  resource for the current OpenAI-compatible inference path,
  `Search Index Data Reader`, `Storage Blob Data Reader`, `Key Vault Secrets User`
- Pull or secret-reference identity: `AcrPull`, `Key Vault Secrets User`
- Search admin identity scaffold: `Search Service Contributor`,
  `Search Index Data Contributor`

## Troubleshooting

- If Foundry inference returns `DeploymentNotFound`, confirm the OpenAI-compatible
  deployment name in the `.bicepparam` file and rerun provisioning.
- If Search returns `403`, confirm the search data-plane roles were assigned on
  the service resource.
- If PostgreSQL verification fails, confirm Microsoft Entra admin setup and the
  `AZURE_POSTGRES_USER` principal.

## Handoff to Day 1

After Day 0 succeeds, the learner should have:

- a reachable Foundry resource with managed identity and project management enabled
- a reachable OpenAI-compatible chat deployment on that Foundry resource
- the Foundry endpoint plus the OpenAI-compatible endpoint exported into `.day0/*.json`
- a reachable Azure AI Search service and index
- a reachable Blob container
- on the full track, a reachable Azure PostgreSQL database for Day 5

From there, move to [Day 1](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_01.md).
