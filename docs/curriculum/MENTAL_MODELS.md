# AegisAP FDE Mental Models

These eight mental models are **permanent, cumulative, and examinable**. They
appear on Day 1 and are reinforced every day through the end of the programme.
Every oral defense question, zero-tolerance condition, and artifact acceptance
criterion is grounded in at least one of these models.

---

## The Eight Models

### 1. Build an Agent or Not

**Definition:** An agent is justified only when the task requires multi-step
reasoning across variable inputs that cannot be captured by deterministic rules
or a scripted pipeline.

**Rejection signals:** predictable input schema, auditable decision tree exists,
latency or cost constraints favor rules, compliance requires deterministic output.

**Acceptance signals:** inputs are heterogeneous, reasoning requires context from
multiple sources, exception handling dominates the workflow, human review is
rate-limited and agentic pre-filtering creates genuine leverage.

### 2. Zero-Tolerance vs Tunable NFRs

**Definition:** Some NFRs cannot be weakened post-launch without a formal change
board review. Others can be tuned within bounds. Distinguishing them before
implementation prevents silent degradation under cost or velocity pressure.

**Zero-tolerance examples:** PII never leaves the tenant, escalation always
fires on compliance breach, OBO is never bypassed without a formal exception.

**Tunable examples:** p95 latency threshold, cache hit-rate target, mini vs full
model routing boundary.

### 3. Authority and Source-of-Truth Hierarchy

**Definition:** When two data sources disagree, the answer is not in the code
— it is in the governance decision about which source is authoritative. That
decision must be documented, owned, and version-controlled.

**Application:** data authority chart, ADR decision rights section, conflict
runbook, source-of-truth register.

### 4. Control Plane vs Data Plane

**Definition:** Changes to routing rules, policy overlays, model selection,
and thresholds operate on the control plane. Changes to invoice records, PO data,
and payment state operate on the data plane. They have different approval paths,
rollback costs, and blast radii.

**Application:** change classification matrix, CAB packet evidence section.

### 5. Reversible vs Irreversible Actions

**Definition:** Every agent action must be classified before implementation.
Irreversible actions (payment release, account lock, data deletion) require
deterministic policy gates, no model discretion, and explicit human approval.

**Application:** action risk register, HITL contract, policy precedence memo.

### 6. Blast Radius Minimisation

**Definition:** Every architectural decision must be evaluated for its failure
blast radius before it is made. Small blast radius is preferred over feature
completeness when the system operates in a regulated financial workflow.

**Application:** oral defense question 2 on every day, war-game triage order.

### 7. Release Evidence over Intuition

**Definition:** A system is not ready for production because it worked in
staging. It is ready only when every gate has produced affirmative evidence that
can be inspected, signed, and audited. Intuition is not evidence.

**Application:** CAB packet, gate exception policy, release ownership map.

### 8. "Who Must Approve This" Before "How Do We Code This"

**Definition:** Before designing a technical implementation, identify the approval
chain required to deploy and operate it. If the approver chain is unknown, the
design is incomplete.

**Application:** RACI matrix, approval authority model, every ADR decision-rights
section, process-fluency dimension of oral defense.

---

## Day-Presence Matrix

| Model | First appears | Reinforced on |
|---|---|---|
| Build an agent or not | Day 1 | Days 2, 3, 6, 7, 9 |
| Zero-tolerance vs tunable NFRs | Day 2 | Days 4, 7, 9, 10, 12, 14 |
| Authority and source-of-truth hierarchy | Day 2 | Days 3, 5, 6, 11 |
| Control plane vs data plane | Day 4 | Days 6, 8, 10, 13 |
| Reversible vs irreversible actions | Day 4 | Days 5, 7, 11, 12, 13, 14 |
| Blast radius minimisation | Day 1 | All days (oral defense Q2) |
| Release evidence over intuition | Day 8 | Days 9, 10, 12, 14 |
| "Who must approve this" before "how to code this" | Day 2 | All days (oral defense Q3) |

---

## How These Are Examined

Each day's three oral defense prompts map directly to these models:

- **Prompt 1** (rejected alternative) → Build an agent or not; Authority hierarchy; Control vs data plane
- **Prompt 2** (blast radius) → Blast radius minimisation; Reversible vs irreversible
- **Prompt 3** (who must approve) → "Who must approve this"; Release evidence over intuition; Zero-tolerance vs tunable

Zero-tolerance conditions (Days 7, 10, 11, 12, 14) are operationalisations of
models 2, 5, and 8 — the highest-consequence failure modes in the programme.
