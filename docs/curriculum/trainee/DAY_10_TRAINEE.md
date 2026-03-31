# Day 10 — Deployment & Acceptance Gating · Trainee Pre-Reading

> **WAF Pillars:** Operational Excellence · Reliability · Security  
> **Time to read:** 25 min  
> **Lab notebook:** `notebooks/day10_deployment_gates.py`

---

## Learning Objectives

By the end of Day 10 you will be able to:

1. Explain Azure Container Apps' revision model and how it enables zero-downtime releases.
2. Describe GitHub Actions OIDC federation and why it eliminates long-lived credentials.
3. List the six implemented Day 10 gates and describe what each verifies.
4. Run the shared gate runner and interpret the release envelope it emits.
5. Distinguish between the implemented training gates and production-extension gates that are discussed but not yet automated in this repo.

---

## 1. Azure Container Apps Revision Model

**Azure Container Apps (ACA)** is a serverless container platform built on Kubernetes.
Its **revision model** is the key feature for safe deployments:

```
images pushed → new revision created (inactive)
              → traffic weight = 0%
              → acceptance gates run
              → on pass: traffic shift staging (100%) or prod (phased)
              → on fail: previous revision retains all traffic
```

### Key concepts

| Concept | Description |
|---|---|
| **Revision** | An immutable snapshot of a container image + config. A new revision is created for every code or config change. |
| **Traffic split** | Percentage of requests routed to each revision (e.g., 90% stable / 10% canary) |
| **Rollback** | Shift 100% traffic back to a previous revision — no re-deploy required |
| **Inactive revision** | A revision that exists but receives 0% traffic — useful for comparing or quick rollback |

### Azure best practice
- Tag images with the full Git SHA (`aegisap-api:<sha>`). Never use `latest` in
  a production deployment — it makes rollback ambiguous.
- Use ACA's `--revision-suffix` flag to give each revision a human-readable name
  (e.g., `rev-20240326-a1b2c3`) for easier identification in the portal.
- Keep at least two previous revisions in an inactive state in case an emergency
  rollback is needed.

---

## 2. GitHub Actions OIDC Federation

Traditional CI/CD uses a Service Principal with a client secret stored as a
GitHub Actions secret. This has two problems:
- The secret must be rotated
- A compromised GitHub Actions run can exfiltrate the secret

**OIDC (OpenID Connect) federation** eliminates this entirely:

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
Entra ID validates: correct repo, correct branch, correct workflow?
    │
    ▼
Entra ID issues an access token (valid for this job only)
    │
    ▼
Azure CLI / SDK calls use this token — no secret ever stored
```

### Why this is better

| Property | Service Principal + secret | OIDC federation |
|---|---|---|
| Secret lifetime | Months (must rotate) | Minutes (per-job token) |
| Secret storage | GitHub Secrets (at risk) | None — no secret exists |
| Scope | Any workflow can use it | Bound to specific repo + branch + workflow |
| Rotation burden | Manual | None |

### Azure best practice
- Configure the federated credential to bind to the **specific branch** (`refs/heads/main`)
  and **specific workflow** (`deploy-staging.yml`). Do not use wildcard subjects.
- Grant the deployment identity only the minimum roles needed: `AcrPush` on the
  registry, `Contributor` on the Container App resource group — not subscription-wide.

---

## 3. The Six Acceptance Gates

Day 10's release pipeline enforces six machine-checked gates before promoting
any revision to production:

| Gate | What it checks | Tool |
|---|---|---|
| **Security posture** | No forbidden runtime secret fallback and the environment matches the security contract | `aegisap.deploy.gates.gate_security_posture()` |
| **Evaluation regression** | Day 8 regression baseline does not show a score drop below threshold | `aegisap.deploy.gates.gate_eval_regression()` |
| **Budget** | Day 9 sample ledger stays within the configured daily ceiling | `aegisap.deploy.gates.gate_budget()` |
| **Refusal safety** | Day 6 malicious-case results meet the minimum structured refusal rate | `aegisap.deploy.gates.gate_refusal_safety()` |
| **Resume safety** | Day 5 resume artifact reports zero duplicate side effects | `aegisap.deploy.gates.gate_resume_safety()` |
| **ACA health** | The target Container App revision reports healthy and ready | `aegisap.deploy.gates.gate_aca_health()` |

All six gates must pass for a staging deployment to be eligible for production
promotion. Any single gate failure blocks the release.

---

## 4. Security Posture In Practice

The Day 10 `security_posture` gate fails the release if any of these
conditions are detected:

| Condition | Why it fails the gate |
|---|---|
| Container image contains `AZURE_OPENAI_API_KEY` env var | Key should be absent; runtime uses Managed Identity |
| ACR pull is configured with username/password | Must use Managed Identity with `AcrPull` role |
| `LANGSMITH_API_KEY` is absent from Key Vault | Should be stored as a Key Vault secret, not a plain env var |
| `AEGISAP_POSTGRES_DSN` is set in staging or production | Password-based DSN forbidden; Entra auth required |

In training, the notebook reads the same contract through the shared gate runner
used by `scripts/check_all_gates.py`.

---

## 5. Production Extensions

The current training notebook can shift traffic to the latest healthy revision
after all six implemented gates pass. The following are valuable production
extensions, but they are not yet automated as notebook gates in this repo:

- Trace-correlation gating across Azure Monitor and LangSmith
- Richer synthetic evaluation slicing beyond the Day 8 regression baseline
- Multi-phase canary traffic shifting with automated halt-and-rollback rules

These are worth discussing with trainees because they are common next steps when
hardening a real deployment pipeline.

### Rollback command

Full rollback from any phase takes under two minutes:

```bash
az containerapp revision set-mode --name aegisap-api \
  --resource-group rg-aegisap-prod \
  --mode multiple

az containerapp ingress traffic set --name aegisap-api \
  --resource-group rg-aegisap-prod \
  --revision-weight "aegisap-api--stable=100"
```

This shifts 100% of traffic back to the previous revision with zero
redeployment.

---

## 6. Applying the Azure Well-Architected Framework

Day 10 is where all five WAF pillars converge:

| Pillar | Day 10 implementation |
|---|---|
| **Security** | OIDC federation, Managed Identity pull, security posture gate |
| **Reliability** | Revision model, rollback procedure, ACA health gate, resume replay gate |
| **Cost Optimization** | Budget gate and routing-cost evidence from Day 9 |
| **Operational Excellence** | IaC-only deployments, gate automation, no portal edits in the release path |
| **Performance Efficiency** | Regression baselines and optional canary-style monitoring extensions |

---

## Glossary

| Term | Definition |
|---|---|
| **Revision** | An immutable ACA deployment snapshot; the rollback unit |
| **Traffic split** | Percentage allocation of incoming requests across active revisions |
| **OIDC federation** | Short-lived token-based authentication between CI/CD and Azure — no stored secrets |
| **Acceptance gate** | A machine-checked condition that must pass before a revision can proceed to production |
| **Canary release** | Routing a small percentage of traffic to a new revision to verify behaviour before full rollout |
| **Secret posture** | The state of how secrets are managed — correct posture means no raw credentials in the runtime |
| **SHA-tagged image** | A container image tagged with the Git commit SHA — ensures traceability and unambiguous rollback |

---

## Check Your Understanding

1. What is an ACA revision, and how does the traffic split model enable zero-downtime rollback?
2. Why is OIDC federation safer than storing a Service Principal secret in GitHub Actions secrets?
3. List the six implemented Day 10 acceptance gates. Which one depends on the Day 5 artifact?
4. What four conditions cause the security posture gate to fail?
5. Which Day 10 production extensions are discussed but not yet automated in the notebook?

---

## Lab Readiness

- **Lab duration:** 2.5 hours
- **Required inputs:** Day 6, Day 8, and Day 9 artifacts plus optional ACA deployment env vars
- **Expected artifact:** `build/day10/release_envelope.json`

### Pass Criteria

- All required gate results are visible and the release envelope records the final gate state.
- The training checkpoint gate writes `build/day10/checkpoint_gate_extension.json`.
- The learner can explain the exact rollback or recovery command for the first failing gate.

### Common Failure Signals

- The notebook cannot import the shared gate module
- Day 6, Day 8, or Day 9 artifacts are missing
- ACA health fails because deployment environment variables are not loaded

### Exit Ticket

1. Which Day 10 gates are directly backed by Day 5, Day 6, Day 8, and Day 9 artifacts?
2. Why is `aca_health` kept separate from `security_posture`?
3. Which gate would you extend first for a production rollout, and why?

### Remediation Task

Rebuild the release envelope with:

```bash
uv run python scripts/check_all_gates.py --skip-deploy --out build/day10/release_envelope.json
```

Then explain which upstream artifact caused the first failing gate.

### Stretch Task

Design a trace-correlation gate that proves the same `workflow_run_id` is
discoverable in both Azure Monitor and LangSmith without requiring manual portal inspection.

### Scoring And Remediation Trigger

- Daily pass requires mostly 3s on the rubric, with no 1 in `Technical Correctness` or `Security Reasoning`.
- Immediate remediation is required if the learner cannot recover a failing gate or cannot build the capstone review packet from the release evidence.
