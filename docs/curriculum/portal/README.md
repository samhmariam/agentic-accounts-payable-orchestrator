# Portal-First Delivery Guides

This folder is the manual-first Azure layer for the AegisAP curriculum.

Use it when you want learners to build the Azure mental model from the control
plane first, then return to the notebook and finally to the repo automation.

## Working Order

Use the same sequence every day:

1. Open the day guide in `docs/curriculum/portal/`.
2. Complete the manual Azure step for that day.
3. Capture the evidence listed in the guide.
4. Return to the notebook and primary day doc.
5. Only then use scripts or modules to see how the repo abstracts the same work.

This preserves the learner's attention on Azure concepts before they are hidden
behind automation.

## Portal Modes

Each day uses one of three portal modes:

- `Configure`: manually create or change a bounded Azure surface so the learner understands what the automation later provisions.
- `Inspect`: manually inspect live Azure state before reading the notebook or scripts that rely on it.
- `Operate`: use Azure evidence to make or validate an operational decision before trusting a local artifact or command output.

Not every day should mutate Azure resources. For later days, portal-first often
means inspecting or operating from Azure, not hand-configuring production state.

## Day Matrix

| Day | Portal mode | Main Azure surfaces |
|---|---|---|
| 00 | `Configure` | Foundry, Search, Storage, Key Vault, PostgreSQL, Container Apps |
| 01 | `Inspect` | Resource group inventory, Foundry deployment, identity surfaces |
| 02 | `Inspect` | Tags, IAM, locations, deployment history, topology |
| 03 | `Configure` | Azure AI Search index, IAM, semantic config |
| 04 | `Inspect` | Foundry deployment, Search, app-vs-Azure boundary |
| 05 | `Inspect` | PostgreSQL, Key Vault, runtime identity dependencies |
| 06 | `Inspect` | Data authority surfaces, ADF/Cosmos/ML create blades or live resources |
| 07 | `Inspect` | IAM, Key Vault, monitoring, Content Safety design surface |
| 08 | `Operate` | Deployments, ACA revisions, IAM, Key Vault |
| 09 | `Operate` | Application Insights, Log Analytics, metrics, ACA scale |
| 10 | `Operate` | ACA revisions, traffic, health, release evidence |
| 11 | `Inspect` | Entra app registrations, enterprise apps, groups, audit logs |
| 12 | `Inspect` | Private endpoints, private DNS, ACA networking, public access flags |
| 13 | `Operate` | Boundary host, Service Bus, DLQ, monitoring, MCP host |
| 14 | `Operate` | ACA traffic, telemetry, residency and network posture evidence |

## Evidence Rule

Every portal-first pass should leave behind concrete evidence:

- the exact Azure blade or object inspected
- the state observed there
- the notebook section that interprets that state
- the script or module that later automates or verifies it

If a learner cannot explain that chain, the portal pass did not do its job.

## Navigation

- Use [DELIVERY_MAP.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/DELIVERY_MAP.md) for the day-by-day repo map.
- Use [README.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/README.md) for the full curriculum contract.
- Use `DAY_XX_PORTAL.md` in this folder as the entrypoint before the notebook for that day.
