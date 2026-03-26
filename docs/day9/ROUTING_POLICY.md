# Day 9 Routing Policy

## Task Classes

- `extract`
- `classify`
- `retrieve_summarise`
- `plan`
- `compliance_review`
- `reflection`
- `final_render`

## Defaults

- `extract` and narrow `classify` default to the light deployment.
- `plan`, `reflection`, and `compliance_review` default to the strong
  deployment.
- `final_render` can use the light deployment only when it is not rendering a
  refusal or escalated justification.

## Escalators

The router promotes to the strong deployment when any of these are true:

- contradictory evidence exists
- retrieval confidence is below threshold
- `high_value`, `missing_po`, `bank_details_changed`, or `new_vendor` risk flags
  are present
- cross-border or multi-currency tax risk is present
- prior reflection or refusal signals are present

These rules are deterministic so they can be audited from traces and state
snapshots.
