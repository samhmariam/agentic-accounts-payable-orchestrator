# Agentic Accounts Payable Orchestrator

AegisAP is the Golden Thread training repo for Forward Deployed Engineers building
production-ready agentic systems on Azure. The repo follows one invoice case
from Day 0 bootstrap through Day 9 observability, regression coverage,
reliability engineering, and explicit cost-speed routing controls.

## Training Journey

| Day | Objective | New Architectural Layer | Azure Services | Command | Artifact | Exit Check |
| --- | --- | --- | --- | --- | --- | --- |
| Day 0 | Bootstrap a keyless Azure substrate | Provisioning + RBAC | Azure OpenAI, Azure AI Search, Blob Storage, optional PostgreSQL, Key Vault, App Insights, Container Apps | `uv run python scripts/verify_env.py --track core` or `--track full` | `.day0/core.json` or `.day0/full.json` | Azure services reachable with `DefaultAzureCredential` |
| Day 1 | Canonicalize invoice intake | Tool-grounded extraction | Azure OpenAI | `uv run python scripts/run_day1_intake.py --mode fixture` or `--mode live` | `build/day1/golden_thread_day1.json` | Canonical invoice emitted or rejected deterministically |
| Day 2 | Route a trusted invoice through explicit state | Stateful control flow | Azure OpenAI substrate from Day 0 | `uv run python scripts/run_day2_workflow.py --day1-artifact build/day1/golden_thread_day1.json --known-vendor` | `build/day2/golden_thread_day2.json` | Workflow state records route, evidence, and recommendations |
| Day 3 | Retrieve evidence and rank authority | Multi-agent retrieval with live enterprise search | Azure AI Search, Blob Storage | `uv run python scripts/run_day3_case.py --retrieval-mode azure_search_live` | `build/day3/golden_thread_day3.json` | Live Search evidence is surfaced and authority-ranked correctly |
| Day 4 | Produce and validate execution plans | Explicit planning and controlled execution | Azure OpenAI, Azure AI Search | `uv run python scripts/run_day4_case.py --planner-mode fixture` or `--planner-mode azure_openai` | `build/day4/golden_thread_day4.json` | Typed plan validates and yields recommendation or escalation |
| Day 5 | Pause, persist, and resume | Durable checkpoints and approval resume | Azure Database for PostgreSQL, Azure OpenAI, Azure AI Search | `uv run python scripts/run_day5_pause_resume.py` then `uv run python scripts/resume_day5_case.py` | `build/day5/golden_thread_day5_pause.json`, `build/day5/golden_thread_day5_resumed.json` | Approval thread resumes without duplicate side effects |
| Day 6 | Refuse unsafe or unauthorised progression | Policy review, bounded reflection, and graceful refusal | Azure OpenAI optional, Azure Database for PostgreSQL | `uv run python scripts/run_day6_case.py` | `build/day6/golden_thread_day6.json` | Case ends in `approved_to_proceed`, `needs_human_review`, or `not_authorised_to_continue` with an audit-ready payload |
| Day 7 | Harden identity, secrets, traces, and audit evidence | Managed identity, secret elimination, redacted observability | Managed Identity, Key Vault RBAC, Azure AI Search RBAC, Log Analytics, PostgreSQL audit store | `uv run python scripts/verify_env.py --track full --env` then `uv run pytest tests/day7 tests/day6/test_training_runtime_integration.py -q` | PostgreSQL audit rows, redacted logs, hardened infra contracts | No forbidden runtime secret fallback, Search local auth disabled, audit rows emitted for sensitive outcomes |
| Day 8 | Make workflow behavior explorable and reliable | OpenTelemetry traces, regression harness, dashboards, alerts | Application Insights, Azure Monitor, Log Analytics, LangSmith optional, PostgreSQL audit store | `uv run pytest tests/day8 -q` and `az bicep build --file infra/monitoring/alerts/alerts.bicep` | Day 8 docs, regression dataset, monitoring assets, correlation-aware runtime | Operators can pivot from workflow run to trace to audit state, and silent reliability regressions surface in telemetry |
| Day 9 | Make capability allocation explicit, measurable, and reversible | Model router, workflow cost ledger, conservative cache, slice-governed optimisation | Azure OpenAI deployments, Azure Monitor, Application Insights, APIM policy assets optional, LangSmith optional | `uv run pytest tests/day9 -q` and `uv run pytest tests/day4/test_azure_openai_planner.py tests/api/test_app.py -q` | Day 9 docs, routing dataset, APIM policies, routed runtime | Model routing and cost are visible per workflow, low-risk paths can use cheaper capability safely, and risky slices block bad routing changes |

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
- [Day 6 Reflection and Graceful Refusal](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_06_REFLECTION_AND_GRACEFUL_REFUSAL.md)
- [Day 7 Security, Identity, and Auditability](/workspaces/agentic-accounts-payable-orchestrator/docs/day7/DAY_07_SECURITY_IDENTITY_AUDITABILITY.md)
- [Day 8 Observability and Reliability Engineering](/workspaces/agentic-accounts-payable-orchestrator/docs/day8/DAY_08_OBSERVABILITY_AND_RELIABILITY.md)
- [Day 9 Cost, Speed, Routing, Caching, and Optimisation](/workspaces/agentic-accounts-payable-orchestrator/docs/day9/DAY_09_COST_SPEED_ROUTING_CACHING_AND_OPTIMISATION.md)

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

4. Run the Day 6 review gate locally if you want to validate the refusal layer before deployment:

```bash
uv run python scripts/run_day6_case.py
```

5. Build and push the image:

```powershell
pwsh ./scripts/build_and_push_image.ps1
```

6. Deploy the Container App:

```powershell
pwsh ./scripts/deploy_container_app.ps1
```

7. Smoke-test the deployed app:

```bash
uv run python scripts/smoke_deployed_app.py --base-url https://<container-app-url>
```

Hosted success means a learner can hit `/healthz`, run the Day 4 case, inspect
the Day 6 review outcome, persist Day 5 state to Azure PostgreSQL, resume the
approval flow without duplicate side effects, and confirm that Day 7 has removed
Search key fallback while emitting redacted audit rows.

## Repo Conventions

- `pyproject.toml` and `uv.lock` are the dependency source of truth.
- `fixtures/golden_thread/` is the primary teaching baseline.
- `fixtures/day06/` is the primary adversarial safety baseline.
- `docs/day7/` groups the Day 7 training guides and security reference docs.
- `tests/day7/` groups the Day 7 security and audit regression suite.
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
uv run python scripts/run_day6_case.py
```

## Days 8-10

Day 8 is now the observability and reliability milestone, Day 9 adds explicit
capability allocation and cost governance, and Day 10 remains reserved for
production deployment hardening.
