# Day 8: IaC, Identity Planes, and Secure Release Ownership

## Learning Objectives

By the end of Day 8, trainees can:

- Design an IaC structure that enforces identity plane separation
- Produce a security review packet sufficient for a CISO to approve
- Define release ownership with deputy coverage and break-glass audit requirements
- Build a drift response playbook that does not rely on tribal knowledge

## The Release Evidence Standard

Day 8 introduces the principle: **"Release evidence over intuition."** A system
is not good because it worked in staging. A system is ready for production only
when every gate has produced affirmative evidence that can be inspected, signed,
and audited.

The IaC and identity plane work today generates the structural evidence layer
that Days 9 and 10 build on.

## Identity Planes: The Three-Tier Model

| Plane | Identity type | Purpose | Key risk if conflated |
|---|---|---|---|
| Workload | Managed Identity | Runtime authentication to AI/storage | Scope creep, credential theft |
| Pipeline | Federated credential | CI/CD authentication | Pipeline compromise → full deployment access |
| Admin | Entra group + PIM | Break-glass and operational access | Permanent privileged access, no audit trail |

Conflating planes is the most common identity mistake in agentic systems.
If the workload identity can deploy infrastructure, the blast radius of a
compromised invoice processing job is the entire infrastructure estate.

## IaC Correctness Requirements

- Every resource must have a managed identity assignment (no connection strings)
- Private endpoints must be declared in IaC — no console-only configuration
- Role assignments must be least-privilege, documented in the security review packet
- Drift must be detectable: state backend, drift detection job, or equivalent

## Secure Release Ownership

Every element of the release process has a human owner. The pipeline does not
own anything — a human role does. The release ownership map must name:

- Who can trigger a deployment
- Who can approve a deployment
- Who holds rollback authority and for how long after go-live
- Who is the first call if the pipeline identity drifts

## FDE Session Guide

**Theory block (45 min):** Identity plane patterns; federated credential configuration; IaC drift detection.

**Lab block (90 min):** Complete release ownership map; build security review packet; write drift response playbook.

**Oral defense (15 min per trainee):** Three prompts below.

## Rubric Weights (100 points total)

| Dimension | Points |
|---|---|
| IaC correctness | 25 |
| Identity / security reasoning | 25 |
| Ownership clarity | 20 |
| Review packet quality | 15 |
| Oral defense | 15 |

**Pass bar: 80.  Elite bar: 90.**

## Oral Defense Prompts

1. Which IaC pattern did you choose over an alternative and what is the security consequence of the rejected approach?
2. If federated credentials drift and the pipeline loses access at 2am, what is the blast radius and who is the first call?
3. Who owns the release machinery in production, and what evidence would a platform team require before granting break-glass access?

## Artifact Scaffolds

- `docs/curriculum/artifacts/day08/RELEASE_OWNERSHIP_MAP.md`
- `docs/curriculum/artifacts/day08/SECURITY_REVIEW_PACKET.md`
- `docs/curriculum/artifacts/day08/DRIFT_RESPONSE_PLAYBOOK.md`

## Mental Models Applied Today

- **Release evidence over intuition** — this day introduces the model
- **Control plane vs data plane** — identity planes are the control plane for today's work
- **Blast radius minimisation** — identity plane conflation blast radius is today's key exercise
- **"Who must approve this"** — release ownership map operationalises this model

## Legacy Reference Documents

The following documents from an earlier programme version are preserved for
reference but are superseded by this document for Day 8 assessment:

- `docs/day8/DAY_08_OBSERVABILITY_AND_RELIABILITY.md` (legacy topic: observability — moved to Day 9)
- `docs/day8/FAILURE_TAXONOMY.md` (legacy)
- `docs/day8/LATENCY_BUDGETS.md` (legacy)
- `docs/day8/OBSERVABILITY_CONTRACT.md` (legacy)
- `docs/day8/RETRY_POLICY.md` (legacy)

## Connections

- **Day 7**: security review packet includes the eval governance evidence
- **Day 9**: observability and cost monitoring depend on the identity configuration done today
- **Day 10**: security review packet feeds the CAB submission directly
- **Day 11**: OBO flows depend on the identity planes established today
