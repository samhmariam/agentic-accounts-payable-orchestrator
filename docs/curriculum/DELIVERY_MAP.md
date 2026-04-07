# Curriculum Delivery Map

This is the fastest way to stay oriented during delivery.

If you only open one curriculum file before teaching or taking a session, open
this one.

## Focus Order

Use the same order every day:

1. Open the day guide in `docs/curriculum/portal/`.
2. Complete the portal-first inspection, configuration, or operating task for the day.
3. Open the day notebook in `notebooks/`.
4. Open the primary day doc listed below.
5. Run the canonical command or the notebook cells that produce the day artifact.
6. Use trainer and trainee companion docs only when they exist for that day.
7. Open artifact templates in `docs/curriculum/artifacts/` only when the notebook
   or rubric tells you to produce or assess them.

This keeps the flow anchored on one live path: Azure first, notebook second,
automation third.

## Folder Roles

| Path | Role |
|---|---|
| `docs/curriculum/portal/` | Manual Azure-first guides for Days 00-14 |
| `notebooks/` | Live teaching path and the operational source for day flow |
| `docs/` | Primary day references and technical deep dives, including top-level day docs and focused folders such as `docs/day7`, `docs/day8`, and `docs/day9` |
| `docs/curriculum/` | Programme operations, rubrics, artifacts, and supporting delivery docs |
| `docs/curriculum/trainer/` | Trainer facilitation companions for Days 00-10 |
| `docs/curriculum/trainee/` | Learner pre-reads for Days 00-10 |
| `scripts/` | Repeatable commands for rebuilding artifacts and validating environments |
| `build/day*/` | Generated outputs that prove the day completed correctly |

## Day-by-Day Navigation

| Day | Open First | Notebook | Primary Day Doc | Companion Docs | Automation Handoff | Main Output |
|---|---|---|---|---|---|---|
| 0 | [DAY_00_PORTAL.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/portal/DAY_00_PORTAL.md) | Day 0 is doc-led rather than notebook-led | [DAY_00_AZURE_BOOTSTRAP.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_00_AZURE_BOOTSTRAP.md) | [DAY_00_TRAINER.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainer/DAY_00_TRAINER.md), [DAY_00_TRAINEE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainee/DAY_00_TRAINEE.md) | `uv run python scripts/verify_env.py --track core` or `--track full` | `.day0/core.json` or `.day0/full.json` |
| 1 | [DAY_01_PORTAL.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/portal/DAY_01_PORTAL.md) | `notebooks/day_1_agentic_fundamentals.py` | [DAY_01.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_01.md) | [DAY_01_TRAINER.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainer/DAY_01_TRAINER.md), [DAY_01_TRAINEE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainee/DAY_01_TRAINEE.md) | `uv run python scripts/run_day1_intake.py --mode fixture` | `build/day1/golden_thread_day1.json` |
| 2 | [DAY_02_PORTAL.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/portal/DAY_02_PORTAL.md) | `notebooks/day_2_requirements_architecture.py` | [DAY_02.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_02.md) | [DAY_02_TRAINER.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainer/DAY_02_TRAINER.md), [DAY_02_TRAINEE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainee/DAY_02_TRAINEE.md) | notebook-led, then artifact templates in `docs/curriculum/artifacts/day02/` | Day 2 artifacts in `docs/curriculum/artifacts/day02/` |
| 3 | [DAY_03_PORTAL.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/portal/DAY_03_PORTAL.md) | `notebooks/day_3_azure_ai_services.py` | [DAY_03_FRAMEWORK_SELECTION_AND_CHOICE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_03_FRAMEWORK_SELECTION_AND_CHOICE.md) | [DAY_03_TRAINER.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainer/DAY_03_TRAINER.md), [DAY_03_TRAINEE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainee/DAY_03_TRAINEE.md) | `uv run python scripts/run_day3_case.py --retrieval-mode fixture` | `build/day3/golden_thread_day3.json` plus Day 3 artifacts in `docs/curriculum/artifacts/day03/` |
| 4 | [DAY_04_PORTAL.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/portal/DAY_04_PORTAL.md) | `notebooks/day_4_single_agent_loops.py` | [DAY_04_EXECUTION_FLOW.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_04_EXECUTION_FLOW.md) | [DAY_04_TRAINER.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainer/DAY_04_TRAINER.md), [DAY_04_TRAINEE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainee/DAY_04_TRAINEE.md) | `uv run python scripts/run_day4_case.py --planner-mode fixture` | `build/day4/golden_thread_day4.json` and `build/day4/checkpoint_policy_overlay.json` |
| 5 | [DAY_05_PORTAL.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/portal/DAY_05_PORTAL.md) | `notebooks/day_5_multi_agent_orchestration.py` | [DAY_05_DURABLE_STATE_AND_RESUMPTION.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_05_DURABLE_STATE_AND_RESUMPTION.md) | [DAY_05_TRAINER.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainer/DAY_05_TRAINER.md), [DAY_05_TRAINEE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainee/DAY_05_TRAINEE.md) | `uv run python scripts/run_day5_pause_resume.py` then `uv run python scripts/resume_day5_case.py` | `build/day5/golden_thread_day5_pause.json` and `build/day5/golden_thread_day5_resumed.json` |
| 6 | [DAY_06_PORTAL.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/portal/DAY_06_PORTAL.md) | `notebooks/day_6_data_ml_integration.py` | [DAY_06_REFLECTION_AND_GRACEFUL_REFUSAL.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_06_REFLECTION_AND_GRACEFUL_REFUSAL.md) | [DAY_06_TRAINER.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainer/DAY_06_TRAINER.md), [DAY_06_TRAINEE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainee/DAY_06_TRAINEE.md) | `uv run python scripts/run_day6_case.py` | `build/day6/golden_thread_day6.json` plus Day 6 artifacts in `docs/curriculum/artifacts/day06/` |
| 7 | [DAY_07_PORTAL.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/portal/DAY_07_PORTAL.md) | `notebooks/day_7_testing_eval_guardrails.py` | [DAY_07_EVAL_GUARDRAILS_SLICE_GOVERNANCE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_07_EVAL_GUARDRAILS_SLICE_GOVERNANCE.md) | [DAY_07_TRAINER.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainer/DAY_07_TRAINER.md), [DAY_07_TRAINEE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainee/DAY_07_TRAINEE.md) | notebook-led plus `uv run python -m pytest tests/day7 tests/day6/test_training_runtime_integration.py -q` | `build/day7/security_posture.json` plus Day 7 artifacts in `docs/curriculum/artifacts/day07/` |
| 8 | [DAY_08_PORTAL.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/portal/DAY_08_PORTAL.md) | `notebooks/day_8_cicd_iac_deployment.py` | [DAY_08_IAC_IDENTITY_RELEASE_OWNERSHIP.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_08_IAC_IDENTITY_RELEASE_OWNERSHIP.md) | [DAY_08_TRAINER.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainer/DAY_08_TRAINER.md), [DAY_08_TRAINEE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainee/DAY_08_TRAINEE.md) | `uv run python -m pytest tests/day8 -q` | `build/day8/regression_baseline.json` and `build/day8/checkpoint_trace_extension.json` |
| 9 | [DAY_09_PORTAL.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/portal/DAY_09_PORTAL.md) | `notebooks/day_9_scaling_monitoring_cost.py` | [DAY_09_COST_SPEED_ROUTING_CACHING_AND_OPTIMISATION.md](/workspaces/agentic-accounts-payable-orchestrator/docs/day9/DAY_09_COST_SPEED_ROUTING_CACHING_AND_OPTIMISATION.md) | [DAY_09_TRAINER.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainer/DAY_09_TRAINER.md), [DAY_09_TRAINEE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainee/DAY_09_TRAINEE.md) | `uv run python -m pytest tests/day9 -q` | `build/day9/routing_report.json` plus Day 9 artifacts in `docs/curriculum/artifacts/day09/` |
| 10 | [DAY_10_PORTAL.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/portal/DAY_10_PORTAL.md) | `notebooks/day_10_production_operations.py` | [DAY_10_DEPLOYMENT_AND_ACCEPTANCE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_10_DEPLOYMENT_AND_ACCEPTANCE.md) | [DAY_10_TRAINER.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainer/DAY_10_TRAINER.md), [DAY_10_TRAINEE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainee/DAY_10_TRAINEE.md) | `uv run python -m pytest tests/day10 tests/api/test_app.py -q` | `build/day10/release_envelope.json` and `build/day10/checkpoint_gate_extension.json` |
| 11 | [DAY_11_PORTAL.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/portal/DAY_11_PORTAL.md) | `notebooks/day_11_delegated_identity_obo.py` | [DAY_11_DELEGATED_IDENTITY.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_11_DELEGATED_IDENTITY.md) | No separate trainer or trainee day files. Use the portal guide, notebook, primary doc, and Day 11 artifact templates. | `uv run python scripts/verify_delegated_identity_contract.py` and `uv run python -m pytest tests/day11 -q` | `build/day11/obo_contract.json` plus Day 11 artifacts in `docs/curriculum/artifacts/day11/` |
| 12 | [DAY_12_PORTAL.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/portal/DAY_12_PORTAL.md) | `notebooks/day_12_private_networking_constraints.py` | [DAY_12_PRIVATE_NETWORKING.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_12_PRIVATE_NETWORKING.md) | No separate trainer or trainee day files. Use the portal guide, notebook, primary doc, and Day 12 artifact templates. | `uv run python scripts/verify_private_network_posture.py` and `uv run python -m pytest tests/day12 -q` | `build/day12/private_network_posture.json` and `build/day12/external_sink_disabled.json` plus Day 12 artifacts |
| 13 | [DAY_13_PORTAL.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/portal/DAY_13_PORTAL.md) | `notebooks/day_13_integration_boundary_and_mcp.py` | [DAY_13_INTEGRATION_AND_MCP.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_13_INTEGRATION_AND_MCP.md) | No separate trainer or trainee day files. Use the portal guide, notebook, primary doc, and Day 13 artifact templates. | `uv run python scripts/verify_mcp_contract_integrity.py` and `uv run python -m pytest tests/day13 -q` | `build/day13/dlq_drain_report.json`, `build/day13/mcp_contract_report.json`, and Day 13 artifacts |
| 14 | [DAY_14_PORTAL.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/portal/DAY_14_PORTAL.md) | `notebooks/day_14_breaking_changes_elite_ops.py` | [DAY_14_BREAKING_CHANGES.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_14_BREAKING_CHANGES.md) | No separate trainer or trainee day files. Use the portal guide, notebook, primary doc, and Day 14 artifact templates. | `uv run python scripts/generate_cto_trace_report.py` and `uv run python -m pytest tests/day14 -q` | Day 14 reports under `build/day14/` plus Day 14 artifacts |

## Practical Rule

When you feel pulled across too many folders, fall back to this rule:

- `notebooks/` tells you what to do now.
- `docs/curriculum/portal/` tells you what to inspect or operate in Azure first.
- `notebooks/` tells you what to do next.
- the primary day doc tells you why the day is designed that way.
- `docs/curriculum/` tells you how the programme is assessed and delivered.
- `scripts/` and `build/` prove that the day actually worked.

That separation is the intended mental model for the repo.
