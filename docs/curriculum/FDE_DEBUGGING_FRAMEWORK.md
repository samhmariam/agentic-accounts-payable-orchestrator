# FDE Debugging Framework

Use this every time a learner hits a failing gate, broken Azure surface, or
false-green artifact. The standard is not "try things until tests pass." The
standard is evidence-first translation from observed cloud state to durable
code.

## OODA For Azure

### Observe

- Name the exact metric, trace, log, or portal blade that proves the system is broken.
- Capture the failing signal before changing code.
- State the blast radius if the signal is ignored.

### Orient

- Identify where the broken behavior lives in Azure, the notebook, and the repo.
- Decide whether the defect is control plane, data plane, identity, networking, or release logic.
- Compare the live state to the artifact or gate that claimed things were safe.

### Decide

- Reproduce the broken state in the notebook or a narrow local preview.
- Prove the smallest repair that restores the contract.
- Name the exact file or IaC module that must change to make the fix durable.

### Act

- Codify the repair in `src/`, `infra/`, or `scripts/`.
- Run the verification commands and rebuild the artifact.
- When Azure access is available, run `uv run aegisap-lab audit-production` to prove the cloud state matches the code.

## Required Language

- `Prove it.`
- `What is the blast radius?`
- `Automate this.`
- `Show me the telemetry.`

## Failure Pattern To Correct Immediately

If a learner can explain the portal but cannot name the permanent code or IaC
change, the diagnosis is incomplete. Portal understanding without codification
is ClickOps debt, not FDE readiness.
