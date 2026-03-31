# Day 10 — Deployment & Acceptance Gating · Trainer Guide

> **Session duration:** 4 hours (70 min theory + 2.5 h lab + 20 min retrospective)  
> **WAF Pillars:** Operational Excellence · Security · Cost Optimization · Reliability  
> **Prerequisite:** All Day 0–9 artefacts present; `full` environment deployed  
> **Note:** This is the final day of the bootcamp — leave time for a full retrospective

---

## Session Goals

By the end of Day 10, every learner should be able to:
- Explain ACA's revision model and use it to roll back to a previous revision
- Walk through the GitHub Actions OIDC federation flow without secret rotation
- Articulate each of AegisAP's six implemented acceptance gates and what triggers a failure
- Demonstrate the shared gate runner and the release envelope it emits
- Reflect on which WAF pillar was addressed on each day and the overall architecture

---

## Preparation Checklist

- [ ] `az containerapp revision list --name aegisap-api --resource-group <rg>` lists ≥ 1 revision
- [ ] GitHub Actions workflow file exists at `.github/workflows/` (or Bicep is ready to deploy it)
- [ ] `uv run python scripts/smoke_deployed_app.py` exits 0
- [ ] `uv run pytest tests/ -q` passes
- [ ] Optionally: ACA monitoring dashboard open in Azure Portal
- [ ] `scripts/check_cost_gates.py` has been run to establish budget baseline
- [ ] All evaluation baselines from Day 8–9 present

---

## Theory Segment (70 min)

### Block 1: Azure Container Apps Revision Model (20 min)

**Talking points:**
1. Explain the revision model with a concrete scenario:
   > "We deploy version 1.2.0. A compliance bug is found in the policy review
   > logic. We need to: (a) not lose in-flight cases; (b) roll back immediately;
   > (c) keep the evidence."
2. Draw the revision model:
   ```
   Traffic → 100%                Traffic → 80/20         Traffic → 0/100
              ↓                              ↓                      ↓
         revision-v1.1          revision-v1.1 │ v1.2          revision-v1.2
                                              ↓
                                    (20% of new traffic)
   ```
3. Explain the revision controller properties:
   - `revisionSuffix`: human-readable suffix from the CI tag
   - Traffic weight: zero a revision but keep it alive (for rollback)
   - Health probes: readiness probe must pass before receiving traffic
4. Show the rollback command:
   ```bash
   az containerapp ingress traffic set \
     --name aegisap-api \
     --resource-group <rg> \
     --revision-weight aegisap-api--v1-1=100 aegisap-api--v1-2=0
   ```
   Ask: "Is this a destructive operation?" (No — v1.2 is still alive,
   just receiving 0% traffic. It can be re-enabled without a redeploy.)

---

### Block 2: OIDC Federation and Secretless Deployment (25 min)

**Talking points:**
1. Open with the problem: "In the old model, a GitHub Actions pipeline has
   a `AZURE_CREDENTIALS` secret — a JSON blob with a Service Principal's
   client secret. What happens if that secret leaks?"
2. Show OIDC federation as the solution:
   ```
   GitHub Actions                    Azure
   ──────────────                   ──────────────────────────────────
   Workflow runs on ref              Entra ID Federated Credential reads
   main, job: deploy                 "subject = repo:org/aegisap:ref:refs/heads/main"
         │                                     │
         └──── presents JWT ─────────────────→ validates against GitHub JWKS
                                              │
                                              └──── issues short-lived token
   ```
3. Walk through the actual repo assets that implement this pattern:
   `.github/workflows/deploy-staging.yml`, `.github/workflows/deploy-prod.yml`,
   and the provisioning stack that assigns the deployment identity its roles.
4. Show the Actions workflow steps:
   ```yaml
   - uses: azure/login@v2
     with:
       client-id: ${{ vars.AZURE_CLIENT_ID }}
       tenant-id: ${{ vars.AZURE_TENANT_ID }}
       subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
   ```
   Compare against the secret-based approach. Ask: "What is different about
   the GitHub variables here vs. secrets?" (These are not sensitive — `client-id`
   is only useful if you also control the GitHub action's subject claim.)

---

### Block 3: The Six Acceptance Gates (25 min)

**Talking points:**
1. Frame acceptance gates as "the system applying its own standards to itself":
   > "We enforce that vendor invoices have citations, that escalations never go
   > unreviewed, and that prompts are injection-clean. We enforce the same
   > standards when deploying this system."
2. Walk through each gate:
   - **Security posture**: shared zero-secret and environment policy contract
   - **Evaluation regression**: Day 8 baseline remains above threshold
   - **Budget**: Day 9 routing report stays within daily budget
   - **Refusal safety**: Day 6 malicious-case results meet the refusal threshold
   - **Resume safety**: Day 5 replay evidence reports zero duplicate side effects
   - **ACA health**: target revision is healthy and ready
3. Ask: "Which gate is zero-tolerance? Why?"
   (In this training implementation, the strictest operational signal is
   `resume_safety`: any duplicate side effect is a release blocker. Also remind
   learners that Day 8 thresholds can still encode zero-tolerance metrics.)
4. Show the gate failure flow: if any gate fails, the traffic weight on the
   new revision remains at 0% and an alert fires. The old revision keeps 100%.

---

## Lab Walkthrough Notes

### Key cells to call out in `day10_deployment_gates.py`:

1. **`_run_trigger` and `_gate_results`** — run the shared gate suite. Point to the readable
   output format. Ask learners: "Which gate would catch a regression introduced
   by changing the escalation threshold?"

2. **`_gate_tabs`** — show how each gate exposes enough detail to diagnose the
   upstream missing artifact or failed contract without opening the portal.

3. **`_do_traffic_shift`** — trigger the post-gate traffic shift. Explain that
   the training notebook performs the final shift only after all gates are green.

4. **`_persist`** — show the release envelope being written. This is the deploy
   equivalent of the prior-day build artifacts.

5. Discuss the missing-but-useful production extensions: trace correlation,
   richer synthetic eval slicing, and phased canary automation.

### Expected lab friction points

| Issue | Likely cause | Resolution |
|---|---|---|
| Gate import fails | Notebook or script is importing the wrong gate module | Use `aegisap.deploy.gates` and re-run `python -m py_compile notebooks/day10_deployment_gates.py` |
| ACA health fails | Container App env vars not loaded or revision unhealthy | Load deploy env or run with `--skip-deploy` while teaching the gate structure |
| Budget gate fails | Day 9 report exceeds the ceiling | Re-run Day 9 and inspect `build/day9/routing_report.json` |
| Refusal safety fails | Day 6 adversarial summary is stale or below threshold | Re-run Day 6 and inspect `build/day6/golden_thread_day6.json` |

---

## Common Misconceptions

| Misconception | Correction |
|---|---|
| "ACA is like AKS with less control" | ACA is a higher-level abstraction purpose-built for containerised microservices. For AegisAP's scale and operational model, ACA is the right tool. AKS is appropriate when you need direct node/pod management. |
| "OIDC federation is only for GitHub Actions" | Azure Federated Identity Credentials work with any OIDC-compliant identity provider: GitLab, Kubernetes service accounts, Azure Pipelines, etc. |
| "A passing ACA health check means a deployment is safe" | `aca_health` is only one of six gates. Artifact-backed quality and safety gates are equally important. |
| "Rollback deletes the failed revision" | Rollback sets traffic weight to 0. The revision remains available for investigation and can be re-enabled. Set retention policy to control how long old revisions persist. |

---

## Bootcamp Retrospective (20 min)

Use this time to close the full AegisAP arc. Walk the curriculum map:

| Day | Domain | WAF Pillar |
|-----|--------|------------|
| 0 | Azure Infrastructure | Security, Reliability |
| 1 | Trust Boundaries | Security |
| 2 | Stateful Workflows | Reliability |
| 3 | Retrieval Authority | Performance, Reliability |
| 4 | Explicit Planning | Operational Excellence |
| 5 | Durable State | Reliability |
| 6 | Policy Review | Security |
| 7 | Identity & Audit | Security |
| 8 | Observability | Operational Excellence |
| 9 | Cost & Routing | Cost Optimization |
| 10 | Deployment | All Five |

Ask the room: "Day 10 is labelled 'All Five.' How?"
- **Security**: OIDC no-secrets deployment, security posture gate
- **Reliability**: phased rollout with health probes, instant rollback
- **Cost Optimization**: cost gate blocks over-budget deployments
- **Operational Excellence**: full gate suite, audit trail for every deploy
- **Performance Efficiency**: revision canarying lets you validate latency before full rollout

---

## Discussion Prompts

1. "You're deploying a model update that improves the aggregate compliance
   accuracy from 0.87 to 0.91 but reduces the escalation recall from 1.0
   to 0.98. Which AegisAP gate catches this? Do you release?"

2. "A new employee is added to the GitHub repository. They push a branch
   that runs the deployment workflow. Why does the OIDC federation not issue
   a token to their branch?" (The federated credential is scoped to
   `ref:refs/heads/main`; a PR branch has a different subject claim.)

3. "Under what circumstances would you increase the phased traffic shift
   from three steps (10/30/100) to five steps? What would those steps be?"

---

## Expected Q&A

**Q: How do we handle database migrations with zero downtime in this model?**  
A: AegisAP uses `scripts/apply_migrations.py` as a pre-deploy step in the
workflow. Migrations must be backward-compatible: columns are added but not
dropped in the same migration. Only after the new revision is serving 100%
traffic and has been running for a soak period are breaking column changes
applied in a follow-on migration.

**Q: Should AegisAP use ACA with KEDA for auto-scaling?**  
A: Yes — KEDA (Kubernetes Event-Driven Autoscaling) is native to ACA and
is the recommended scaling mechanism for event-driven workloads. Scaling
on queue depth or HTTP concurrent requests is more precise than CPU-based
scaling. This is a Day 0 Bicep extension and would be in scope for production.

**Q: What is the target time to rollback in production?**  
A: With the ACA traffic weight approach and a pre-warmed previous revision,
rollback is a single API call. Time-to-rollback is < 60 seconds from decision
to old revision serving 100% traffic. The constraint is human decision time,
not system time.

---

## Facilitation Addendum

### Observable Mastery Signals

- Learner can map each Day 10 gate to its upstream artifact or runtime dependency
- Learner can explain why `scripts/check_all_gates.py` and `aegisap.deploy.gates` must stay in sync
- Learner can tell the difference between implemented gates and production-extension ideas

### Intervention Cues

- If a learner starts describing gates that are not implemented, redirect them to the actual gate names in the notebook
- If a learner treats missing upstream artifacts as “just a notebook problem,” pause and reconnect it to release readiness
- If a learner gets stuck on ACA health, let them continue with `--skip-deploy` while preserving the gate model discussion

### Fallback Path

- If Azure deployment access is unavailable, run the gate suite with `--skip-deploy` and use a saved `build/day10/release_envelope.json` as the discussion artifact
- This is an approved day to run one unsignposted failure drill from [INCIDENT_DRILL_RUNBOOK.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/INCIDENT_DRILL_RUNBOOK.md), especially the broken ACA health env-var scenario.

### Exit Ticket Answer Key

1. Day 5 backs `resume_safety`, Day 6 backs `refusal_safety`, Day 8 backs `eval_regression`, and Day 9 backs `budget`.
2. `aca_health` checks live deployment readiness; `security_posture` checks the contract for secrets and identity safety.
3. A strong answer picks trace-correlation or phased canary automation and ties it to real incident response or rollback confidence.

### Time-box Guidance

- Reserve the final 30 minutes for checkpoint review, release-packet discussion, and rubric scoring.
- If ACA access is blocking, switch immediately to `--skip-deploy` and spend the time on gate interpretation and recovery judgment.
- Do not start the release-style defense until the PR-style review cycle from [CAPSTONE_PR_REVIEW.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/CAPSTONE_PR_REVIEW.md) is complete.

### Scoring And Remediation Trigger

- Immediate remediation is required if the learner cannot recover the first failing gate or cannot describe the rollback command.
- A green release envelope without a coherent capstone review packet is not a passing Day 10 outcome.

---

## Final Session Close

> "Across 10 days, AegisAP went from a skeleton with Bicep templates to a
> production-calibrated system: extraction, stateful orchestration, grounded
> retrieval, explicit planning, durable checkpoints, policy review, hardened
> identity, full observability, cost governance, and automated acceptance
> gating. Every Azure best practice applied here came from the Well-Architected
> Framework. Every capability applied here closes a real failure mode in
> financial AI. The notebooks are yours to take further."
