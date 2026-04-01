# Day 10: Deployment and Acceptance Gating

Day 10 turns AegisAP from a training runtime into a controlled release target.
The goal is not just “the app deploys.” The goal is that a new Azure Container
Apps revision is promoted only when deployment, observability, cost, safety,
and resume behavior all pass machine-checked gates.

## Release Model

- One deployable HTTP service image: `docker/Dockerfile.api`
- One worker artifact image for eval and replay checks: `docker/Dockerfile.worker`
- Staging is the automatic release-candidate environment
- Production is manual promotion of a previously staging-approved SHA
- Azure Container Apps revisions are the rollback unit

## Runtime Contract

The deployable API exposes these release-facing endpoints in addition to the
existing Day 4 and Day 5 routes:

- `GET /health/live`
- `GET /health/ready`
- `GET /version`
- `POST /workflow/run`
- `POST /workflow/resume/{case_id}`

`/health/live` proves only process health. `/health/ready` proves the app is
fully initialized for traffic: tracing configured, secret access viable, and
database reachability satisfied for the active environment.

## Deployment Path

The Day 10 deployment path is GitHub Actions + Azure OIDC + SHA-tagged images.

1. CI validates Python, tests, Bicep, and both Dockerfiles.
2. `deploy-staging.yml` builds and pushes `aegisap-api:<sha>` and
   `aegisap-worker:<sha>`, deploys a new staging ACA revision, waits for
   readiness, then runs smoke and acceptance gates.
3. Only a SHA with a successful staging deployment is eligible for
   `deploy-prod.yml`.
4. Production deploys the exact same SHA as a new immutable ACA revision.

## Acceptance Gates

Day 10 release gates are implemented as code under `scripts/` and `evals/`.

- Deployment gate:
  build, push, deploy, and smoke must succeed without portal edits.
- Trace correlation gate:
  the same workflow run must be discoverable in Azure Monitor and LangSmith.
- Synthetic evaluation gate:
  synthetic suite thresholds must hold for faithfulness, compliance accuracy,
  and mandatory-escalation recall.
- Cost gate:
  workflow cost ceilings must hold by case class, not just by deployment.
- Malicious refusal gate:
  all adversarial cases must end in structured refusals with no side effects.
- Resume replay gate:
  pause/resume must not duplicate side effects or drift the final output.
- Secret posture gate:
  the deploy path must not rely on registry credentials, raw LangSmith keys, or
  other forbidden runtime fallback secrets.

## Managed Identity and Secrets

Day 10 keeps the Day 7 security contract intact:

- ACR pull uses managed identity
- the app uses Key Vault access via managed identity
- raw runtime secrets are not the deployment default
- registry username/password fallback is out of policy

The deploy workflows expect infra and identity to exist as code. No portal edits
should be required to make staging or production healthy.

## Staging Verification Sequence

The post-deploy staging flow is:

1. `GET /health/live`
2. `GET /health/ready`
3. `GET /version`
4. one happy-path workflow run
5. one approval resume
6. trace correlation check across Azure Monitor and LangSmith
7. synthetic and malicious suites
8. cost gate
9. replay safety gate

If any one of those fails, the release candidate is not releasable.

## Production Promotion

Production promotion is manual and protected. The production workflow:

- accepts a specific SHA
- verifies that SHA already passed `deploy-staging.yml`
- deploys a new ACA revision
- runs smoke and trace-correlation checks
- records the previous active revision as the rollback target

If post-deploy validation fails, rollback should happen by activating the prior
good ACA revision, not by rebuilding old code.

---

## FDE Rubric — Day 10 (100 points)

| Dimension | Points |
|---|---|
| Technical release readiness | 25 |
| Evidence pack quality | 25 |
| Gate exception handling | 20 |
| Executive communication | 15 |
| Oral defense | 15 |

**Pass bar: 80.  Elite bar: 90.**

**Zero-tolerance conditions:** (1) pass declared when gate evidence is absent; (2) gate exception approved without required authority or expiry. Either condition overrides total to 0.

## Oral Defense Prompts

1. Walk through one gate in your CAB packet that almost failed and explain what evidence tipped the decision.
2. A late executive wants to override one gate for business urgency. What is your response and what is the blast radius if you comply?
3. Who chairs the CAB for this system, what quorum is required, and what documented evidence must exist before the chair can approve?

## Artifact Scaffolds

- `docs/curriculum/artifacts/day10/CAB_PACKET.md`
- `docs/curriculum/artifacts/day10/EXECUTIVE_RELEASE_BRIEF.md`
- `docs/curriculum/artifacts/day10/GATE_EXCEPTION_POLICY.md`
