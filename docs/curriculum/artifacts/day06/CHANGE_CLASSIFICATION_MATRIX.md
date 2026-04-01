# CHANGE CLASSIFICATION MATRIX

## Purpose

Classify every change type by its blast radius, approval path, and rollback
cost before any changes are deployed to production.

## Required Headings

1. Change taxonomy — define the change classes used (e.g., model change, policy change, data-plane change, control-plane change, infra change)
2. Classification matrix (change type × blast radius × approval path × rollback cost × zero-tolerance impact)
3. Mis-classification risk — which two change types are most commonly confused and why that confusion is dangerous
4. CAB trigger threshold — which change classes require a full Change Advisory Board review
5. Emergency change procedure — for out-of-band changes: authority, evidence, and post-change audit requirement

## Guiding Questions

- Which change type has the highest blast radius if mis-classified as a lower tier?
- If a threshold change is logged as a data change instead of a policy change, what approval step is bypassed?
- Who has the authority to classify a change, and who can challenge that classification?
- What is the fallback if the emergency change procedure is invoked three times in one month?

## Acceptance Criteria

- Minimum 5 change classes defined with clear distinguishing criteria
- Matrix has a value for every cell (no blanks or "varies")
- Mis-classification risk section names the specific wrong approval path that would result
- CAB trigger threshold is explicit (not "major changes")
- Emergency change procedure names an authority role and a maximum frequency or volume threshold
