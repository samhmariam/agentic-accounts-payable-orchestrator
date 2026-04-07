import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _bootstrap():
    import sys
    from pathlib import Path
    _root = Path(__file__).resolve().parents[1]
    for _p in [str(_root / "src"), str(_root / "notebooks"), str(_root)]:
        if _p not in sys.path:
            sys.path.insert(0, _p)
    return


@app.cell
def _imports():
    import marimo as mo
    import json
    import os
    from pathlib import Path
    return json, mo, os, Path


# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------
@app.cell
def _title(mo):
    mo.md("""
    # Day 10 — Deployment & Acceptance Gating · Production Operations

    > **WAF Pillars covered:** Operational Excellence · Reliability · Security · Cost Optimization · Performance Efficiency
    > **Estimated time:** 2.5 hours
    > **Sources:** `docs/curriculum/trainee/DAY_10_TRAINEE.md`
    > **Prerequisites:** Days 1–9 complete; all prior artifacts present in `build/`.

    ---

    ## Learning Objectives

    1. Explain Azure Container Apps' revision model and how it enables zero-downtime releases.
    2. Describe release authority, gate exceptions, and why green technical checks are still not enough without named owners.
    3. List the six implemented acceptance gates and describe what each verifies.
    4. Run the shared gate runner and interpret the release envelope it produces.
    5. Define halt criteria, error-budget thinking, and the incident roles required in the first 24 hours after release.

    ---

    ## Where Day 10 Sits in the Full Arc

    ```
    Day 7  ── Day 8 ── Day 9 ──►[Day 10]
    Testing  CI/CD   Scaling   Production
    & Safety & IaC   & Cost    Operations
    ```

    Day 10 answers: **"How do we confirm that AegisAP is safe to promote to production?"**
    Every prior day produced an artifact. Today those artifacts are the evidence that the
    six acceptance gates consume.

    Sections 1-4 intentionally **refresh** Day 8 deployment mechanics in production terms.
    The genuinely new Day 10 material begins in Sections 5-8: halt criteria, release authority,
    incident command, and evidence packaging for operators and change boards.
    """)
    return


@app.cell
def _full_day_agenda(mo):
    from _shared.curriculum_scaffolds import render_full_day_agenda

    render_full_day_agenda(
        mo,
        day_label="Day 10 production operations",
        core_outcome="treat a green deployment as the start of operator accountability rather than the end of engineering work",
    )
    return

@app.cell
def _notebook_guide(mo):
    from _shared.lab_guide import render_notebook_learning_context

    render_notebook_learning_context(
        mo,
        purpose='Decide whether AegisAP is safe to promote by turning earlier artifacts into acceptance-gate evidence and operator-facing release materials.',
        prerequisites=['Days 1-9 complete.', '`build/day5/golden_thread_day5_resumed.json`, `build/day6/golden_thread_day6.json`, `build/day8/regression_baseline.json`, and `build/day9/routing_report.json` are present.', '`evals/malicious_cases.jsonl` is present.'],
        resources=['`notebooks/day_10_production_operations.py`', '`build/day10/` for `release_envelope.json`, `checkpoint_gate_extension.json`, and `design_defense.json`', '`scripts/check_all_gates.py` for CLI follow-up', '`docs/curriculum/artifacts/day10/` for CAB and executive outputs'],
        setup_sequence=['Verify the upstream artifacts exist before assuming Day 10 cells will pass.', 'Run the early lineage and evidence-map cells so you can see which prior day feeds which gate.', 'Keep the notebook as the primary place to understand the release decision; use the CLI gate runner only as follow-up validation.'],
        run_steps=['Work through the six gate explanations and the release-evidence sections in order.', 'Use the notebook tables to map each gate to its upstream artifact and operator meaning.', 'Run the artifact-writing cells that produce `build/day10/release_envelope.json` and `build/day10/design_defense.json`.', 'Finish with the Day 10 checklist and artifact pack references.'],
        output_interpretation=['The main completion signal is `build/day10/release_envelope.json` plus the checkpoint extension artifact.', 'Interpret outputs as release evidence, not just test results: each gate answers a production question.', 'A good Day 10 result tells you whether to halt, release, or escalate, and why.'],
        troubleshooting=['If a gate fails, first check whether its upstream artifact exists and is current.', 'If the release envelope looks incomplete, rerun the artifact cell after the earlier gate-summary cells have executed.', 'If you feel lost in gate names, stay with the release-evidence map before using the CLI runner.'],
        outside_references=['Long-form theory: `docs/curriculum/trainee/DAY_10_TRAINEE.md`', 'Trainer notes: `docs/curriculum/trainer/DAY_10_TRAINER.md`', 'Reusable references: `docs/curriculum/artifacts/day10/`'],
    )
    return


@app.cell
def _three_surface_linkage(mo):
    from _shared.lab_guide import render_surface_linkage

    render_surface_linkage(
        mo,
        portal_guide="docs/curriculum/portal/DAY_10_PORTAL.md",
        portal_activity="Inspect the live Container App revision, traffic state, ingress, and health signals in Azure before you trust the release envelope or gate runner.",
        notebook_activity="Use the gate explanations, release-evidence map, release-authority framing, and envelope sections to interpret what the Azure release state actually means operationally.",
        automation_steps=[
            "`uv run python scripts/check_all_gates.py --out build/day10/release_envelope.json` formalizes the release decision after you have already inspected the live runtime.",
            "`uv run python -m pytest tests/day10 tests/api/test_app.py -q` adds regression proof for the same release judgment.",
        ],
        evidence_checks=[
            "The portal revision and traffic picture should match the release story told in the notebook.",
            "`build/day10/release_envelope.json` should encode the same go, hold, or rollback judgment you would make from Azure evidence.",
            "If the gate artifact and the live Azure state disagree, treat the disagreement as a blocker rather than trusting the generated report.",
        ],
    )
    return


@app.cell
def _azure_mastery_guide(mo):
    from _shared.lab_guide import render_azure_mastery_guide

    render_azure_mastery_guide(
        mo,
        focus="Day 10 mastery means you can inspect release state in Azure Container Apps, verify the gate decision from the command line, recognise the minimal code path for health and traffic control, and prove that a green release envelope matches the live runtime.",
        portal_tasks="""
- Open the **Container App** and inspect **Revisions** so you can see which revision is live, which ones are inactive, and whether the traffic picture matches the release story.
- Inspect **Ingress** and the app URL so you can connect gate outputs to the actual revision receiving traffic.
- Open **Application Insights** or the linked monitoring surface and confirm the candidate revision is healthy before treating the release envelope as trustworthy.
- If a release is halted or rolled back, use the portal to confirm the rollback is a real traffic change, not just a local note in the notebook.
""",
        cli_verification="""
**Inspect the Container App from Azure CLI**

```bash
export AZURE_CONTAINER_APP_NAME=ca-aegisap-staging

az containerapp show \
  --name "$AZURE_CONTAINER_APP_NAME" \
  --resource-group "$AZURE_RESOURCE_GROUP" \
  --query "{latestRevision:properties.latestRevisionName,provisioningState:properties.provisioningState,fqdn:properties.configuration.ingress.fqdn}"
```

**List revisions and compare them to the release decision**

```bash
az containerapp revision list \
  --name "$AZURE_CONTAINER_APP_NAME" \
  --resource-group "$AZURE_RESOURCE_GROUP" \
  -o table
```

**Run the shared gate runner and write the release envelope**

```bash
uv run python scripts/check_all_gates.py \
  --out build/day10/release_envelope.json
```

**Rollback traffic to a known-good revision if needed**

```bash
az containerapp ingress traffic set \
  --name "$AZURE_CONTAINER_APP_NAME" \
  --resource-group "$AZURE_RESOURCE_GROUP" \
  --revision-weight "<stable-revision>=100"
```
""",
        sdk_snippet="""
The repo's `AcaClient` shows the minimum code needed to inspect health or automate traffic changes without storing credentials.

```python
from aegisap.deploy.aca_client import AcaClient

client = AcaClient.from_env()
health = client.health_check()

if health.is_ready:
    print(health.latest_revision, health.status_code)
```
""",
        proof_in_azure="""
- `build/day10/release_envelope.json` exists and the gate statuses line up with the upstream artifacts you expect.
- The active revision and traffic split shown in Azure match the promote, halt, or rollback decision you are defending.
- The health endpoint and monitoring view agree that the live revision is actually healthy.
- Real production readiness means the envelope, the portal state, and the operator narrative all tell the same story.
""",
    )
    return


@app.cell
def _release_evidence_map(mo):
    mo.callout(
        mo.md(
            """
    ## Visual Guide — Release Evidence Map

    ```
    Day 5  ──► build/day5/golden_thread_day5_resumed.json ──► gate_resume_safety
    Day 6  ──► build/day6/golden_thread_day6.json         ──► gate_refusal_safety
    Day 8  ──► build/day8/regression_baseline.json        ──► gate_eval_regression
    Day 9  ──► build/day9/routing_report.json             ──► gate_budget
    Day 10 ──► runtime env + ACA revision health          ──► gate_security_posture / gate_aca_health
                                                         └──► build/day10/release_envelope.json
    ```

    Read the map from left to right:
    every Day 10 decision is only as trustworthy as the earlier artifact that feeds it.

    | Operator question | Evidence source | Why it matters |
    |---|---|---|
    | "Will this deploy duplicate side effects?" | `build/day5/golden_thread_day5_resumed.json` | Rollback is safer when replay safety is already proven |
    | "Did quality regress?" | `build/day8/regression_baseline.json` | Aggregate health is not enough without task-quality evidence |
    | "Can finance tolerate this revision?" | `build/day9/routing_report.json` | Budget drift is a release decision, not a bookkeeping detail |
    | "Is the runtime actually healthy?" | Container Apps revision health + env introspection | Technical evidence must match what is truly deployed |
    """
        ),
        kind="info",
    )
    return


@app.cell
def _day10_mastery_checkpoint(mo):
    mo.callout(
        mo.md(
            """
    ## Mastery Checkpoint — Before You Trust A Green Envelope

    You are ready to move past the Day 10 operator frame only if you can answer:
    - which prior artifact each of the six gates depends on, without looking it up
    - which gates are binary stop conditions versus gates that might require named override authority
    - why `skip_deploy=True` is acceptable for training but insufficient for real production promotion
    - what evidence a CAB or release manager would ask for if the deploy is technically green but financially or operationally suspicious
    """
        ),
        kind="warn",
    )
    return


# ---------------------------------------------------------------------------
# Section 1 – ACA Revision Model
# ---------------------------------------------------------------------------
@app.cell
def _s1_header(mo):
    mo.md("## 1. Azure Container Apps Revision Model")
    return


@app.cell
def _s1_body(mo):
    mo.md(r"""
    ### What is a Revision?

    An **ACA revision** is an immutable snapshot of:
    - The container image digest (SHA-pinned)
    - Environment variables and secrets references
    - CPU / memory / scaling rules

    A new revision is created on every `az containerapp update` or image push.
    Crucially, a new revision **starts at 0% traffic** — it is inactive until
    the release pipeline explicitly assigns it traffic weight.

    ### Deployment flow

    ```
    image pushed → new revision created (0% traffic)
                 → acceptance gates run against the new revision
                 → PASS: traffic shift to new revision (staging: 100%, prod: phased)
                 → FAIL: previous revision retains all traffic — no user impact
    ```

    ### Key concepts

    | Concept | Description |
    |---|---|
    | **Revision** | Immutable snapshot — the rollback unit |
    | **Traffic split** | Percentage of requests to each revision (e.g., 90% stable / 10% canary) |
    | **Rollback** | Shift 100% traffic back to a prior revision — no re-deploy required |
    | **Inactive revision** | Exists, receives 0% traffic — available for fast rollback |

    ### Azure best practices

    - Tag images with the full Git SHA (`aegisap-api:<sha>`). Never use `latest` in
      production — it makes rollback ambiguous.
    - Use `--revision-suffix` to give each revision a readable name
      (e.g., `rev-20240326-a1b2c3`) for easier portal identification.
    - Keep at least two prior revisions inactive for emergency rollback.

    ### Rollback command (full procedure — under 2 minutes)

    ```bash
    # Step 1: Enable multiple-revision mode if not already set
    az containerapp revision set-mode \
        --name aegisap-api \
        --resource-group rg-aegisap-prod \
        --mode multiple

    # Step 2: Route 100% traffic back to the stable revision
    az containerapp ingress traffic set \
        --name aegisap-api \
        --resource-group rg-aegisap-prod \
        --revision-weight "aegisap-api--stable=100"
    ```

    The new (broken) revision continues to exist as an inactive revision —
    useful for post-incident diagnostics — but receives zero traffic.
    """)
    return


# ---------------------------------------------------------------------------
# Section 2 – OIDC Federation
# ---------------------------------------------------------------------------
@app.cell
def _s2_header(mo):
    mo.md("## 2. GitHub Actions OIDC Federation")
    return


@app.cell
def _s2_body(mo):
    mo.md(r"""
    ### The problem with Service Principal secrets

    Traditional deployments store a Service Principal with a client secret in
    GitHub Actions secrets. This has two failure modes:

    1. **Rotation burden** — The secret has a lifetime measured in months and must be
       rotated manually before it expires.
    2. **Exfiltration risk** — A compromised Actions run (e.g., a malicious dependency)
       can read and exfiltrate the secret, granting persistent Azure access.

    ### How OIDC federation eliminates this

    ```
    GitHub Actions job starts
        │
        ▼
    GitHub generates a short-lived OIDC token (JWT) for this specific workflow run
        │
        ▼
    azure/login action presents the token to Microsoft Entra ID
        │
        ▼
    Entra ID validates: correct repo? correct branch? correct workflow?
        │
        ▼
    Entra ID issues an access token valid for THIS JOB ONLY
        │
        ▼
    Azure CLI / SDK calls use this token — no secret ever stored or transmitted
    ```

    ### Comparison

    | Property | Service Principal + secret | OIDC federation |
    |---|---|---|
    | Secret lifetime | Months (must rotate) | Minutes (per-job token) |
    | Secret storage | GitHub Secrets | **None** — no secret exists |
    | Blast radius | Any workflow | Bound to specific repo + branch + workflow |
    | Rotation burden | Manual | None |

    ### Security posture gate failures

    The Day 10 `security_posture` gate fails the release if any of these
    conditions are detected:

    | Condition | Why it blocks |
    |---|---|
    | Container image contains `AZURE_OPENAI_API_KEY` | Should use Managed Identity — no key in runtime env |
    | ACR pull uses username/password | Must use Managed Identity with `AcrPull` role |
    | `LANGSMITH_API_KEY` absent from Key Vault | Must be a Key Vault secret — not a plain env var |
    | `AEGISAP_POSTGRES_DSN` set in staging or prod | Password DSN forbidden — Entra auth required |

    ### Azure best practices

    - Bind the federated credential to the **specific branch** (`refs/heads/main`)
      and **specific workflow** (`deploy-staging.yml`). Never use wildcard subjects.
    - Grant the deployment identity only the minimum RBAC roles:
      `AcrPush` on the registry, `Contributor` on the Container App resource group
      — never subscription-wide.
    """)
    return


# ---------------------------------------------------------------------------
# Section 3 – The Six Acceptance Gates
# ---------------------------------------------------------------------------
@app.cell
def _s3_header(mo):
    mo.md("## 3. The Six Acceptance Gates")
    return


@app.cell
def _s3_body(mo):
    mo.md(r"""
    All six gates must **pass** for a revision to be eligible for production promotion.
    Any single failure blocks the release with zero impact on live traffic.

    | Gate | What it checks | Artifact consumed |
    |---|---|---|
    | **security_posture** | No forbidden runtime secrets; env matches security contract | Environment introspection |
    | **eval_regression** | Day 8 regression baseline shows no score drop below threshold | `build/day8/regression_baseline.json` |
    | **budget** | Day 9 sample ledger stays within the configured daily cost ceiling | `build/day9/routing_report.json` |
    | **refusal_safety** | Day 6 adversarial results meet the minimum structured refusal rate | `build/day6/golden_thread_day6.json` |
    | **resume_safety** | Day 5 resume artifact reports zero duplicate side effects | `build/day5/golden_thread_day5_resumed.json` |
    | **aca_health** | Target Container App revision reports healthy and ready | Live ACA API (or skipped in training) |

    ### How gates are structured

    Every gate returns a `GateResult`:

    ```python
    @dataclass
    class GateResult:
        name: str
        passed: bool
        detail: str
        evidence: dict | None = None
    ```

    The gate runner collects all six and passes them to `build_release_envelope()`:

    ```python
    from aegisap.deploy.gates import run_all_gates, build_release_envelope

    results = run_all_gates(skip_deploy=True)  # skip_deploy=True skips live ACA check
    envelope = build_release_envelope(results)
    # envelope["all_passed"] is True only if all six gates passed
    ```

    ### Production extensions (not automated in this repo)

    The following gates are valuable in a real deployment pipeline but are not
    provided as notebook cells in this training repo:

    - Trace-correlation gating across Azure Monitor and LangSmith
    - Richer synthetic evaluation slicing beyond the Day 8 regression baseline
    - Multi-phase canary traffic shifting with automated halt-and-rollback rules

    These are worth discussing as next steps when hardening a real pipeline.
    """)
    return


# ---------------------------------------------------------------------------
# Section 4 – Live Gate Runner
# ---------------------------------------------------------------------------
@app.cell
def _s4_header(mo):
    mo.md("## 4. Live Gate Runner")
    return


@app.cell
def _s4_body(mo):
    mo.md(r"""
    The cell below runs all six gates and renders a pass/fail table.
    `skip_deploy=True` is set so the ACA health gate is skipped — appropriate
    in a local training environment where no live Container App is provisioned.

    All other five gates consume artifacts from `build/`. If a prior day's
    artifact is missing, that gate returns `passed=False` with a descriptive
    `detail` message indicating which notebook to run first.
    """)
    return


@app.cell
def _gate_runner_button(mo):
    _run_gates_btn = mo.ui.run_button(label="Run All Gates")
    mo.vstack([
        mo.md("### Run the acceptance gate suite"),
        _run_gates_btn,
    ])
    return (_run_gates_btn,)


@app.cell
def _gate_runner_output(mo, _run_gates_btn):
    from aegisap.deploy.gates import run_all_gates, build_release_envelope

    if _run_gates_btn.value:
        _results = run_all_gates(skip_deploy=True)
        _envelope = build_release_envelope(_results)

        _rows = []
        for _r in _results:
            _rows.append({
                "Gate": _r.name,
                "Status": "PASS" if _r.passed else "FAIL",
                "Detail": _r.detail,
            })

        _all_passed = _envelope["all_passed"]
        _banner = mo.callout(
            mo.md(
                "**All six gates passed.** Revision is eligible for staging promotion."),
            kind="success",
        ) if _all_passed else mo.callout(
            mo.md(
                "**One or more gates failed.** Release is blocked. See detail column for remediation."),
            kind="danger",
        )

        mo.vstack([
            _banner,
            mo.table(_rows),
        ])
    else:
        mo.callout(
            mo.md("Press **Run All Gates** to execute the suite."), kind="info")
    return (build_release_envelope, run_all_gates,)


# ---------------------------------------------------------------------------
# Section 5 – WAF Pillar Convergence
# ---------------------------------------------------------------------------
@app.cell
def _s5_header(mo):
    mo.md("## 5. SLOs, Error Budgets & Halt Criteria")
    return


@app.cell
def _s5_body(mo):
    mo.md(r"""
    Production operators do not ask only "did the gates pass?"
    They ask:

    - What signal forces an immediate halt?
    - How long can the system remain degraded before rollback is mandatory?
    - Which owner is allowed to override a gate and under what evidence standard?

    ### Recommended Day 10 halt criteria

    | Condition | Halt immediately? | Why |
    |---|---|---|
    | `security_posture` fails | **Yes** | Secret or identity drift is a hard trust-boundary break |
    | Critical slice regression | **Yes** | Aggregate scores can hide regulated-case regressions |
    | `resume_safety` fails | **Yes** | Duplicate side effects can create irreversible damage |
    | `budget` fails but all safety gates pass | Usually yes | Cost spikes are rarely worth live escalation without owner approval |
    | `aca_health` flakes during staged rollout | Pause and diagnose | Health instability under canary means rollback may soon be needed |

    ### Error-budget framing for AegisAP

    | Signal | Example operating budget | What burns it down |
    |---|---|---|
    | Failed recommendations | `0` on zero-tolerance classes | Missed mandatory escalation, wrong approval path |
    | User-visible health | Small, bounded budget | ACA revision instability, cold-start spikes |
    | Cost variance | Daily ceiling from Day 9 | Routing drift, cache bypass explosion |

    The key mental model: **a passing gate is not permission to relax.**
    It is permission to start watching the right signals with the right owners on call.
    """)
    return


@app.cell
def _waf_pillar_explorer(mo):
    _pillar_picker = mo.ui.dropdown(
        options=[
            "Green canary",
            "Eval slice regression",
            "Security posture drift",
            "Budget burn spike",
            "Rollback readiness gap",
        ],
        value="Green canary",
        label="Release state",
    )
    mo.vstack([
        mo.md("### Explore a release state — halt, continue, or escalate?"),
        _pillar_picker,
    ])
    return (_pillar_picker,)


@app.cell
def _waf_pillar_detail(mo, _pillar_picker):
    _detail = {
        "Green canary": {
            "decision": "Continue cautiously",
            "owner": "Release manager",
            "evidence": "All six gates pass; no live error spike; rollback revision known",
            "actions": [
                "Keep traffic staged rather than jumping immediately to 100%",
                "Watch Day 9 cost and latency signals during the first control window",
                "Keep rollback authority explicit until the observation window closes",
            ],
        },
        "Eval slice regression": {
            "decision": "Halt release",
            "owner": "Model owner + product approver",
            "evidence": "Protected slice regresses even if aggregate score improves",
            "actions": [
                "Block traffic shift immediately",
                "Open the slice regression log and identify the business class affected",
                "Require explicit override authority if anyone argues for release-with-monitoring",
            ],
        },
        "Security posture drift": {
            "decision": "Halt and investigate",
            "owner": "Security approver or break-glass owner",
            "evidence": "Forbidden secret present, MI drift, or identity contract violation",
            "actions": [
                "Treat as trust-boundary break, not a minor deploy issue",
                "Rollback if the new revision has any live traffic",
                "Preserve evidence before remediation so the incident can be audited",
            ],
        },
        "Budget burn spike": {
            "decision": "Escalate before continuing",
            "owner": "Service owner + finance/platform reviewer",
            "evidence": "Day 9 ledger projection exceeds daily ceiling",
            "actions": [
                "Check whether routing drift or cache bypass changed the economics",
                "Do not waive the budget gate silently; record the exception owner and expiry",
                "Decide whether the business value of continued rollout justifies the spend",
            ],
        },
        "Rollback readiness gap": {
            "decision": "Stop promotion",
            "owner": "Release manager",
            "evidence": "Candidate looks healthy, but stable revision or runbook is not confidently available",
            "actions": [
                "Do not continue on optimism",
                "Reconstruct the rollback path before any additional traffic shift",
                "Treat missing rollback evidence as an operational correctness failure",
            ],
        },
    }

    chosen = _pillar_picker.value
    info = _detail[chosen]
    lines = [f"### {chosen}"]
    lines.append(f"**Recommended decision:** {info['decision']}  |  **Primary owner:** {info['owner']}\n")
    lines.append(f"**Evidence threshold:** {info['evidence']}\n")
    lines.append("**Immediate actions:**")
    for p in info["actions"]:
        lines.append(f"- {p}")
    mo.md("\n".join(lines))
    return


@app.cell
def _day10_war_room_drill(mo):
    mo.callout(
        mo.md(
            r"""
    ### War-Room Mini Drill — T+00 to T+20

    Use this as a timed go / no-go rehearsal with a partner or out loud:

    | Time | New information | Your decision |
    |---|---|---|
    | `T+00` | All six gates pass, canary starts at 10% | Do you proceed or hold for an operator brief? |
    | `T+08` | p99 latency rises 18%, user-visible errors stay low | Which signal burns your error budget first? |
    | `T+12` | Quarter-end business owner asks to keep moving because no hard failures exist yet | Who has authority to continue, and what evidence must they sign against? |
    | `T+20` | Budget burn is now 2.2x the Day 9 expectation and rollback is still available | Do you halt, partially continue, or promote? Why? |

    A strong answer names:
    - the gate or live signal that changed the decision
    - the owner allowed to approve an exception
    - the expiry on that exception
    - the rollback trigger if the next interval worsens
    """
        ),
        kind="info",
    )
    return


# ---------------------------------------------------------------------------
# Section 6 – Release Envelope Viewer
# ---------------------------------------------------------------------------
@app.cell
def _s6_header(mo):
    mo.md("## 6. Release Envelope Structure")
    return


@app.cell
def _s6_body(mo):
    mo.md(r"""
    When all gates pass, `build_release_envelope()` produces a JSON document
    that serves as the machine-readable proof of release readiness:

    ```json
    {
      "all_passed": true,
      "gates": [
        {
          "name": "security_posture",
          "passed": true,
          "detail": "All checks passed.",
          "evidence": {"checks": ["managed_identity_pull", "no_raw_dsn", ...]}
        },
        {
          "name": "budget",
          "passed": true,
          "detail": "$0.012127 / $5.00 daily limit. Projected: $0.1455",
          "evidence": {"total_cost_usd": 0.012127, "within_budget": true, ...}
        }
      ]
    }
    ```

    This document is written to `build/day10/release_envelope.json` by the
    `_artifact_write` cell below. `scripts/check_all_gates.py` reads and
    re-validates it as part of the CI pipeline.

    ### Envelope fields

    | Field | Type | Description |
    |---|---|---|
    | `all_passed` | bool | True only if every gate in `gates` has `passed=true` |
    | `gates` | list | One entry per gate: `name`, `passed`, `detail`, `evidence` |
    | `evidence` | dict or null | Gate-specific structured data for audit trail |

    ### Checkpoint extension contract

    The Day 10 checkpoint also checks that the Day 4 and Day 8 checkpoint
    artifacts exist (`checkpoint_policy_overlay.json` and
    `checkpoint_trace_extension.json`). This is an additional training gate
    — `checkpoint_extension_contract` — that verifies the full Days 1–8 arc
    is in a runnable state before the final release rehearsal.
    """)
    return


@app.cell
def _envelope_viewer_button(mo):
    _view_envelope_btn = mo.ui.run_button(
        label="View Release Envelope (if present)")
    mo.vstack([
        mo.md("### Inspect the release envelope"),
        _view_envelope_btn,
    ])
    return (_view_envelope_btn,)


@app.cell
def _envelope_viewer_output(mo, Path, json, _view_envelope_btn):
    if _view_envelope_btn.value:
        _envelope_path = Path(__file__).resolve(
        ).parents[1] / "build" / "day10" / "release_envelope.json"
        if _envelope_path.exists():
            _envelope = json.loads(_envelope_path.read_text())
            _rows = []
            for _g in _envelope.get("gates", []):
                _rows.append({
                    "Gate": _g["name"],
                    "Passed": str(_g["passed"]),
                    "Detail": _g["detail"],
                })
            _all_ok = _envelope.get("all_passed", False)
            mo.vstack([
                mo.callout(
                    mo.md(f"**all_passed = {_all_ok}**"),
                    kind="success" if _all_ok else "danger",
                ),
                mo.table(_rows),
            ])
        else:
            mo.callout(
                mo.md(
                    "No release envelope found yet. "
                    "Run the `_artifact_write` cell to generate it."
                ),
                kind="warn",
            )
    else:
        mo.callout(
            mo.md("Press **View Release Envelope** to inspect."), kind="info")
    return


# ---------------------------------------------------------------------------
# Section 7 – Continuous Improvement Loop
# ---------------------------------------------------------------------------
@app.cell
def _s7_header(mo):
    mo.md("## 7. Incident Command, Exceptions & The First 24 Hours")
    return


@app.cell
def _s7_body(mo):
    mo.md(r"""
    The first 24 hours after release are where operator quality shows up.

    ### Minimum incident roles

    | Role | Responsibility |
    |---|---|
    | Incident commander | Owns triage order, stop/continue recommendation, and timeline discipline |
    | Release manager | Knows the candidate revision, stable revision, and rollback steps |
    | Domain owner | Explains business blast radius of degraded behavior |
    | Security approver | Required if a trust-boundary exception is being considered |

    ### Gate exceptions are not free passes

    If a team wants to continue despite a failing gate, the exception must name:
    - the exact failing gate
    - the bounded blast radius
    - the counter-signing authority
    - the expiry time
    - the rollback trigger that ends the exception automatically

    If any of those five are missing, it is not an exception process. It is wishful thinking.

    ### First 24-hour monitoring query

    ```sql
    traces
    | where customDimensions["aegis.outcome_type"] in
        ("recommendation_issued", "escalation_required", "case_refused")
    | summarize
        count() by outcome_type=tostring(customDimensions["aegis.outcome_type"]),
        bin(timestamp, 1h)
    | order by timestamp desc
    ```

    Alert if the `case_refused` fraction rises above 5% or if the high-value
    approval path disappears from the stream. The first can indicate upstream
    data quality drift; the second can indicate a dangerous routing regression.
    """)
    return


# ---------------------------------------------------------------------------
# Section 8 – Design Defense
# ---------------------------------------------------------------------------
@app.cell
def _s8_header(mo):
    mo.md("## 8. Design Defense")
    return


@app.cell
def _s8_body(mo):
    mo.md("""
    A **Design Defense** is a structured self-assessment where you articulate the key
    decisions made during the programme, the trade-offs considered, and the evidence
    behind each choice. This mirrors the FDE capstone review format: your reviewer will
    ask "why did you choose X over Y?" and expect an answer that references NFRs, ADRs,
    or gate evidence — not intuition.

    Answer the three questions below, one per FDE competency. Your responses will be
    saved to `build/day10/design_defense.json` as a programme artifact.
    """)
    return


@app.cell
def _design_defense_form(mo):
    _dd_analyze = mo.ui.text_area(
        placeholder=(
            "Reference your Day 1 Decision Tool score and Day 2 NFR table. "
            "Which signals scored highest for AegisAP, and what do they imply architecturally?"
        ),
        label=(
            "Analyze — Why is an agentic system the right approach for AegisAP? "
            "Cite specific signals and at least one NFR."
        ),
    )
    _dd_design = mo.ui.text_area(
        placeholder=(
            "Reference an ADR by number. Name the alternative that was rejected "
            "and the consequence that was accepted as a result."
        ),
        label=(
            "Design — Name one significant architectural decision, its rejected alternative, "
            "and the consequence accepted."
        ),
    )
    _dd_deploy = mo.ui.text_area(
        placeholder=(
            "Walk through the six gates, the halt criteria, and one exception you would NOT allow. "
            "Which owner would you wake up at 2am and why?"
        ),
        label=(
            "Deploy — Explain how the six acceptance gates, halt criteria, and rollback authority "
            "together prove AegisAP is safe to promote to production."
        ),
    )
    _dd_save_btn = mo.ui.run_button(label="Save Design Defense Artifact")
    mo.vstack([
        _dd_analyze,
        _dd_design,
        _dd_deploy,
        _dd_save_btn,
    ])
    return _dd_analyze, _dd_design, _dd_deploy, _dd_save_btn


@app.cell
def _design_defense_artifact(
    mo,
    Path,
    json,
    _dd_analyze,
    _dd_design,
    _dd_deploy,
    _dd_save_btn,
):
    if _dd_save_btn.value:
        import datetime as _dd_dt

        _completeness = {
            "analyze_answered": len(_dd_analyze.value.strip()) > 50,
            "design_answered": len(_dd_design.value.strip()) > 50,
            "deploy_answered": len(_dd_deploy.value.strip()) > 50,
        }
        _completeness["all_complete"] = all(_completeness.values())

        _dd_artifact = {
            "produced_at": _dd_dt.datetime.utcnow().isoformat() + "Z",
            "competency_responses": {
                "analyze": _dd_analyze.value.strip(),
                "design": _dd_design.value.strip(),
                "deploy": _dd_deploy.value.strip(),
            },
            "completeness": _completeness,
        }

        _dd_out = Path(__file__).resolve(
        ).parents[1] / "build" / "day10" / "design_defense.json"
        _dd_out.parent.mkdir(parents=True, exist_ok=True)
        _dd_out.write_text(json.dumps(_dd_artifact, indent=2))

        _status = [
            f"- Analyze: {'✅ Answered' if _completeness['analyze_answered'] else '⚠️ Too short (< 50 chars)'}",
            f"- Design:  {'✅ Answered' if _completeness['design_answered'] else '⚠️ Too short (< 50 chars)'}",
            f"- Deploy:  {'✅ Answered' if _completeness['deploy_answered'] else '⚠️ Too short (< 50 chars)'}",
        ]
        mo.callout(
            mo.md(
                "**Design defense saved to `build/day10/design_defense.json`**\n\n"
                + "\n".join(_status)
            ),
            kind="success" if _completeness["all_complete"] else "warn",
        )
    else:
        mo.callout(
            mo.md(
                "Write your responses above, then click "
                "**Save Design Defense Artifact** to record them."
            ),
            kind="info",
        )
    return


# ---------------------------------------------------------------------------
# Exercises
# ---------------------------------------------------------------------------
@app.cell
def _exercises_header(mo):
    mo.md("---\n## Exercises")
    return


@app.cell
def _exercise_1(mo):
    mo.accordion({
        "Exercise 1 — Gate failure triage": mo.vstack([
            mo.md(r"""
**Scenario:** You push a new release and the gate runner returns:

```
[FAIL] eval_regression         Regressed metrics: test_pass_rate
[PASS] security_posture        All checks passed.
[PASS] budget                  $0.0121 / $5.00 daily limit.
[PASS] refusal_safety          Refusal rate: 97.3% (required >= 95.0%)
[PASS] resume_safety           No duplicate side effects.
[PASS] aca_health              Skipped (--skip-deploy flag).
```

**Questions:**

1. Which day's artifact is the `eval_regression` gate reading? What file does it look for?
2. What does a regression in `test_pass_rate` tell you about the change you just pushed?
3. List the steps you would take to investigate and remediate — from reading the baseline
   to deciding whether to block or gate-override the release.
4. Under what conditions (if any) would it be acceptable to bypass the `eval_regression` gate?
            """),
            mo.accordion({
                "Show solution": mo.md(r"""
**1. Artifact and file:**

The `eval_regression` gate reads `build/day8/regression_baseline.json`.
It calls `aegisap.observability.baseline.compare_to_baseline(current)` to
compute per-metric deltas and flags any metric where the current value falls
below the baseline threshold.

**2. What the regression means:**

A `test_pass_rate` regression means the proportion of synthetic test cases that
the system answers correctly has dropped below the baseline established in Day 8.
This could indicate:
- A prompt or policy change that reduces extraction accuracy
- A model version change (e.g., a rolling deployment updated the model endpoint)
- A data preprocessing regression affecting input quality

**3. Remediation steps:**

1. **Read the baseline file:** `build/day8/regression_baseline.json` — check
   what `test_pass_rate` was at baseline and what the current value is.
2. **Check the diff:** What changed in this PR? Prompt templates, routing policy,
   model deployment name, eval fixture?
3. **Re-run Day 8 notebook** on `main` (no changes) to confirm the baseline is
   still reproducible — rules out infrastructure flakiness.
4. **Isolate the change:** Revert the suspected breaking change in a branch, run
   the eval, compare scores.
5. **Decision gate:** If the regression is < 1% and caused by a deliberate
   trade-off (e.g., a latency reduction that slightly reduces completeness), document
   the decision and update the baseline threshold in `evals/score_thresholds.yaml`.
6. If the regression is unexplained or > 1%, **block the release** and fix root cause.

**4. Acceptable bypass conditions:**

Almost never. The only defensible bypass is:
- A known eval-fixture bug that causes false negatives (fix the fixture instead)
- A planned model upgrade where the new model is validated on a richer eval suite
  (raise the baseline threshold before merging, do not lower it)

A release with a regressed `test_pass_rate` that goes to production is a
silent quality degradation — it will erode user trust before anyone notices.
                """),
            }),
        ]),
    })
    return


@app.cell
def _exercise_2(mo):
    mo.accordion({
        "Exercise 2 — Rollback procedure design": mo.vstack([
            mo.md(r"""
**Scenario:** AegisAP v2.3.1 was promoted to production 30 minutes ago (100% traffic).
Users are reporting that compliance review decisions are inconsistently structured —
some responses are missing the `evidence_citations` field.

A hotfix will take 4 hours to develop and test. Leadership has approved an immediate rollback.

**Questions:**

1. Identify the exact `az containerapp` commands to execute the rollback (assume the stable
   revision suffix is `aegisap-api--rev-2024-stable`).
2. Which acceptance gate should have caught this before promotion? What would you change
   about the gate or the eval suite to prevent recurrence?
3. After rollback, what should the on-call engineer check in Azure Monitor / KQL to
   confirm that the stable revision is serving requests correctly?
4. What practice would you add to the CI pipeline to ensure `evidence_citations` is
   always present in compliance review output?
            """),
            mo.accordion({
                "Show solution": mo.md(r"""
**1. Rollback commands:**

```bash
# Ensure multiple-revision mode is enabled (safe to run even if already set)
az containerapp revision set-mode \
    --name aegisap-api \
    --resource-group rg-aegisap-prod \
    --mode multiple

# Route 100% traffic back to the stable revision
az containerapp ingress traffic set \
    --name aegisap-api \
    --resource-group rg-aegisap-prod \
    --revision-weight "aegisap-api--rev-2024-stable=100"

# Confirm traffic weights
az containerapp ingress traffic show \
    --name aegisap-api \
    --resource-group rg-aegisap-prod
```

**2. Which gate should have caught it:**

The `eval_regression` gate — if a synthetic test case for `compliance_review`
verified that `evidence_citations` is always present in the output schema.

Likely gap: the eval suite tests high-level correctness (is the decision right?)
but not structural completeness (are all required fields present?).

Prevention:
- Add a structural schema validator to the eval suite: after each
  `compliance_review` response, assert `evidence_citations` is present and non-empty.
- Write this as a `synthetic_cases.jsonl` entry so it is executed by `gate_eval_regression`.

**3. Post-rollback KQL checks:**

```sql
-- Verify stable revision is receiving traffic
traces
| where customDimensions["aegis.outcome_type"] == "recommendation_issued"
| project timestamp, operation_Id, customDimensions["aegis.workflow_run_id"]
| order by timestamp desc
| take 20

-- Check for error rate in the last 15 minutes
exceptions
| where timestamp > ago(15m)
| summarize count() by type, bin(timestamp, 1m)
| order by timestamp desc
```

If both queries return clean results (outcomes flowing, error rate normal),
the rollback was successful.

**4. CI addition to prevent recurrence:**

Add a Pydantic schema validator that runs as part of the Day 7 test suite:

```python
from pydantic import BaseModel

class ComplianceReviewOutput(BaseModel):
    decision: str
    confidence: float
    evidence_citations: list[str]  # Must be present and non-empty
    reviewer_notes: str | None = None

# In the eval runner:
output = ComplianceReviewOutput.model_validate(raw_response)
```

Wire this into `gate_eval_regression` by including the schema validation
pass rate in the regression baseline. Any future release where schema
validation drops below 100% will fail the gate.
                """),
            }),
        ]),
    })
    return


@app.cell
def _exercise_3(mo):
    mo.accordion({
        "Exercise 3 — WAF gap analysis": mo.vstack([
            mo.md(r"""
**Scenario:** Your team is preparing AegisAP for a new customer with strict SLA
requirements (p99 latency < 3s for compliance review) and a data residency requirement
(all data must remain in the EU).

Look at the WAF convergence table in Section 5 and the gate list in Section 3.

**Questions:**

1. Which existing acceptance gate most directly addresses the p99 latency requirement?
   What would you add to it to make the check quantitative?
2. Which WAF pillar is least covered by the existing six gates for the EU data residency
   requirement? Propose a new gate that would address it.
3. The new customer requires that all compliance review decisions are stored for 7 years
   for regulatory audit. Which day's artifact chain would you extend to add this
   requirement, and what new gate would you introduce?
4. Map your proposed gates to WAF pillars and add them to the convergence table.
            """),
            mo.accordion({
                "Show solution": mo.md(r"""
**1. Latency gate — existing and proposed:**

The closest existing gate is `eval_regression` — it guards against accuracy
regressions but does NOT measure latency.

To add a quantitative p99 latency check:
- Extend `build/day8/regression_baseline.json` to include a `p99_latency_ms` field
  for `compliance_review` tasks.
- In `gate_eval_regression`, compare current p99 against the baseline and fail the gate
  if the current p99 exceeds 3000ms.
- Alternatively, introduce a dedicated `gate_latency_sla` that reads from Azure Monitor
  (`performanceCounters` or `dependencies` table) using the Day 8/9 KQL patterns.

**2. Data residency — WAF gap and new gate:**

Least covered: **Security** (and Operational Excellence for auditability).

Proposed gate — `gate_data_residency`:
```python
def gate_data_residency() -> GateResult:
    # Read the deployed Container App's region from az containerapp show
    # Verify: location is in West Europe or North Europe
    # Verify: AZURE_OPENAI_ENDPOINT points to an EU endpoint
    # Verify: PostgreSQL server is in an EU region (check POSTGRES_HOST suffix)
    # Verify: Azure Search service region is EU
    ...
```

This gate would fail a release where any data-processing component is configured
to use a non-EU endpoint — catching misconfiguration before user data flows through.

**3. 7-year audit retention:**

Extend the **Day 6** artifact chain (policy review and compliance review decisions).

Day 6 currently writes `build/day6/golden_thread_day6.json` with decision records.
To add 7-year retention:
- Extend the Day 6 notebook to emit decisions to an Azure Storage immutable blob
  container with a retention policy set to 7 years (WORM — Write Once Read Many).
- Introduce `gate_audit_retention` in Day 10:
  - Check that the Storage account has an immutable storage policy configured.
  - Check that the retention period is >= 7 * 365 days.
  - Check that the blob container used by Day 6 is covered by the policy.

**4. Extended WAF convergence table:**

| Pillar | Gate | New / Extended? |
|---|---|---|
| Security | `security_posture` | Existing |
| Security | `gate_data_residency` | **New** |
| Reliability | `resume_safety`, `aca_health` | Existing |
| Cost Optimization | `budget` | Existing |
| Operational Excellence | `gate_audit_retention` | **New** |
| Performance Efficiency | `eval_regression` + p99 extension | Extended |
                """),
            }),
        ]),
    })
    return


@app.cell
def _exercise_4(mo):
    mo.accordion({
        "Exercise 4 — Gate extension implementation": mo.vstack([
            mo.md(r"""
**Task:** Implement a new gate function `gate_data_residency()` that verifies
AegisAP's computational components are all configured for EU deployment.

Specifically, the gate should check:

1. `AZURE_OPENAI_ENDPOINT` contains `.westeurope.` or `.northeurope.` or `.swedencentral.`
2. `AZURE_SEARCH_ENDPOINT` contains one of the same EU region strings
3. `AZURE_POSTGRES_HOST` does not contain `.azure.com` (i.e., a valid custom DSN is
   used, or the check is advisory if DSN is absent)

The gate should return a `GateResult` with `passed=True` only if all three checks pass,
and a descriptive `detail` string listing any failures.

**Bonus:** Where would you add this gate so that `run_all_gates()` includes it?
            """),
            mo.accordion({
                "Show solution": mo.md(r"""
**Implementation:**

```python
import os
from aegisap.deploy.gates import GateResult

_EU_REGIONS = (".westeurope.", ".northeurope.", ".swedencentral.")

def gate_data_residency() -> GateResult:
    failures = []

    # 1. OpenAI endpoint
    oai_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    if oai_endpoint and not any(r in oai_endpoint for r in _EU_REGIONS):
        failures.append(
            f"AZURE_OPENAI_ENDPOINT '{oai_endpoint}' is not in an EU region"
        )

    # 2. Search endpoint
    search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT", "")
    if search_endpoint and not any(r in search_endpoint for r in _EU_REGIONS):
        failures.append(
            f"AZURE_SEARCH_ENDPOINT '{search_endpoint}' is not in an EU region"
        )

    # 3. Postgres host — advisory check
    pg_host = os.environ.get("AZURE_POSTGRES_HOST", "")
    if pg_host and ".azure.com" in pg_host and not any(r in pg_host for r in _EU_REGIONS):
        failures.append(
            f"AZURE_POSTGRES_HOST '{pg_host}' may not be in an EU region"
        )

    if not oai_endpoint and not search_endpoint:
        # Env vars not set (local training) — treat as advisory pass
        return GateResult(
            name="data_residency",
            passed=True,
            detail="No endpoints configured — skipped (training environment).",
        )

    passed = len(failures) == 0
    detail = (
        "All configured endpoints are in EU regions."
        if passed
        else f"Data residency failures: {'; '.join(failures)}"
    )
    return GateResult(
        name="data_residency",
        passed=passed,
        detail=detail,
        evidence={"failures": failures, "eu_regions_checked": list(_EU_REGIONS)},
    )
```

**Adding to `run_all_gates()`:**

In `src/aegisap/deploy/gates.py`, add the new function and append to `ALL_GATES`:

```python
# In ALL_GATES list (after existing gates):
ALL_GATES: list[tuple[str, Callable[..., GateResult]]] = [
    ("security_posture", gate_security_posture),
    ("eval_regression", gate_eval_regression),
    ("budget", gate_budget),
    ("refusal_safety", gate_refusal_safety),
    ("resume_safety", gate_resume_safety),
    ("aca_health", gate_aca_health),
    ("data_residency", gate_data_residency),  # New gate
]
```

`run_all_gates()` iterates `ALL_GATES` and calls each function, so no other
changes are needed. The gate will appear in the release envelope automatically.

**WAF mapping:** Security (data residency), Operational Excellence (audit trail).
                """),
            }),
        ]),
    })
    return


# ---------------------------------------------------------------------------
# Artifact — release_envelope.json
# ---------------------------------------------------------------------------
@app.cell
def _artifact_write(mo, json, Path):
    from aegisap.deploy.gates import run_all_gates as _run_all_gates
    from aegisap.training.checkpoints import run_day10_gate_extension_checkpoint

    # Run all gates (skip live ACA check — not deployed in training)
    _base_results = _run_all_gates(skip_deploy=True)

    # Run the Day 10 checkpoint — writes release_envelope.json and checkpoint artifact
    _checkpoint_path, _checkpoint_payload, _envelope_path, _envelope = (
        run_day10_gate_extension_checkpoint(base_results=_base_results)
    )

    # Display results
    _rows = []
    for _r in _base_results:
        _rows.append({
            "Gate": _r.name,
            "Status": "PASS" if _r.passed else "FAIL",
            "Detail": _r.detail,
        })

    _all_passed = _envelope.get("all_passed", False)
    _checkpoint_passed = _checkpoint_payload["training_gate"]["passed"]
    _ready = _checkpoint_payload.get("ready_for_capstone_review", False)

    mo.vstack([
        mo.callout(
            mo.md(
                "**Artifact written:** `build/day10/release_envelope.json` "
                "and `build/day10/checkpoint_gate_extension.json`"
            ),
            kind="success",
        ),
        mo.table(_rows),
        mo.md(f"""
**Summary:**
- Base gates all passed: `{_all_passed}`
- Checkpoint extension gate passed: `{_checkpoint_passed}`
- Ready for capstone review: `{_ready}`
- Envelope path: `{_envelope_path}`
- Checkpoint path: `{_checkpoint_path}`
        """),
    ])
    return


# ---------------------------------------------------------------------------
# Reflection
# ---------------------------------------------------------------------------
@app.cell
def _reflection(mo):
    mo.accordion({
        "Day 10 Reflection": mo.md(r"""
## Reflect on Day 10

Before moving to the capstone, take a moment to consolidate your understanding.

**Questions to consider:**

1. **Gate dependency chain:** The six gates each consume an artifact from a
   prior day. If you had to run the full pipeline from scratch (Days 1–10),
   which day would you run first and why?

2. **Single gate failure:** The release pipeline requires ALL six gates to pass.
   Is this the right design for all organisations? What circumstances might
   justify a gate override — and what process controls would you require?

3. **The OIDC federation model** relies on Entra ID validating the workflow's
   identity (repo + branch + workflow). What happens if a developer pushes to
   `main` directly, bypassing branch protection? What Azure controls prevent
   this?

4. **Artifact immutability:** The `build/` directory is not committed to git in
   this repo. In a production CI system, where and how would you persist the
   gate artifacts for a given release so that they are auditable six months later?

5. **Day 10 → beyond:** Which of the three "production extension" gates discussed
   in Section 3 (trace-correlation gating, richer eval slicing, multi-phase canary)
   would you prioritise first for your organisation? What would the implementation
   effort look like?
        """),
    })
    return


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
@app.cell
def _summary(mo):
    mo.md(r"""
---

## Day 10 Summary Checklist

| Topic | Key insight |
|---|---|
| ACA revision model | New revisions start at 0% traffic; rollback is a traffic weight change, not a re-deploy |
| OIDC federation | Per-job tokens eliminate stored secrets; credentials are bound to a specific repo + branch + workflow |
| Six acceptance gates | Each gate consumes an artifact from a prior day — the full arc is machine-verified |
| Release envelope | Machine-readable JSON document that serves as structured audit evidence |
| WAF convergence | All five pillars are verified in the Day 10 gate run |
| Continuous improvement | Gate failures tell you which day's artifact needs updating — the feedback loop is intentional |

**Artifacts produced:**
- `build/day10/release_envelope.json` — structured proof of release readiness
- `build/day10/checkpoint_gate_extension.json` — training checkpoint with extension contract verification

**Before you close Day 10, confirm you can:**
- explain why a green training envelope is not the same as authoritative production evidence
- name which upstream artifact feeds each gate and how to rebuild it
- defend a stop-release decision using halt criteria, error budget posture, and release ownership
    """)
    return


# ---------------------------------------------------------------------------
# Forward
# ---------------------------------------------------------------------------
@app.cell
def _forward(mo):
    mo.callout(
        mo.md(r"""
**Congratulations — AegisAP is production-ready.**

You have completed all ten days of the AegisAP Forward Deployed Engineer training.

**What you have built:**

| Capability | Day(s) | Gate |
|---|---|---|
| Agentic invoice processing loop | 1, 4 | `eval_regression` |
| Durable, replay-safe orchestration | 5 | `resume_safety` |
| Policy-governed refusal framework | 6, 7 | `refusal_safety` |
| OIDC-secured, IaC-defined deployment | 8 | `security_posture` |
| Cost-routed, observable inference | 9 | `budget` |
| Machine-verified release pipeline | 10 | All gates |

**Next steps:**

- **Capstone project:** Apply the full arc to a new document type (e.g., utility invoices
  with multi-entity line items).
- **Extend the gate suite:** Implement `gate_data_residency` from Exercise 4.
- **Production hardening:** Add canary traffic shifting with automated halt-and-rollback
  as described in the production extensions discussion.

The architecture is repeatable. The gates are enumerable. The evidence is machine-readable.
Ship with confidence.
        """),
        kind="success",
    )
    return



@app.cell
def _fde_learning_contract(mo):
    mo.md(r"""
    ---
    ## FDE Learning Contract — Day 10: Production Acceptance, Release Evidence, and Change Board Readiness
    
> **Zero-tolerance day** — a hard-fail on any zero-tolerance condition sets the day score to 0.

    ### Four Daily Outputs

    | # | Output type | Location |
    |---|---|---|
    | 1 | Technical build | `LAB_OUTPUT/` |
    | 2 | Design defense memo | `DECISION_MEMOS/` |
    | 3 | Corporate process artifact | `PROCESS_ARTIFACTS/` |
    | 4 | Oral defense prep notes | `ORAL_DEFENSE/` |

    ### Rubric Weights (100 points total)

    | Dimension | Points |
    |---|---|
    | Technical Release Readiness | 25 |
| Evidence Pack Quality | 25 |
| Gate Exception Handling | 20 |
| Executive Communication | 15 |
| Oral Defense | 15 |

    Pass bar: **80 / 100**   Elite bar: **90 / 100**

    ### Oral Defense Prompts

    1. Walk through one gate in your CAB packet that almost failed and explain what evidence tipped the decision.
2. A late executive wants to override one gate for business urgency. What is your response and what is the blast radius if you comply?
3. Who chairs the CAB for this system, what quorum is required, and what documented evidence must exist before the chair can approve?

    ### Artifact Scaffolds

    - `docs/curriculum/artifacts/day10/CAB_PACKET.md`
- `docs/curriculum/artifacts/day10/EXECUTIVE_RELEASE_BRIEF.md`
- `docs/curriculum/artifacts/day10/GATE_EXCEPTION_POLICY.md`

    See `docs/curriculum/MENTAL_MODELS.md` for mental models reference.
    See `docs/curriculum/ASSESSOR_CALIBRATION.md` for scoring anchors.
    """)
    return


if __name__ == "__main__":
    app.run()
