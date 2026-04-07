# AegisAP Curriculum Guide

This folder contains the portal-first and notebook-led delivery materials for
the AegisAP FDE curriculum. The notebooks and
[CURRICULUM_MANIFEST.yaml](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/CURRICULUM_MANIFEST.yaml)
are the operational source of truth for live delivery.

Use [DELIVERY_MAP.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/DELIVERY_MAP.md)
as the single navigation layer for daily delivery. It tells you which notebook,
primary doc, portal guide, command path, and artifact matter for each day.

The new manual-first Azure layer lives in
[portal/README.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/portal/README.md).
Use it to start each day in Azure first, then return to the notebook and only
after that to the scripts or modules that abstract the same work.

Trainer and trainee day documents still exist as supporting theory material for
the foundational portions of the course:

| Document | Audience | Purpose |
|---|---|---|
| `portal/DAY_XX_PORTAL.md` | Trainer + learner | Manual Azure-first guide: what to inspect or operate in the portal before the notebook |
| `trainer/DAY_XX_TRAINER.md` | Instructor | Facilitation guide, talking points, Q&A, common mistakes |
| `trainee/DAY_XX_TRAINEE.md` | Learner | Pre-lab reading, theory, Azure best practices, self-check |

Portal guides now cover Days 00-14. Trainer and trainee companion day docs
currently cover Days 00-10. Days 11-14 use the portal guide, notebook, primary
day doc, and artifact templates instead of separate trainer/trainee files.

Program-level operating guides live alongside the day materials:

- [TRAINER_OPERATIONS.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/TRAINER_OPERATIONS.md)
- [TRAINEE_PREFLIGHT_CHECKLIST.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/TRAINEE_PREFLIGHT_CHECKLIST.md)
- [FACILITATOR_DAY_START_CHECKLIST.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/FACILITATOR_DAY_START_CHECKLIST.md)
- [CAPSTONE_PR_REVIEW.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/CAPSTONE_PR_REVIEW.md)
- [INCIDENT_DRILL_RUNBOOK.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/INCIDENT_DRILL_RUNBOOK.md)
- [PILOT_MEASUREMENT_PLAN.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/PILOT_MEASUREMENT_PLAN.md)
- [GRADUATE_PROFILE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/GRADUATE_PROFILE.md)

---

## Audience And Entry Criteria

This curriculum is designed for internal FDEs who need to deliver Azure-first
agentic systems from concept to production. Learners are expected to arrive
with:

- Solid Python fundamentals
- Basic Git and CI/CD familiarity
- Working knowledge of HTTP APIs and JSON
- Comfort using the Azure CLI and reading IaC

Recommended pre-bootcamp setup:

- `uv sync --extra dev --extra day9`
- `az login`
- `source ./scripts/setup-env.sh core` for Days 0-4
- `source ./scripts/setup-env.sh full` before Day 5 and beyond

Use
[TRAINEE_PREFLIGHT_CHECKLIST.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/TRAINEE_PREFLIGHT_CHECKLIST.md)
as the launch-readiness checklist rather than relying on memory.

---

## Curriculum Map

| Day | Notebook | Core Theme | Azure Services / Enterprise Focus |
|---|---|---|---|
| 1 | `day_1_agentic_fundamentals.py` | Agentic systems fundamentals and business value | Azure AI strategy, WAF, CAF |
| 2 | `day_2_requirements_architecture.py` | Discovery, scoping, NFRs, architecture | Enterprise governance and stakeholder power |
| 3 | `day_3_azure_ai_services.py` | Azure AI services and framework choice | Azure AI Search, Azure OpenAI |
| 4 | `day_4_single_agent_loops.py` | Single-agent loops and fail-closed policy | Structured outputs, tool execution |
| 5 | `day_5_multi_agent_orchestration.py` | Multi-agent orchestration and HITL | LangGraph, durable state |
| 6 | `day_6_data_ml_integration.py` | Data authority and ML integration | ADF, Cosmos DB, MLflow |
| 7 | `day_7_testing_eval_guardrails.py` | Evals, guardrails, and structured refusal | Content Safety, slice governance |
| 8 | `day_8_cicd_iac_deployment.py` | CI/CD, IaC, identity, and secure release | Bicep, OIDC, ACA |
| 9 | `day_9_scaling_monitoring_cost.py` | Observability, routing, scaling, and cost | Azure Monitor, App Insights, economic control |
| 10 | `day_10_production_operations.py` | Production acceptance and release evidence | Release gates, CAB readiness |
| 11 | `day_11_delegated_identity_obo.py` | Delegated identity and OBO | Entra, Key Vault, actor-bound approval |
| 12 | `day_12_private_networking_constraints.py` | Private networking and security dependencies | Private Endpoints, DNS, egress policy |
| 13 | `day_13_integration_boundary_and_mcp.py` | Integration boundaries, async reliability, MCP | Azure Functions, Service Bus, MCP |
| 14 | `day_14_breaking_changes_elite_ops.py` | Elite operations and executive incident leadership | Canary evidence, trace correlation, incident command |

---

## Delivery Contract

Every day should leave the learner with four concrete outputs:

- A pre-read that explains the concept and names the production failure mode it prevents
- A notebook run that generates a day-specific artifact under `build/dayX/`
- A pass/fail definition of done that can be observed without trainer guesswork
- An exit ticket that proves the learner can explain the design choice, not just run the code

Use [ASSESSMENT_RUBRIC.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/ASSESSMENT_RUBRIC.md)
to score technical correctness, debugging discipline, security reasoning, and
production-readiness judgment.

Every trainee day and every trainer day must now include the same assessment
contract:

- `Lab Readiness`
- `Pass Criteria`
- `Common Failure Signals`
- `Exit Ticket`
- `Remediation Task`
- `Stretch Task`

---

## Learning Arc

The 14-day journey follows one system from concept to production discipline.
Days are cumulative. Earlier architecture and governance decisions become later
identity, network, boundary, and operations gates.

```
Day 1  Fundamentals ───► Day 2  Scope & architecture
Day 2  Scope & architecture ─► Day 3  Azure AI choices
Day 3  Azure AI choices ───► Day 4  Agent loop design
Day 4  Agent loop design ──► Day 5  Multi-agent state
Day 5  Multi-agent state ──► Day 6  Data authority
Day 6  Data authority ─────► Day 7  Evals & guardrails
Day 7  Evals & guardrails ─► Day 8  Secure deployment
Day 8  Secure deployment ──► Day 9  Observability & cost
Day 9  Observability & cost ► Day 10 Production operations
Day 10 Production ops ─────► Day 11 Delegated identity
Day 11 Delegated identity ─► Day 12 Private networking
Day 12 Private networking ─► Day 13 Integration boundaries
Day 13 Integration boundaries ► Day 14 Elite operations
```

---

## Track Matrix

| Track | When to use | Expected by days | Typical verification |
|---|---|---|---|
| `core` | Days 0-4, local notebook work, trust-boundary and planning fundamentals | 0-4 | `uv run python scripts/verify_env.py --track core` |
| `full` | Days 5-10, durable state, hosted runtime, security, deployment | 5-10 | `uv run python scripts/verify_env.py --track full --env` |

---

## Artifact Chain

The labs are intentionally cumulative. Trainers should treat missing upstream
artifacts as hard blockers unless a recovery command is supplied.

| Day | Primary artifact | Consumed by |
|---|---|---|
| 0 | `.day0/core.json` or `.day0/full.json` | Day 1 and local environment setup |
| 1 | `build/day1/golden_thread_day1.json` | Day 2 |
| 2 | `build/day2/golden_thread_day2.json` | Day 3 |
| 3 | `build/day3/golden_thread_day3.json` | Day 4 |
| 4 | `build/day4/golden_thread_day4.json`, `build/day4/checkpoint_policy_overlay.json` | Day 5, Day 10 review |
| 5 | `build/day5/golden_thread_day5_pause.json`, `build/day5/golden_thread_day5_resumed.json` | Day 7, Day 10 |
| 6 | `build/day6/golden_thread_day6.json` | Day 10 |
| 7 | `build/day7/security_posture.json` | Day 10 |
| 8 | `build/day8/regression_baseline.json`, `build/day8/checkpoint_trace_extension.json` | Day 9, Day 10 |
| 9 | `build/day9/routing_report.json` | Day 10 |
| 10 | `build/day10/release_envelope.json`, `build/day10/checkpoint_gate_extension.json` | Capstone review |
| Capstone | `build/capstone/<trainee_id>/release_packet.json` | Trainer scoring and release-style defense |

---

## Mandatory Checkpoints

Three days now include required build-or-modify checkpoints. These are pass/fail
gates for continuing without remediation.

| Checkpoint | Day | Required artifact | What the learner must prove |
|---|---|---|---|
| `Policy Overlay Change` | 4 | `build/day4/checkpoint_policy_overlay.json` | A fail-closed planning rule blocks the seeded case when evidence is missing |
| `Trace Extension` | 8 | `build/day8/checkpoint_trace_extension.json` | A new trace attribute or span is visible in regression evidence and KQL |
| `Gate Extension And Recovery` | 10 | `build/day10/checkpoint_gate_extension.json` | A training-only release gate is wired to upstream checkpoint artifacts and the release path is recovered |

Checkpoint coaching is part of the trainer rubric, not optional enrichment.

---

## Day Dependencies

- Day 0 establishes identity, Azure reachability, and zero-secret runtime posture.
- Days 1-4 build a trustworthy, explainable decision pipeline on top of that substrate.
- Days 5-7 convert the demo workflow into a resumable, auditable, secure runtime.
- Days 8-10 add production operations: observability, cost control, and release gating.

If a learner falls behind, recover them by regenerating the missing upstream
artifact with the exact script or notebook command referenced in the notebook
callouts rather than skipping a day.

---

## How to Use These Materials

### For Trainers
1. Read [TRAINER_OPERATIONS.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/TRAINER_OPERATIONS.md) before the cohort begins.
2. Open [DELIVERY_MAP.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/DELIVERY_MAP.md) and follow the day row for the session you are delivering.
3. For Days 00-10, read `trainer/DAY_XX_TRAINER.md` the evening before each session. For Days 11-14, use the notebook plus the primary day doc.
4. Score learners with `docs/curriculum/templates/DAILY_SCORECARD.md`.
5. Use [INCIDENT_DRILL_RUNBOOK.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/INCIDENT_DRILL_RUNBOOK.md) for the unsignposted failure drill on Days 8-10.
6. Use [CAPSTONE_PR_REVIEW.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/CAPSTONE_PR_REVIEW.md) and [CAPSTONE_REVIEW.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/CAPSTONE_REVIEW.md) together for the final review.
7. Each trainer file ends with a **Next-Day Bridge** — use it to close the session.

### For Trainees
1. Open [DELIVERY_MAP.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/DELIVERY_MAP.md) first and use it to find the current portal guide, notebook, and primary day doc.
2. Start with `portal/DAY_XX_PORTAL.md` for the day before opening the notebook.
3. For Days 00-10, read `trainee/DAY_XX_TRAINEE.md` before the session starts. For Days 11-14, use the portal guide, notebook, and primary day doc.
4. The **Check Your Understanding** questions at the end are not graded — they are
   designed to reveal gaps before you hit them in the notebook.
5. Refer back to the **Glossary** and **Azure Best Practices** sections while
   working through the notebook cells.

---

## Capstone Expectation

The bootcamp closes with a production-readiness review rather than a green-check
demo. A successful learner should be able to:

- Walk the golden thread from Day 0 to Day 10 without hand-waving missing controls
- Explain where Azure identity, policy, observability, and cost controls are enforced
- Diagnose a failed gate or missing artifact with an exact recovery command
- Defend at least one tradeoff they made between speed, safety, and cost

The detailed scoring and deliverables are defined in
[CAPSTONE_REVIEW.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/CAPSTONE_REVIEW.md).

The learner-to-role handoff is defined in
[GRADUATE_PROFILE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/GRADUATE_PROFILE.md).

---

## Capstone Review Flow

The capstone starts at the end of Day 9 and closes on Day 10.

1. Choose one bounded enhancement from the approved menu in [CAPSTONE_REVIEW.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/CAPSTONE_REVIEW.md).
2. Submit a one-page design brief naming scope, risk, tests, rollback, expected artifacts, and the assumption used to resolve the built-in ambiguity.
3. Complete the PR-style review cycle in [CAPSTONE_PR_REVIEW.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/CAPSTONE_PR_REVIEW.md).
4. Implement the enhancement and keep all required release checks green.
5. Build `build/capstone/<trainee_id>/release_packet.json` with `scripts/build_capstone_release_packet.py`.
6. Pass a release-style defense scored against [ASSESSMENT_RUBRIC.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/ASSESSMENT_RUBRIC.md).

---

## Azure Well-Architected Framework Alignment

Every day is tagged to one or more WAF pillars:

| Pillar | Primary Days |
|---|---|
| Security | 0, 6, 7 |
| Reliability | 5, 8, 10 |
| Cost Optimization | 9, 10 |
| Operational Excellence | 4, 8, 10 |
| Performance Efficiency | 3, 9 |
