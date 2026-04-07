# Day 07 — Portal-First Safety Surfaces

> **Portal mode:** `Inspect`  
> **Intent:** make security, evaluation, and auditability visible in Azure before they are reduced to test commands or JSON outputs.

## Portal-First Outcome

You can explain which Azure surfaces supply evidence for guardrails, monitoring,
and least-privilege access, and which Day 7 controls remain application-owned.

## Portal Mode

Inspect the Azure evidence surfaces first. If a safety service is not deployed,
use the portal create flow to understand its required shape rather than skipping it.

## Azure Portal Path

1. Open **Access control (IAM)** on Foundry, Search, and Key Vault and confirm the runtime identity is narrow and read-oriented.
2. Open Key Vault and confirm only residual secrets belong there.
3. Open Application Insights or Log Analytics if deployed and identify where Day 7 would gather safety or refusal evidence.
4. If Azure AI Content Safety is part of the tenant strategy, inspect the create or existing resource surface and note how it would sit in the intake boundary.
5. Write down which Day 7 safeguards are not native Azure features: refusal schema, slice thresholds, mandatory escalation recall, and policy reason codes.

## What To Capture

- One screenshot or note proving least-privilege runtime access.
- The expected Azure evidence source for traces, refusals, or security review.
- A short list of Day 7 controls that must still be enforced in code and evaluation logic.

## Handoff To Notebook

- Open [day_7_testing_eval_guardrails.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_7_testing_eval_guardrails.py).
- Use [DAY_07_EVAL_GUARDRAILS_SLICE_GOVERNANCE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_07_EVAL_GUARDRAILS_SLICE_GOVERNANCE.md) plus the Day 7 artifact templates to connect Azure evidence to release-blocking safety decisions.

## Handoff To Automation

After the portal pass, move to the notebook and supporting validation path:

```bash
uv run python -m pytest tests/day7 tests/day6/test_training_runtime_integration.py -q
```
