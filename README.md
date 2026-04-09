# Agentic Accounts Payable Orchestrator

AegisAP is the Golden Thread training repo for Forward Deployed Engineers building
production-ready agentic systems on Azure. The repo follows one invoice case
from Day 0 bootstrap through Day 14, covering observability, regression coverage,
reliability engineering, cost-speed routing controls, gated Azure deployment,
delegated identity, private networking, integration boundaries, MCP, and elite
operational readiness.

## Training Journey

| Day | Objective | New Architectural Layer | Azure Services | Command | Artifact | Exit Check |
| --- | --- | --- | --- | --- | --- | --- |
| Day 0 | Recover the bootstrap contract before the cohort trusts Azure again | Provisioning + RBAC | Microsoft Foundry, Azure AI Search, Blob Storage, optional PostgreSQL, Key Vault, App Insights, Container Apps | `uv run aegisap-lab incident start --day 00 --track core` or `--track full` | `.day0/core.json` or `.day0/full.json` | The selected track can be reloaded from `.day0/<track>.json` and re-verified with `DefaultAzureCredential` |
| Day 1 | Canonicalize invoice intake | Tool-grounded extraction | Azure OpenAI | `uv run aegisap-lab incident start --day 01` | `build/day1/golden_thread_day1.json` | Canonical invoice emitted or rejected deterministically |
| Day 2 | Route a trusted invoice through explicit state | Stateful control flow | Azure OpenAI substrate from Day 0 | `uv run aegisap-lab incident start --day 02` | `build/day2/golden_thread_day2.json` | Workflow state records route, evidence, and recommendations |
| Day 3 | Retrieve evidence and rank authority | Multi-agent retrieval with hostile authority ranking | Azure AI Search, Blob Storage | `uv run aegisap-lab incident start --day 03` | `build/day3/golden_thread_day3.json` | Structured authority outranks stale evidence again |
| Day 4 | Produce and validate execution plans | Explicit planning and fail-closed control | Azure OpenAI, Azure AI Search | `uv run aegisap-lab incident start --day 04` | `build/day4/golden_thread_day4.json` | Combined-risk cases stay manual-review-only |
| Day 5 | Pause, persist, and resume | Durable checkpoints and approval resume | Azure Database for PostgreSQL, Azure OpenAI, Azure AI Search | `uv run aegisap-lab incident start --day 05` | `build/day5/golden_thread_day5_pause.json`, `build/day5/golden_thread_day5_resumed.json` | Approval threads reject stale resume material and avoid duplicate side effects |
| Day 6 | Refuse unsafe or unauthorised progression | Review boundary, authority conflict, and graceful refusal | Azure OpenAI optional, Azure Database for PostgreSQL | `uv run aegisap-lab incident start --day 06` | `build/day6/golden_thread_day6.json` | Unsafe review inputs end in a defended refusal or human review path |
| Day 7 | Repair a guardrail breach before it becomes an audit finding | Redaction boundaries, refusal evidence, eval governance | Managed Identity, Key Vault RBAC, Azure AI Search RBAC, Log Analytics, PostgreSQL audit store | `uv run aegisap-lab incident start --day 07` | `build/day7/eval_report.json` | Sensitive audit evidence is redacted again before persistence |
| Day 8 | Repair runtime identity drift and re-prove least privilege | IaC role assignments, secure release ownership, trace evidence | Application Insights, Azure Monitor, Bicep, GitHub OIDC | `uv run aegisap-lab incident start --day 08` | `build/day8/deployment_design.json`, `build/day8/regression_baseline.json`, `build/day8/checkpoint_trace_extension.json` | Runtime search access is least-privilege again and release evidence is regenerated |
| Day 9 | Repair routing and budget drift before finance notices | Model router, workflow cost ledger, conservative cache | Azure OpenAI deployments, Azure Monitor, Application Insights | `uv run aegisap-lab incident start --day 09` | `build/day9/routing_report.json` | Risky work routes back to the strong tier and cost controls stay intact |
| Day 10 | Establish the Capstone A foundation packet under false-green release pressure | Release envelope integrity, acceptance gates, CAB packet | Azure Container Apps, ACR, Key Vault, Application Insights, GitHub Actions | `uv run aegisap-lab incident start --day 10` | `build/day10/release_envelope.json`, `build/day10/checkpoint_gate_extension.json`, `build/capstone/<trainee_id>/release_packet.json` | Any failing gate blocks the Capstone A foundation packet again |
| Day 11 | Repair delegated identity before authority confusion reaches production | OBO token exchange, actor binding, MSAL token verification | Azure AD, Managed Identity, Azure OpenAI | `uv run aegisap-lab incident start --day 11` | `build/day11/obo_contract.json` | Actor-bound approval only passes when the required group evidence matches the OBO actor |
| Day 12 | Restore private-network truth when the checker goes blind | VNET injection, Private Endpoints, Private DNS, external-sink guard | Azure Virtual Network, Private Endpoints, Private DNS, Azure Container Apps | `uv run aegisap-lab incident start --day 12` | `build/day12/static_bicep_analysis.json`, `build/day12/private_network_posture.json`, `build/day12/external_sink_disabled.json` | Static and live network evidence agree that the AI surface is private-only |
| Day 13 | Recover a governed integration boundary under contract drift | Azure Functions, Service Bus, DLQ compensating actions, MCP contract | Azure Functions (Flex Consumption), Azure Service Bus Premium, Azure Container Apps | `uv run aegisap-lab incident start --day 13` | `build/day13/dlq_drain_report.json`, `build/day13/mcp_contract_report.json`, `build/day13/webhook_reliability_report.json` | The MCP contract exposes the governed write path again and compensating-action evidence is intact |
| Day 14 | Close Capstone A with the final CAB defense, blank-slate drill, and chaos evidence | Canary regression, data residency ARM check, trace correlation, chaos capstone, CTO report | Azure Container Apps, Azure Resource Manager, Application Insights, all prior services | `uv run aegisap-lab incident start --day 14` | `build/day14/canary_regression_report.json`, `build/day14/data_residency_report.json`, `build/day14/trace_correlation_report.json`, `build/day14/breaking_changes_drills.json`, `build/day14/cto_trace_report.json`, `build/capstone/<trainee_id>/final_packet.json` | The elite-ops gates, final CAB packet, blank-slate drill, and chaos evidence all agree on the safe decision |

## Start Here

1. Read [Training Journey](/workspaces/agentic-accounts-payable-orchestrator/docs/TRAINING_JOURNEY.md).
2. Start the Day 0 bootstrap incident with [Day 0 Azure Bootstrap](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_00_AZURE_BOOTSTRAP.md) and `uv run aegisap-lab incident start --day 00 --track core` or `--track full`.
3. Run the golden-thread lab for each day in order.
4. Use [Curriculum Delivery Map](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/DELIVERY_MAP.md) as the single navigation layer for notebook, doc, script, and artifact selection.
5. Use the notebooks for walkthroughs and the scripts for repeatable execution.

## Day Guides

- [Day 0 Azure Bootstrap](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_00_AZURE_BOOTSTRAP.md)
- [Day 1 Intake and Canonicalization](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_01.md)
- [Day 2 Stateful Workflow](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_02.md)
- [Day 3 Retrieval Authority Rescue Mission](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_03.md)
- [Day 4 Fail-Closed Planning Rescue Mission](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_04.md)
- [Day 5 Durable State Rescue Mission](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_05.md)
- [Day 6 Review Boundary Rescue Mission](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_06.md)
- [Day 7 Guardrail Breach Rescue Mission](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_07.md)
- [Day 8 Identity Drift Rescue Mission](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_08.md)
- [Day 9 Routing Regression Rescue Mission](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_09.md)
- [Day 10 Release Board Rescue Mission](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_10.md)
- [Day 11 Delegated Identity Rescue Mission](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_11.md)
- [Day 12 Private Network Rescue Mission](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_12.md)
- [Day 13 Integration Boundary Rescue Mission](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_13.md)
- [Day 14 Chaos Command Rescue Mission](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_14.md)

## Notebooks

- `notebooks/day_0_bootstrap_incident.py`
- `notebooks/day_1_agentic_fundamentals.py`
- `notebooks/day_2_requirements_architecture.py`
- `notebooks/day_3_azure_ai_services.py`
- `notebooks/day_4_single_agent_loops.py`
- `notebooks/day_5_multi_agent_orchestration.py`
- `notebooks/day_6_data_ml_integration.py`
- `notebooks/day_7_testing_eval_guardrails.py`
- `notebooks/day_8_cicd_iac_deployment.py`
- `notebooks/day_9_scaling_monitoring_cost.py`
- `notebooks/day_10_production_operations.py`
- `notebooks/day_11_delegated_identity_obo.py`
- `notebooks/day_12_private_networking_constraints.py`
- `notebooks/day_13_integration_boundary_and_mcp.py`
- `notebooks/day_14_breaking_changes_elite_ops.py`

## Day 0 in 10 Minutes

The recommended bootstrap is devcontainer-first, keyless, and RBAC-based.

1. Open the repo in the devcontainer.
2. Run `az login` and `az account set --subscription <subscription-id>`.
3. Copy `infra/core.bicepparam.example` to `infra/core.bicepparam`.
4. Provision core resources:

```powershell
pwsh ./scripts/provision-core.ps1 `
  -SubscriptionId <subscription-id> `
  -ResourceGroup <resource-group> `
  -Location <azure-region>
```

5. Load the generated state:

```bash
source ./scripts/setup-env.sh core
```

6. Verify the environment:

```bash
uv run python scripts/verify_env.py --track core --env
uv run python scripts/verify_env.py --track core
```

Use the `full` track before Day 5 or before deploying the hosted runtime.

## Azure Deployment Path

The hosted training milestone uses the `full` track and a minimal FastAPI
runtime exposed through Azure Container Apps.

1. Provision `full` track resources.
2. Load the environment with `source ./scripts/setup-env.sh full`.
3. Apply the Day 5 migration:

```bash
uv run python scripts/apply_migrations.py
```

4. Run the Day 6 review gate locally if you want to validate the refusal layer before deployment:

```bash
uv run aegisap-lab artifact rebuild --day 06
```

5. Build and push the API image:

```powershell
pwsh ./scripts/build_and_push_image.ps1 -ImageName aegisap-api -Dockerfile ./docker/Dockerfile.api
```

6. Deploy the staging Container App revision:

```powershell
pwsh ./scripts/deploy_container_app.ps1 -EnvironmentName staging
```

7. Smoke-test the deployed app:

```bash
uv run python scripts/smoke_test.py --base-url https://<container-app-url>
```

Hosted success means a learner can hit `/healthz`, run the Day 4 case, inspect
the Day 6 review outcome, persist Day 5 state to Azure PostgreSQL, resume the
approval flow without duplicate side effects, and confirm that Day 7 has removed
Search key fallback while emitting redacted audit rows.

## Repo Conventions

- `pyproject.toml` and `uv.lock` are the dependency source of truth.
- `fixtures/golden_thread/` is the primary teaching baseline.
- `fixtures/day06/` is the primary adversarial safety baseline.
- `docs/` holds the primary day references for the incident-driven curriculum.
- `tests/day7/` groups the Day 7 security and audit regression suite.
- `build/day*/` contains generated lab artifacts.
- `src/aegisap/api/app.py` is the deployable training runtime.
- Existing unit and integration tests remain the regression baseline.

## Verification

Run the local regression suite:

```bash
uv run python -m pytest -q
```

Run the deployment-free lab path:

```bash
uv run aegisap-lab artifact rebuild --day 01
uv run aegisap-lab artifact rebuild --day 02
uv run aegisap-lab artifact rebuild --day 03
uv run aegisap-lab artifact rebuild --day 04
uv run aegisap-lab artifact rebuild --day 05
uv run aegisap-lab artifact rebuild --day 06
uv run aegisap-lab artifact rebuild --day 07
uv run aegisap-lab artifact rebuild --day 08
uv run aegisap-lab artifact rebuild --day 09
uv run aegisap-lab artifact rebuild --day 10
uv run aegisap-lab artifact rebuild --day 11
uv run aegisap-lab artifact rebuild --day 12
uv run aegisap-lab artifact rebuild --day 13
uv run aegisap-lab artifact rebuild --day 14
```
