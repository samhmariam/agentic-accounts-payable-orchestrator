# Agentic Accounts Payable Orchestrator

Day 0 should get engineers to Day 1 with the fewest moving parts possible. In this repo that means a default `core` track for Azure OpenAI, Azure AI Search, and Blob Storage, plus an optional `full` track for the broader platform.

## Recommended Day 0

The recommended path is devcontainer-first and keyless end to end. It assumes:

- you run `az login` inside the devcontainer or local shell
- `DefaultAzureCredential` provides all Azure auth
- no service keys, connection strings, or database passwords are committed or required for the default flow

### 10-minute quickstart

1. Open the repo in the devcontainer.

   The container creates `.venv`, installs the repo dependencies with `uv`, and installs Bicep.

2. Authenticate to Azure and select the subscription.

   ```bash
   az login
   az account set --subscription <subscription-id>
   az account show
   ```

3. Copy the core parameter template and fill in the placeholders.

   ```bash
   cp infra/core.bicepparam.example infra/core.bicepparam
   ```

   `infra/core.bicepparam` must include:

   - resource names for Storage, Search, and Azure OpenAI
   - `openAiChatDeploymentName`
   - `openAiChatModelName` and `openAiChatModelVersion` if the deployment does not already exist
   - a unique Azure OpenAI resource name, because the deployment uses that same value as the required custom subdomain for Microsoft Entra token auth

4. Provision the core Day 0 resources.

   ```powershell
   pwsh ./scripts/provision-core.ps1 `
     -SubscriptionId <subscription-id> `
     -ResourceGroup <resource-group> `
     -Location <azure-region>
   ```

   This script:

   - deploys Azure OpenAI, Azure AI Search, and Blob Storage
   - applies the local developer RBAC roles
   - configures Azure OpenAI with a custom subdomain so keyless Microsoft Entra auth works against the account endpoint
   - creates the named OpenAI chat deployment if model settings are supplied
   - creates the starter Search index if it does not already exist
   - writes local state to `.day0/core.json`

5. Load the local environment from the generated Day 0 state file.

   In `bash`:

   ```bash
   source ./scripts/setup-env.sh core
   ```

   In PowerShell:

   ```powershell
   . ./scripts/setup-env.ps1 -Track core
   ```

6. Verify the environment.

   ```bash
   uv run python scripts/verify_env.py --track core --env
   uv run python scripts/verify_env.py --track core
   ```

## What Day 1 Assumes

Day 1 assumes only this substrate exists:

- one reachable Azure OpenAI chat deployment
- one reachable Azure AI Search service with the target starter index
- one reachable Blob Storage account with the source container

That is enough to start agent behavior, retrieval wiring, and document handling. PostgreSQL, Key Vault, telemetry, registry, and runtime hosting are intentionally deferred out of the recommended path.

## Tracks

### Core track

Use the `core` track when the goal is a fast, low-friction bootstrap.

- Infra: `infra/core.bicep`
- Param template: `infra/core.bicepparam.example`
- Provisioning: `scripts/provision-core.ps1`
- Setup in bash: `source ./scripts/setup-env.sh core`
- Setup in PowerShell: `. ./scripts/setup-env.ps1 -Track core`
- Verification: `uv run python scripts/verify_env.py --track core`

Core resource providers:

- `Microsoft.CognitiveServices`
- `Microsoft.Search`
- `Microsoft.Storage`

### Full track

Use the `full` track only when you need the broader Azure platform on Day 0.

- Infra: `infra/full.bicep`
- Param template: `infra/full.bicepparam.example`
- Provisioning: `scripts/provision-full.ps1`
- Setup in bash: `source ./scripts/setup-env.sh full`
- Setup in PowerShell: `. ./scripts/setup-env.ps1 -Track full`
- Verification: `uv run python scripts/verify_env.py --track full`

The full track adds:

- PostgreSQL Flexible Server with Microsoft Entra auth
- Key Vault in RBAC mode
- Application Insights and Log Analytics
- Container Registry
- Container Apps environment
- user-assigned managed identity

Full-track-only resource providers:

- `Microsoft.DBforPostgreSQL`
- `Microsoft.KeyVault`
- `Microsoft.ContainerRegistry`
- `Microsoft.App`
- `Microsoft.Insights`
- `Microsoft.OperationalInsights`
- `Microsoft.ManagedIdentity`

## Local Workflow

### Devcontainer

The repo is optimized for the provided devcontainer:

- Python 3.12
- Azure CLI
- Bicep
- PowerShell 7
- `uv`
- Docker tooling

The container uses the workspace `.venv` as the default interpreter, matching the README commands and `scripts/verify_env.py`.

### State files and setup

Provisioning writes local, ignored state files:

- `.day0/core.json`
- `.day0/full.json`

`scripts/setup-env.ps1` reads those files and exports the non-secret environment variables into the current PowerShell process. It does not fetch keys, admin keys, storage connection strings, or PostgreSQL passwords, and it does not overwrite `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, or `AZURE_CLIENT_SECRET`.

`scripts/setup-env.sh` does the same for the current `bash` process, which is the recommended path when running `uv run ...` commands from the devcontainer terminal.

The generated environment also includes `AZURE_SEARCH_DAY3_INDEX` for the dedicated Day 3 live-retrieval index.

### `.env.example`

`.env.example` documents the resulting environment contract for both tracks, but it is not the primary bootstrap path. The preferred flow is provision -> setup-env -> verify.

## Security Baseline

Day 0 defaults in this repo:

- use `az login` locally and managed identity in Azure-hosted workloads
- use RBAC-enabled data-plane access instead of service keys
- keep Azure OpenAI and Search local auth disabled
- keep Storage shared-key auth disabled
- keep PostgreSQL password auth disabled in the full track
- do not commit populated `.bicepparam`, `.env`, or `.day0` files

Useful local development roles:

- Azure OpenAI: `Cognitive Services OpenAI User`
- Azure AI Search: `Search Service Contributor` and `Search Index Data Contributor`
- Blob Storage: `Storage Blob Data Contributor`
- Key Vault in the full track: `Key Vault Secrets User`

## Verification

`scripts/verify_env.py` is track-aware:

- `--track core` checks Azure OpenAI, Azure AI Search, and Blob Storage
- `--track full` checks the core services plus PostgreSQL, Key Vault, and Application Insights
- `--env` validates only the environment variables for the selected track
- `--include-langsmith` enables the optional LangSmith check

The default Day 0 success condition is:

- `uv run python scripts/verify_env.py --track core` completes without failures

Optional Day 3 live retrieval follow-up:

- `python scripts/ingest_day3_search_docs.py` indexes the Day 3 unstructured evidence into the dedicated Search index
- `python scripts/verify_day3_live_retrieval.py` runs one live Day 3 smoke case against Azure AI Search

Full-track success adds:

- `uv run python scripts/verify_env.py --track full` completes without failures

## Compatibility Notes

- `scripts/provision.ps1` now aliases the recommended `core` bootstrap.
- `infra/main.bicep` remains as a compatibility wrapper to the core template.
- If you need the broader platform, use the explicit `full` files and scripts instead of the compatibility aliases.

## References

- Azure resource providers and Azure services: <https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-services-resource-providers>
- Azure OpenAI keyless connections: <https://learn.microsoft.com/en-us/azure/developer/ai/keyless-connections>
- Azure AI Search RBAC client connections: <https://learn.microsoft.com/en-us/azure/search/search-security-rbac-client-code>
- Azure Storage auth with Microsoft Entra ID: <https://learn.microsoft.com/en-us/azure/storage/blobs/authorize-access-azure-active-directory>
- Azure Database for PostgreSQL Flexible Server Microsoft Entra auth: <https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/security-entra-configure>
- Azure Key Vault authentication: <https://learn.microsoft.com/en-us/azure/key-vault/general/authentication>
- Azure Monitor OpenTelemetry overview: <https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-overview>
