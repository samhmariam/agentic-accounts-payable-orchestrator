# Claims Intake Fixtures — Capstone B

Five trainee-visible cases for the DME (durable medical equipment) claims
intake transfer domain.

## Case Index

| File | Description | HITL trigger? | Expected outcome |
|---|---|---|---|
| `claim_001_routine.json` | Routine low-value claim | No | auto_approved |
| `claim_002_high_value.json` | High-value claim above threshold | Yes | pending_adjudicator_review |
| `claim_003_missing_auth.json` | Missing prior-authorisation reference | No | refused — missing_auth |
| `claim_004_code_mismatch.json` | Procedure/diagnosis code inconsistency | No | refused — code_mismatch |
| `claim_005_duplicate.json` | Duplicate resubmission via related-claim reference | No | refused — duplicate_detected |

## Hostile Schema Reference

Claims use a FHIR-like `Claim` payload rather than flat AP fields. The adapter
must flatten these nested shapes before shared fail-closed logic can run:

- `identifier[].type.coding[].code` and `identifier[].value`
- `item[].productOrService.coding[].code`
- `diagnosis[].diagnosisCodeableConcept.coding[].code`
- `supportingInfo[].category.coding[].code`
- `supportingInfo[].valueReference.identifier.value`
- `related[].relationship.coding[].code`
- `related[].claim.identifier.value`
- `total.value`

## Transfer Note

Do not rename these fixtures into invoice-shaped keys. The point of the lab is
to build an adapter boundary from hostile healthcare payloads into reusable
control signals.
