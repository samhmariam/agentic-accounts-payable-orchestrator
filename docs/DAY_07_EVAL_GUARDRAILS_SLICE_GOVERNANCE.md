# Day 7: Evaluation, Guardrails, Structured Refusal, and Slice Governance

## Learning Objectives

By the end of Day 7, trainees can:

- Design an evaluation regime with slice-level governance and zero-tolerance metrics
- Implement a structured refusal schema that produces auditable typed outcomes
- Articulate the difference between zero-tolerance and tunable metrics in an enterprise context
- Produce eval governance evidence that qualifies for a CAB submission

## Zero-Tolerance Day

This is a zero-tolerance day. Two conditions trigger a hard fail regardless of
total score:

1. **Mandatory escalation missed on a critical slice regression** — releasing when a zero-tolerance slice regressed is not a matter of judgement.
2. **Refusal schema absent for a high-risk action class** — if an action class can be taken without a typed refusal path, the safety architecture is incomplete.

## Core Concept: Aggregate Is Not Enough

An aggregate eval score that improves can mask a critical slice regression.
Financial compliance systems have heterogeneous risk distributions: a 2% error
rate on high-value invoices is categorically different from a 2% error rate on
low-value invoices. The evaluation regime must reflect this.

The mental model: **"Which slice, if it regressed, would trigger a regulatory
question — and is that slice governed independently?"**

## Structured Refusal

Every agent action that can be declined must have a typed refusal path:

- **Refusal code**: machine-readable, actionable by downstream systems
- **Consumer-facing message**: plain language, no internal state leaked
- **Audit record**: fields sufficient for an external auditor to reconstruct the decision
- **Escalation linkage**: who gets notified and what SLA governs their response

An action without a refusal path is an action the system always takes —
regardless of context. That is not safe in a financial workflow.

## FDE Session Guide

**Theory block (45 min):** Slice evaluation architecture; zero-tolerance metric patterns; structured output for refusal.

**Lab block (90 min):** Build eval governance policy; complete slice regression decision log; define refusal reason code catalog.

**Oral defense (15 min per trainee):** Three prompts below.

## Rubric Weights (100 points total)

| Dimension | Points |
|---|---|
| Zero-tolerance metric handling | 30 |
| Slice-based reasoning | 20 |
| Refusal schema quality | 20 |
| Security reasoning | 15 |
| Oral defense | 15 |

**Pass bar: 80.  Elite bar: 90.**

**Zero-tolerance conditions:** (1) mandatory escalation missed on critical slice regression; (2) refusal schema absent for high-risk action class. Either condition overrides total to 0.

## Oral Defense Prompts

1. The aggregate eval score improved but one critical slice regressed. Walk through your decision to block or release and name the approver chain.
2. If your refusal schema is incomplete for one action class, what is the blast radius in terms of audit evidence gaps and regulatory exposure?
3. Who must sign off on a release where a zero-tolerance metric is borderline, and what evidence package is the minimum acceptable for that sign-off?

## Artifact Scaffolds

- `docs/curriculum/artifacts/day07/EVAL_GOVERNANCE_POLICY.md`
- `docs/curriculum/artifacts/day07/SLICE_REGRESSION_DECISION_LOG.md`
- `docs/curriculum/artifacts/day07/REFUSAL_REASON_CODE_CATALOG.md`

## Mental Models Applied Today

- **Zero-tolerance vs tunable NFRs** — this day's core exercise
- **Reversible vs irreversible actions** — refusal schema enforces the irreversible action boundary
- **Blast radius minimisation** — slice governance quantifies the blast radius of a missed regression
- **Release evidence over intuition** — eval evidence is not optional; it is the only acceptable evidence

## Legacy Reference Documents

The following documents from an earlier programme version are preserved for
reference but are superseded by this document for Day 7 assessment:

- `docs/day7/DAY_07_SECURITY_IDENTITY_AUDITABILITY.md` (legacy topic: identity and auditability — topic moved to Day 11)

## Connections

- **Day 4**: policy overlay provides the deterministic rules that refusal codes enforce
- **Day 10**: eval governance evidence package feeds the CAB packet
- **Day 11**: security and identity reasoning deepens the refusal audit record design
