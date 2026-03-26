# Agentic Accounts Payable Orchestrator

AegisAP is the Golden Thread training repo for Forward Deployed Engineers building
production-ready agentic systems on Azure. The repo follows one invoice case
from Day 0 bootstrap through Day 5 durable approval resume.

## Training Journey

| Day | Objective | New Architectural Layer | Azure Services | Command | Artifact | Exit Check |
| --- | --- | --- | --- | --- | --- | --- |
| Day 0 | Bootstrap a keyless Azure substrate | Provisioning + RBAC | Azure OpenAI, Azure AI Search, Blob Storage, optional PostgreSQL, Key Vault, App Insights, Container Apps | `uv run python scripts/verify_env.py --track core` or `--track full` | `.day0/core.json` or `.day0/full.json` | Azure services reachable with `DefaultAzureCredential` |
| Day 1 | Canonicalize invoice intake | Tool-grounded extraction | Azure OpenAI | `uv run python scripts/run_day1_intake.py --mode fixture` or `--mode live` | `build/day1/golden_thread_day1.json` | Canonical invoice emitted or rejected deterministically |
| Day 2 | Route a trusted invoice through explicit state | Stateful control flow | Azure OpenAI substrate from Day 0 | `uv run python scripts/run_day2_workflow.py --day1-artifact build/day1/golden_thread_day1.json --known-vendor` | `build/day2/golden_thread_day2.json` | Workflow state records route, evidence, and recommendations |
| Day 3 | Retrieve evidence and rank authority | Multi-agent retrieval with live enterprise search | Azure AI Search, Blob Storage | `uv run python scripts/run_day3_case.py --retrieval-mode azure_search_live` | `build/day3/golden_thread_day3.json` | Live Search evidence is surfaced and authority-ranked correctly |
| Day 4 | Produce and validate execution plans | Explicit planning and controlled execution | Azure OpenAI, Azure AI Search | `uv run python scripts/run_day4_case.py --planner-mode fixture` or `--planner-mode azure_openai` | `build/day4/golden_thread_day4.json` | Typed plan validates and yields recommendation or escalation |
| Day 5 | Pause, persist, and resume | Durable checkpoints and approval resume | Azure Database for PostgreSQL, Azure OpenAI, Azure AI Search | `uv run python scripts/run_day5_pause_resume.py` then `uv run python scripts/resume_day5_case.py` | `build/day5/golden_thread_day5_pause.json`, `build/day5/golden_thread_day5_resumed.json` | Approval thread resumes without duplicate side effects |

## Start Here

1. Read [Training Journey](/workspaces/agentic-accounts-payable-orchestrator/docs/TRAINING_JOURNEY.md).
2. Provision Azure with [Day 0 Azure Bootstrap](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_00_AZURE_BOOTSTRAP.md).
3. Run the golden-thread lab for each day in order.
4. Use the notebooks for walkthroughs and the scripts for repeatable execution.

## Day Guides

- [Day 0 Azure Bootstrap](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_00_AZURE_BOOTSTRAP.md)
- [Day 1 Intake and Canonicalization](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_01.md)
- [Day 2 Stateful Workflow](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_02.md)
- [Day 3 Retrieval and Authority](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_03_MULTI_AGENT_RETRIEVAL.md)
- [Day 4 Explicit Planning](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_04_EXPLICIT_PLANNING.md)
- [Day 5 Durable State and Resumption](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_05_DURABLE_STATE_AND_RESUMPTION.md)

## Notebooks

- `notebooks/day1_intake_and_canonicalization.ipynb`
- `notebooks/day2_stateful_workflow_orchestration.ipynb`
- `notebooks/day3_multi_agent_retrieval_and_authority.ipynb`
- `notebooks/day4_explicit_planning_and_controlled_execution.ipynb`
- `notebooks/day5_durable_state_and_resumption.ipynb`

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

4. Build and push the image:

```powershell
pwsh ./scripts/build_and_push_image.ps1
```

5. Deploy the Container App:

```powershell
pwsh ./scripts/deploy_container_app.ps1
```

6. Smoke-test the deployed app:

```bash
uv run python scripts/smoke_deployed_app.py --base-url https://<container-app-url>
```

Hosted success means a learner can hit `/healthz`, run the Day 4 case, persist
Day 5 state to Azure PostgreSQL, and resume the approval flow without duplicate
side effects.

## Repo Conventions

- `pyproject.toml` and `uv.lock` are the dependency source of truth.
- `fixtures/golden_thread/` is the primary teaching baseline.
- `build/day*/` contains generated lab artifacts.
- `src/aegisap/api/app.py` is the deployable training runtime.
- Existing unit and integration tests remain the regression baseline.

## Verification

Run the local regression suite:

```bash
pytest -q
```

Run the deployment-free lab path:

```bash
uv run python scripts/run_day1_intake.py
uv run python scripts/run_day2_workflow.py --day1-artifact build/day1/golden_thread_day1.json --known-vendor
uv run python scripts/run_day3_case.py --retrieval-mode fixture
uv run python scripts/run_day4_case.py --planner-mode fixture
```

## Days 6-10

Days 6-10 are intentionally reserved for future curriculum expansion:
graceful refusal, security hardening, observability and regression, cost/speed
optimization, and production deployment hardening.
