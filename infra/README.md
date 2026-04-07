# Infra Layout

This directory is being refactored toward a layered structure:

- `foundations/`: reusable Azure resource primitives
- `data/`: data and ML service modules
- `capabilities/`: higher-level bundles composed from foundations
- `overlays/`: learner-facing day or milestone wrappers

For compatibility, the current public entrypoints remain:

- `core.bicep`
- `full.bicep`
- `main.bicep`
- `notebook.bicep`

Older paths under `modules/` remain available as shims while callers are
migrated to the new layout.

## Current Notebook Provisioning Model

`azd` currently provisions notebook resources through `infra/notebook.bicep`.
See `azure.yaml`, which points to:

- `path: infra`
- `module: notebook`

The notebook stack is currently mapped by profile or tier, not by a one-file-
per-notebook model.

## Notebook To Bicep Mapping

| Notebook day(s) | Notebook profile | Primary Bicep entrypoint(s) | What it provisions |
|---|---|---|---|
| Days 1-2 | n/a | No notebook-specific Azure provisioning module | Architecture and design days; no dedicated notebook infra tier |
| Days 3-4 | `core` | `infra/core.bicep` | Blob Storage, Azure AI Search, Microsoft Foundry |
| Days 5-7 | `standard` | `infra/notebook_standard.bicep` + `infra/core.bicep` | Adds PostgreSQL, Content Safety, Cosmos DB, Azure Data Factory |
| Days 8-10 | `full` | `infra/notebook_full.bicep` + `standard` + `core` | Adds ACR, Key Vault, ACA environment, Log Analytics, App Insights, Azure ML |
| Days 11-14 | `advanced` | `infra/notebook_advanced.bicep` + `full` + `standard` + `core` | Adds VNet, Private DNS, Private Endpoints, Service Bus |

In `infra/notebook.bicep` this is wired as:

- `coreResources` -> `./core.bicep`
- `standardResources` -> `./notebook_standard.bicep`
- `fullResources` -> `./notebook_full.bicep`
- `advancedResources` -> `./notebook_advanced.bicep`

## Tier Details

### Core

`infra/core.bicep` now wraps the shared foundation modules:

- `infra/foundations/storage.bicep`
- `infra/foundations/search_service.bicep`
- `infra/foundations/foundry_account.bicep`

This is the base retrieval substrate used by Days 3-4 and inherited by all
higher notebook profiles.

### Standard

`infra/notebook_standard.bicep` currently provisions PostgreSQL inline and uses
these module paths:

- `infra/modules/content_safety.bicep`
- `infra/modules/cosmos_db.bicep`
- `infra/modules/adf.bicep`

Those `infra/modules/*` paths are compatibility shims and now forward to the
newer modules under `infra/data/`.

### Full

`infra/notebook_full.bicep` provisions:

- Log Analytics
- Application Insights
- Azure Container Registry
- Key Vault
- Container Apps environment
- three user-assigned managed identities
- Azure Machine Learning via `infra/modules/azure_ml.bicep`

`infra/modules/azure_ml.bicep` is also a compatibility shim and now forwards to
`infra/data/azure_ml.bicep`.

### Advanced

`infra/notebook_advanced.bicep` currently uses:

- `infra/network/vnet.bicep`
- `infra/network/private_dns.bicep`
- `infra/network/private_endpoints.bicep`

It also defines Service Bus inline for the current training flow.

## Important Nuances

- Day 11 is only partially represented in Bicep. The delegated identity and
  OBO parts are mostly Entra and application configuration work outside the
  current ARM stack.
- Day 12 conceptually relates to `infra/network/private_aca.bicep`, but the
  current notebook stack does not yet wire that module into `notebook.bicep`.
- Day 13 conceptually relates to `infra/integration/service_bus.bicep` and
  `infra/integration/function_app.bicep`, but the current notebook profile path
  still provisions Service Bus inline inside `infra/notebook_advanced.bicep`.

## Non-Notebook Entry Points

The repo also keeps broader Day 0 bootstrap entrypoints:

- `infra/core.bicep`: minimal shared platform for early days with a Foundry-first baseline
- `infra/full.bicep`: expanded shared platform for later days

Those are used by scripts such as:

- `scripts/provision-core.ps1`
- `scripts/provision-full.ps1`

They are not the same thing as the notebook-profile stack, but they provision
overlapping resource sets and are referenced throughout the curriculum.
