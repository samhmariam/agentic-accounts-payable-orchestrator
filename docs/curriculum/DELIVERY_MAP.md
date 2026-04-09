# Curriculum Delivery Map

This is the fastest way to stay oriented during delivery.

## Focus Order

1. For Day 0, start with the day module README under `modules/`, then launch the bootstrap incident for the chosen track.
2. For Days 1-14, start with the day module README under `modules/`.
3. Run `uv run aegisap-lab incident start --day XX` only after you have read the customer context and file manifest.
4. Use the notebook as the diagnostic lens and reload harness, then patch the durable repo targets in your IDE and rerun the bootstrap cell before trusting the notebook proof.
5. Inject or reset the daily drill from the module entrypoint when the session calls for a timed failure recovery.
6. Run the canonical mastery gate after the verification commands.

## Folder Roles

| Path | Role |
|---|---|
| `modules/` | Primary learner entrypoints with customer context, mastery gate, chaos gate, and file manifest wormholes |
| `notebooks/` | Diagnostic lens for portal state, live experiments, and verification handoff |
| `docs/` | Supporting day references and business framing |
| `src/`, `infra/`, `scripts/` | Durable production targets that must be patched outside the notebook |
| `docs/curriculum/` | Programme operations, rubrics, trainer guidance, and schema-backed curriculum contract |

## Day-by-Day Navigation

| Day | Open First | Notebook | Primary Day Doc | Mastery Gate | Main Output |
|---|---|---|---|---|---|
| 0 | `modules/day_00_bootstrap/README.md` | `notebooks/day_0_bootstrap_incident.py` | [DAY_00_AZURE_BOOTSTRAP.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_00_AZURE_BOOTSTRAP.md) | `uv run aegisap-lab mastery --day 00 --track core` or `--track full` | `.day0/core.json` or `.day0/full.json` |
| 1 | `modules/day_01_trust_boundary/README.md` | `notebooks/day_1_agentic_fundamentals.py` | `docs/DAY_01.md` | `uv run aegisap-lab mastery --day 01` | `build/day1/golden_thread_day1.json` |
| 2 | `modules/day_02_resilience_ownership/README.md` | `notebooks/day_2_requirements_architecture.py` | `docs/DAY_02.md` | `uv run aegisap-lab mastery --day 02` | `build/day2/golden_thread_day2.json` |
| 3 | `modules/day_03_retrieval_authority/README.md` | `notebooks/day_3_azure_ai_services.py` | `docs/DAY_03.md` | `uv run aegisap-lab mastery --day 03` | `build/day3/golden_thread_day3.json` |
| 4 | `modules/day_04_single_agent_loops/README.md` | `notebooks/day_4_single_agent_loops.py` | `docs/DAY_04.md` | `uv run aegisap-lab mastery --day 04` | `build/day4/golden_thread_day4.json` |
| 5 | `modules/day_05_durable_state/README.md` | `notebooks/day_5_multi_agent_orchestration.py` | `docs/DAY_05.md` | `uv run aegisap-lab mastery --day 05` | `build/day5/golden_thread_day5_resumed.json` |
| 6 | `modules/day_06_data_authority/README.md` | `notebooks/day_6_data_ml_integration.py` | `docs/DAY_06.md` | `uv run aegisap-lab mastery --day 06` | `build/day6/golden_thread_day6.json` |
| 7 | `modules/day_07_eval_guardrails/README.md` | `notebooks/day_7_testing_eval_guardrails.py` | `docs/DAY_07.md` | `uv run aegisap-lab mastery --day 07` | `build/day7/eval_report.json` |
| 8 | `modules/day_08_iac_identity/README.md` | `notebooks/day_8_cicd_iac_deployment.py` | `docs/DAY_08.md` | `uv run aegisap-lab mastery --day 08` | `build/day8/deployment_design.json` |
| 9 | `modules/day_09_observability_cost/README.md` | `notebooks/day_9_scaling_monitoring_cost.py` | `docs/DAY_09.md` | `uv run aegisap-lab mastery --day 09` | `build/day9/routing_report.json` |
| 10 | `modules/day_10_production_acceptance/README.md` | `notebooks/day_10_production_operations.py` | `docs/DAY_10.md` | `uv run aegisap-lab mastery --day 10` | `build/day10/release_envelope.json` |
| 11 | `modules/day_11_delegated_identity/README.md` | `notebooks/day_11_delegated_identity_obo.py` | `docs/DAY_11.md` | `uv run aegisap-lab mastery --day 11` | `build/day11/obo_contract.json` |
| 12 | `modules/day_12_private_networking/README.md` | `notebooks/day_12_private_networking_constraints.py` | `docs/DAY_12.md` | `uv run aegisap-lab mastery --day 12` | `build/day12/private_network_posture.json` |
| 13 | `modules/day_13_integration_boundary/README.md` | `notebooks/day_13_integration_boundary_and_mcp.py` | `docs/DAY_13.md` | `uv run aegisap-lab mastery --day 13` | `build/day13/mcp_contract_report.json` |
| 14 | `modules/day_14_elite_ops/README.md` | `notebooks/day_14_breaking_changes_elite_ops.py` | `docs/DAY_14.md` | `uv run aegisap-lab mastery --day 14` | `build/day14/cto_trace_report.json` |

## Practical Rule

- Start in `modules/` to understand the customer constraint and file manifest, including Day 00.
- Use `notebooks/` to diagnose and validate repo code, not to write the durable patch.
- Use `src/`, `infra/`, and `scripts/` for the permanent fix.
- Use `uv run aegisap-lab mastery --day XX` to prove the repair holds under the curriculum contract.


## Drill Flow

- Use `uv run aegisap-lab drill list --day XX` to see the default and alternate drills for a day.
- Use `uv run aegisap-lab drill inject --day XX` to seed the broken state.
- Use `uv run aegisap-lab drill reset --day XX` to restore the baseline before the next learner.
