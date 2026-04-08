# Curriculum Delivery Map

This is the fastest way to stay oriented during delivery.

If you only open one curriculum file before teaching or taking a session, open
this one.

## Focus Order

Use the same order every day:

1. For Day 0, start with the portal bootstrap guide.
2. For Days 1-14, start with `uv run aegisap-lab incident start --day XX`.
3. Complete the portal investigation or operating task only when the notebook tells you to do so.
4. Open the day notebook in `notebooks/`.
5. Open the primary day doc listed below.
6. Run the canonical terminal verification command after the production patch step.
7. Open artifact templates in `docs/curriculum/artifacts/` only when the notebook
   or rubric tells you to produce or assess them.

This keeps the flow anchored on one live path: incident first, notebook second,
automation third, with Day 0 as the only bootstrap exception.

## Folder Roles

| Path | Role |
|---|---|
| `docs/curriculum/portal/` | Manual Azure bootstrap guide for Day 0 only |
| `notebooks/` | Live teaching path and the operational source for day flow |
| `docs/` | Primary day references for Days 0-14 |
| `docs/curriculum/` | Programme operations, rubrics, artifacts, and supporting delivery docs |
| `docs/curriculum/trainer/` | Day 0 trainer bootstrap companion |
| `docs/curriculum/trainee/` | Day 0 learner bootstrap companion |
| `scripts/` | Repeatable commands for rebuilding artifacts and validating environments |
| `build/day*/` | Generated outputs that prove the day completed correctly |

## Day-by-Day Navigation

| Day | Open First | Notebook | Primary Day Doc | Companion Docs | Automation Handoff | Main Output |
|---|---|---|---|---|---|---|
| 0 | [DAY_00_PORTAL.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/portal/DAY_00_PORTAL.md) | Day 0 is doc-led rather than notebook-led | [DAY_00_AZURE_BOOTSTRAP.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_00_AZURE_BOOTSTRAP.md) | [DAY_00_TRAINER.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainer/DAY_00_TRAINER.md), [DAY_00_TRAINEE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainee/DAY_00_TRAINEE.md) | `uv run python scripts/verify_env.py --track core` or `--track full` | `.day0/core.json` or `.day0/full.json` |
| 1 | `uv run aegisap-lab incident start --day 01` | `notebooks/day_1_agentic_fundamentals.py` | [DAY_01.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_01.md) | None. Use the notebook, primary day doc, artifacts, and PR review contract. | `uv run python -m pytest tests/test_day_01_money.py tests/test_day_01_fixtures.py -q` then `uv run aegisap-lab artifact rebuild --day 01` | `build/day1/golden_thread_day1.json` |
| 2 | `uv run aegisap-lab incident start --day 02` | `notebooks/day_2_requirements_architecture.py` | [DAY_02.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_02.md) | None. Use the notebook, primary day doc, artifacts, and PR review contract. | `uv run python -m pytest tests/day2/test_resilience_controls.py tests/day8/test_retry_policy.py -q` then `uv run aegisap-lab artifact rebuild --day 02` | Day 2 artifacts in `docs/curriculum/artifacts/day02/` and `build/day2/golden_thread_day2.json` |
| 3 | `uv run aegisap-lab incident start --day 03` | `notebooks/day_3_azure_ai_services.py` | [DAY_03.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_03.md) | None. Use the notebook, primary day doc, artifacts, and PR review contract. | `uv run python -m pytest tests/day3/test_vendor_authority_ranking.py tests/day3/test_day3_exit_check.py -q` then `uv run aegisap-lab artifact rebuild --day 03` | `build/day3/golden_thread_day3.json` plus Day 3 artifacts in `docs/curriculum/artifacts/day03/` |
| 4 | `uv run aegisap-lab incident start --day 04` | `notebooks/day_4_single_agent_loops.py` | [DAY_04.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_04.md) | None. Use the notebook, primary day doc, artifacts, and PR review contract. | `uv run python -m pytest tests/day4/unit/planning/test_policy_overlay.py tests/day4/unit/recommendation/test_recommendation_gate.py -q` then `uv run aegisap-lab artifact rebuild --day 04` | `build/day4/golden_thread_day4.json` and Day 4 artifacts in `docs/curriculum/artifacts/day04/` |
| 5 | `uv run aegisap-lab incident start --day 05` | `notebooks/day_5_multi_agent_orchestration.py` | [DAY_05.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_05.md) | None. Use the notebook, primary day doc, artifacts, and PR review contract. | `uv run python -m pytest tests/day5/integration/test_resume_service.py tests/day5/integration/test_idempotent_recommendation_resume.py -q` then `uv run aegisap-lab artifact rebuild --day 05` | `build/day5/golden_thread_day5_pause.json`, `build/day5/golden_thread_day5_resumed.json`, and Day 5 artifacts |
| 6 | `uv run aegisap-lab incident start --day 06` | `notebooks/day_6_data_ml_integration.py` | [DAY_06.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_06.md) | None. Use the notebook, primary day doc, artifacts, and PR review contract. | `uv run python -m pytest tests/day6/test_review_gate.py tests/day6/test_training_runtime_integration.py -q` then `uv run aegisap-lab artifact rebuild --day 06` | `build/day6/golden_thread_day6.json` plus Day 6 artifacts in `docs/curriculum/artifacts/day06/` |
| 7 | `uv run aegisap-lab incident start --day 07` | `notebooks/day_7_testing_eval_guardrails.py` | [DAY_07.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_07.md) | None. Use the notebook, primary day doc, artifacts, and PR review contract. | `uv run python -m pytest tests/day7/security/test_redaction.py tests/day7/audit/test_audit_row_written_for_sensitive_decision.py -q` then `uv run aegisap-lab artifact rebuild --day 07` | `build/day7/eval_report.json` plus Day 7 artifacts in `docs/curriculum/artifacts/day07/` |
| 8 | `uv run aegisap-lab incident start --day 08` | `notebooks/day_8_cicd_iac_deployment.py` | [DAY_08.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_08.md) | None. Use the notebook, primary day doc, artifacts, and PR review contract. | `uv run python -m pytest tests/day7/security/test_search_token_auth_only.py tests/day8/test_security_and_context.py tests/day8/test_observability_contract.py -q` then `uv run aegisap-lab artifact rebuild --day 08` | `build/day8/deployment_design.json`, `build/day8/regression_baseline.json`, and `build/day8/checkpoint_trace_extension.json` |
| 9 | `uv run aegisap-lab incident start --day 09` | `notebooks/day_9_scaling_monitoring_cost.py` | [DAY_09.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_09.md) | None. Use the notebook, primary day doc, artifacts, and PR review contract. | `uv run python -m pytest tests/day9/test_routing_policy.py tests/day9/test_cache_and_cost.py tests/day9/test_runtime_day9_contract.py -q` then `uv run aegisap-lab artifact rebuild --day 09` | `build/day9/routing_report.json` plus Day 9 artifacts in `docs/curriculum/artifacts/day09/` |
| 10 | `uv run aegisap-lab incident start --day 10` | `notebooks/day_10_production_operations.py` | [DAY_10.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_10.md) | None. Use the notebook, primary day doc, artifacts, and PR review contract. | `uv run python -m pytest tests/day10/test_deployment_contract.py tests/day10/test_release_security.py tests/day10/test_release_envelope.py tests/training/test_checkpoints.py tests/api/test_app.py -q` then `uv run aegisap-lab artifact rebuild --day 10` | `build/day10/release_envelope.json` and `build/day10/checkpoint_gate_extension.json` |
| 11 | `uv run aegisap-lab incident start --day 11` | `notebooks/day_11_delegated_identity_obo.py` | [DAY_11.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_11.md) | None. Use the notebook, primary day doc, artifacts, and PR review contract. | `uv run python -m pytest tests/day11/test_actor_verification.py tests/day11/test_obo_flow.py tests/day11/test_obo_simulation.py -q` then `uv run aegisap-lab artifact rebuild --day 11` | `build/day11/obo_contract.json` plus Day 11 artifacts in `docs/curriculum/artifacts/day11/` |
| 12 | `uv run aegisap-lab incident start --day 12` | `notebooks/day_12_private_networking_constraints.py` | [DAY_12.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_12.md) | None. Use the notebook, primary day doc, artifacts, and PR review contract. | `uv run python -m pytest tests/day12/test_network_posture.py tests/day12/test_bicep_policy_checker.py -q` then `uv run aegisap-lab artifact rebuild --day 12` | `build/day12/static_bicep_analysis.json`, `build/day12/private_network_posture.json`, `build/day12/external_sink_disabled.json`, and Day 12 artifacts |
| 13 | `uv run aegisap-lab incident start --day 13` | `notebooks/day_13_integration_boundary_and_mcp.py` | [DAY_13.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_13.md) | None. Use the notebook, primary day doc, artifacts, and PR review contract. | `uv run python -m pytest tests/day13/test_dlq_consumer.py tests/day13/test_mcp_server.py tests/day13/test_payment_hold.py -q` then `uv run aegisap-lab artifact rebuild --day 13` | `build/day13/dlq_drain_report.json`, `build/day13/mcp_contract_report.json`, `build/day13/webhook_reliability_report.json`, and Day 13 artifacts |
| 14 | `uv run aegisap-lab incident start --day 14` | `notebooks/day_14_breaking_changes_elite_ops.py` | [DAY_14.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_14.md) | None. Use the notebook, primary day doc, artifacts, and PR review contract. | `uv run python -m pytest tests/day14/test_breaking_changes.py -q` then `uv run python scripts/run_chaos_capstone.py` then `uv run aegisap-lab artifact rebuild --day 14` | Day 14 reports under `build/day14/`, including `breaking_changes_drills.json` and `cto_trace_report.json` |

## Practical Rule

When you feel pulled across too many folders, fall back to this rule:

- `uv run aegisap-lab incident start --day XX` creates the hostile starting state.
- `notebooks/` tells you what to do now.
- `docs/curriculum/portal/` matters only for the Day 0 bootstrap exception.
- the primary day doc tells you why the day is designed that way.
- `docs/curriculum/` tells you how the programme is assessed and delivered.
- `scripts/` and `build/` prove that the day actually worked.

That separation is the intended mental model for the repo.
