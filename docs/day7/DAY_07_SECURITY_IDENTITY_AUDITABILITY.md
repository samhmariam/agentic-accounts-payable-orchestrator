# Day 7 - Security, Identity, and Auditability

Day 7 hardens AegisAP as a reviewable enterprise system. The goal is not to add
new workflow intelligence. The goal is to eliminate hidden credential fallback,
bind sensitive behavior to named identities, and emit durable redacted audit
records for approvals, refusals, and resumptions.

## What Changes

- The runtime uses `DefaultAzureCredential` through the shared security package.
- Search key fallback is forbidden by startup policy and validated in tests.
- The deployed Container App uses system-assigned identity for SDK calls and a
  separate user-assigned identity only for ACR pull.
- Residual secrets move behind Key Vault lookup contracts.
- Sensitive outcomes emit PostgreSQL audit rows and redacted structured logs.

## Day 7 Folder Map

- `docs/day7/` holds the training guide and security reference documents.
- `tests/day7/` holds the Day 7 security and audit regression suite.
- `src/aegisap/security/`, `src/aegisap/audit/`, and `src/aegisap/observability/`
  stay in shared runtime locations because Day 5, Day 6, and the hosted API all
  import them directly.

## Control Model

- Identity plane: runtime API, jobs scaffold, search admin scaffold, developer or ops identities.
- Secret plane: only residual secrets in Key Vault, no Search or OpenAI API key fallback.
- Decision plane: Day 6 review outcomes plus Day 5 approval and resume transitions.
- Trace plane: request and thread correlation with PII redaction before emission.

## Core Files

- [security/config.py](/workspaces/agentic-accounts-payable-orchestrator/src/aegisap/security/config.py)
- [security/credentials.py](/workspaces/agentic-accounts-payable-orchestrator/src/aegisap/security/credentials.py)
- [security/key_vault.py](/workspaces/agentic-accounts-payable-orchestrator/src/aegisap/security/key_vault.py)
- [security/redaction.py](/workspaces/agentic-accounts-payable-orchestrator/src/aegisap/security/redaction.py)
- [audit/models.py](/workspaces/agentic-accounts-payable-orchestrator/src/aegisap/audit/models.py)
- [audit/writer.py](/workspaces/agentic-accounts-payable-orchestrator/src/aegisap/audit/writer.py)
- [training_runtime.py](/workspaces/agentic-accounts-payable-orchestrator/src/aegisap/day5/workflow/training_runtime.py)
- [container_app.bicep](/workspaces/agentic-accounts-payable-orchestrator/infra/modules/container_app.bicep)
- [role_assignments.bicep](/workspaces/agentic-accounts-payable-orchestrator/infra/modules/role_assignments.bicep)

## Sequence

```text
Day 4 recommendation
  -> Day 6 review outcome
  -> Day 5 durable checkpoint
  -> Day 7 audit writer + redacted log emission
  -> approval or refusal state persisted in PostgreSQL
```

## Exit Checks

1. `uv run python scripts/verify_env.py --track full --env`
2. `uv run pytest tests/day7 tests/day6/test_training_runtime_integration.py -q`
3. `az bicep build --file infra/full.bicep`
4. `az bicep build --file infra/modules/container_app.bicep`
5. `az bicep build --file infra/modules/role_assignments.bicep`

Day 7 is complete when:

- no forbidden runtime secret env vars are allowed outside local or test
- Search runtime access remains token-based and local auth stays disabled
- Key Vault diagnostics are configured for `AuditEvent`
- approval, refusal, and resume paths emit redacted audit evidence

## Optional Hosted Check

After deploying the full track runtime, run:

```bash
uv run python scripts/smoke_deployed_app.py --base-url https://<container-app-url>
```

The thread snapshot should show audit rows with redacted evidence summaries and
Day 6 review state.
