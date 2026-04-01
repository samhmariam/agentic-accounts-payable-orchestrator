# Day 3: Azure AI Services, Framework Selection, and Architectural Choice

## Learning Objectives

By the end of Day 3, trainees can:

- Evaluate Azure AI Services options against a structured decision matrix
- Choose and defend an agent framework with at least three rejected alternatives documented
- Define the boundary between RAG-owned and policy-owned decisions
- Produce a model routing policy that can survive a finance review

## Core Concept: The Architectural Choice Point

Day 3 is the last day where a low-cost framework reversal is possible. Every
choice made today — framework, retrieval boundary, model routing — becomes a
migration cost tomorrow. The mental model is: **"I am choosing what I will pay
to change later."**

## Azure AI Services in Scope

- **Azure OpenAI Service**: model hosting, deployment tiers, PTU vs PAYG
- **Azure AI Foundry**: model catalogue, evaluation, fine-tuning hooks
- **Azure AI Search**: retrieval index, hybrid search, semantic ranking
- **Azure AI Content Safety**: pre-filter and output filter hooks
- **Azure Cognitive Services** (Document Intelligence, Form Recognizer): structured extraction

## Framework Selection Decision

The framework decision is not primarily about features. It is about:

1. **State contract compatibility** — will the state schema migrate cleanly when requirements change?
2. **Tool interface stability** — does the framework's tool abstraction survive a model swap?
3. **Observability surface** — does the framework emit spans that satisfy Day 8 requirements without patching?
4. **Policy overlay integration** — can deterministic policy rules override model decisions at a non-negotiable boundary?

Every rejected alternative must have its strongest single argument documented.
A rejected alternative without a pro-argument was not seriously considered.

## RAG Boundary Decision

The retrieval boundary separates two authority domains:

- **RAG-owned**: enrichment, evidence gathering, context expansion — model may reason over retrieved content
- **Policy-owned**: compliance rules, approval thresholds, zero-tolerance conditions — deterministic code only; model cannot override

A common failure mode: the model is allowed to reason over a retrieved compliance
document and infer an exception. This is not acceptable. Policies must be encoded,
not retrieved.

## FDE Session Guide

**Theory block (45 min):** Framework comparison methodology; RAG boundary patterns; Azure AI Services pricing model.

**Lab block (90 min):** Complete the framework decision matrix; draft model routing policy; define RAG boundary.

**Oral defense (15 min per trainee):** Three prompts below.

## Rubric Weights (100 points total)

| Dimension | Points |
|---|---|
| Correct technical selection | 30 |
| Rejected alternatives strength | 20 |
| Azure implementation realism | 20 |
| Cost / latency / quality trade-off | 15 |
| Oral defense | 15 |

**Pass bar: 80.  Elite bar: 90.**

## Oral Defense Prompts

1. You chose one framework and rejected three. Explain the single strongest argument for each rejected alternative and why that argument was still insufficient.
2. If your framework choice turns out to be wrong at Day 10 scale, what is the migration blast radius in terms of state contracts and tool interfaces?
3. Who in the enterprise approves a framework change after Day 3, and what evidence of migration risk would they require before signing off?

## Artifact Scaffolds

- `docs/curriculum/artifacts/day03/FRAMEWORK_DECISION_MATRIX.md`
- `docs/curriculum/artifacts/day03/MODEL_ROUTING_POLICY_V1.yaml`
- `docs/curriculum/artifacts/day03/RAG_BOUNDARY_DECISION.md`

## Mental Models Applied Today

- **Build an agent or not** — now refined: which agent framework, not just whether to agent
- **Authority and source-of-truth hierarchy** — RAG boundary decision is this model applied
- **Blast radius minimisation** — framework choice blast radius is this day's exercise
- **"Who must approve this"** — framework change authority documented in FRAMEWORK_DECISION_MATRIX.md

## Connections to Previous Days

- Day 1: agent-fit decision now becomes a framework decision
- Day 2: NFRs (latency/cost/accuracy) now have implementation targets

## Connections to Future Days

- Day 4: policy overlay must integrate with the framework chosen today
- Day 7: refusal schema must fit the tool interface of this framework
- Day 10: release evidence includes the framework's observability spans
