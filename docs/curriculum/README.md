# AegisAP Curriculum Guide

This folder contains the theoretical foundations that prepare learners for each
hands-on Marimo notebook lab. Every day has two documents:

| Document | Audience | Purpose |
|---|---|---|
| `trainer/DAY_XX_TRAINER.md` | Instructor | Facilitation guide, talking points, Q&A, common mistakes |
| `trainee/DAY_XX_TRAINEE.md` | Learner | Pre-lab reading, theory, Azure best practices, self-check |

Program-level operating guides live alongside the day materials:

- [TRAINER_OPERATIONS.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/TRAINER_OPERATIONS.md)
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

---

## Curriculum Map

| Day | Notebook | Core Theme | Azure Services |
|---|---|---|---|
| 0 | `day0_azure_bootstrap.py` | Infrastructure as Code & Identity | Bicep, Key Vault, Managed Identity, ACA, ACR |
| 1 | `day1_intake_canonicalization.py` | Trust Boundaries & Data Contracts | Azure OpenAI, schema validation |
| 2 | `day2_stateful_workflow.py` | Workflow State Machines | LangGraph, Azure AI, structured telemetry |
| 3 | `day3_retrieval_authority.py` | Retrieval-Augmented Generation | Azure AI Search, hybrid & semantic search |
| 4 | `day4_explicit_planning.py` | Plan-First Agent Architecture | Azure OpenAI structured outputs |
| 5 | `day5_durable_state.py` | Durable Workflows & Human-in-the-Loop | Azure PostgreSQL Flexible Server, ACA |
| 6 | `day6_policy_review.py` | Responsible AI & Graceful Refusal | Azure Content Safety, prompt defense |
| 7 | `day7_security_identity.py` | Zero Trust, PII & Audit | Managed Identity, Key Vault, RBAC |
| 8 | `day8_observability.py` | Observability & Reliability Engineering | Azure Monitor, App Insights, OpenTelemetry |
| 9 | `day9_cost_routing.py` | Cost Governance & Model Routing | Azure OpenAI tiers, semantic caching |
| 10 | `day10_deployment_gates.py` | Deployment & Acceptance Gating | ACA revisions, GitHub Actions OIDC |

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

The 11-day journey follows a single invoice case (`INV-3001 / Acme Office Supplies`)
end-to-end. Days are cumulative — each adds a new production-readiness concern to
exactly the same domain object. This design ensures learners experience the full
lifecycle of an enterprise AI feature, not a series of isolated demos.

```
Day 0  Extract & trust ──► Day 1
Day 1  Canonical shape ──► Day 2
Day 2  Explicit state ───► Day 3
Day 3  Grounded evidence ► Day 4
Day 4  Typed plan ────────► Day 5
Day 5  Durable pause ────► Day 6
Day 6  Safety gate ──────► Day 7
Day 7  Identity hardening ► Day 8
Day 8  Observability ────► Day 9
Day 9  Cost governance ──► Day 10
Day 10 Controlled release
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
| 0 | `build/day0/env_report.json` | Day 1 |
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
2. Read `trainer/DAY_XX_TRAINER.md` the evening before each session.
3. Score learners with `docs/curriculum/templates/DAILY_SCORECARD.md`.
4. Use [INCIDENT_DRILL_RUNBOOK.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/INCIDENT_DRILL_RUNBOOK.md) for the unsignposted failure drill on Days 8-10.
5. Use [CAPSTONE_PR_REVIEW.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/CAPSTONE_PR_REVIEW.md) and [CAPSTONE_REVIEW.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/CAPSTONE_REVIEW.md) together for the final review.
6. Each trainer file ends with a **Next-Day Bridge** — use it to close the session.

### For Trainees
1. Read `trainee/DAY_XX_TRAINEE.md` before the session starts (or the night before).
2. The **Check Your Understanding** questions at the end are not graded — they are
   designed to reveal gaps before you hit them in the notebook.
3. Refer back to the **Glossary** and **Azure Best Practices** sections while
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
