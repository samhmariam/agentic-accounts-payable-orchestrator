# ACTION RISK REGISTER

## Purpose

Classify every agent action by reversibility and risk level before implementation,
ensuring irreversible actions have deterministic policy gates and no model discretion.

## Required Headings

1. Action inventory table (action ID, name, action class, reversibility, risk level, policy gate, model-discretion allowed Y/N)
2. Irreversible action treatment — for each irreversible action: the deterministic policy gate, the approval authority, and the test that proves the gate holds
3. Reversible action treatment — rollback mechanism and blast radius if rollback fails
4. Gap analysis — any action where the policy gate is TBD or the test is missing

## Guiding Questions

- Which action would an auditor find most concerning, and how does the register address that concern?
- If the policy gate for an irreversible action fails open, what is the blast radius?
- Which action is classified as reversible but actually has a non-trivial rollback cost?
- Who has authority to add a new irreversible action to this register after Day 4?

## Acceptance Criteria

- Minimum 6 actions classified
- Every irreversible action has a named policy gate and a test that covers the fail-closed path
- Model-discretion allowed = No for all irreversible actions (no exceptions without explicit justification)
- Gap analysis is honest — if a gate is missing, it is listed here
- Risk levels use a consistent classification (e.g., critical / high / medium / low)

## Reversibility Classification Reference

- **Reversible**: can be undone with no external approval and no data loss (e.g., draft a recommendation)
- **Costly to reverse**: can be undone but requires human action or data reconciliation (e.g., send notification)
- **Irreversible**: cannot be undone without a compliance process (e.g., release payment, lock account)
