# Day 11 — Portal-First Delegated Identity

> **Portal mode:** `Inspect`  
> **Intent:** inspect the Entra object model for OBO before the token exchange is hidden behind verifier code.

## Portal-First Outcome

You can point to the app registration, service principal, and approver group that
define delegated authority and explain why managed identity alone is not enough.

## Portal Mode

This is an identity-boundary inspection day. The goal is to see the human actor
story in Entra before relying on a verifier artifact.

## Azure Portal Path

1. Open **Microsoft Entra ID -> App registrations** and inspect the AegisAP backend app.
2. Open **Enterprise applications** and inspect the service principal that performs the OBO exchange.
3. Open the approver **Group** and inspect who is actually in the finance-approval authority set.
4. If your tenant permits it, inspect sign-in or audit logs so the OBO flow is tied to a real actor story.
5. Record which identity objects are human actors and which are service identities.

## What To Capture

- Backend app registration and service principal identifiers.
- The approver group and its intended authority boundary.
- A short explanation of why an app-only identity is insufficient for delegated approval.

## Three-Surface Linkage

- `Portal`: inspect the Entra app registration, service principal, approver group, and any relevant audit surface directly.
- `Notebook`: open [day_11_delegated_identity_obo.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_11_delegated_identity_obo.py) and trace how those Azure objects become actor-bound OBO checks.
- `Automation`: run `scripts/verify_delegated_identity_contract.py` and the Day 11 test path after the delegated-identity story is already clear.
- `Evidence`: the Entra object model, the notebook contract explanation, and `build/day11/obo_contract.json` should agree on who is actually allowed to approve.

## Handoff To Notebook

- Open [day_11_delegated_identity_obo.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_11_delegated_identity_obo.py).
- Use [DAY_11_DELEGATED_IDENTITY.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_11_DELEGATED_IDENTITY.md) and the Day 11 artifact templates to interpret the object model.

## Handoff To Automation

After the portal inspection, verify the same story from the repo:

```bash
uv run python scripts/verify_delegated_identity_contract.py
uv run python -m pytest tests/day11 -q
```
