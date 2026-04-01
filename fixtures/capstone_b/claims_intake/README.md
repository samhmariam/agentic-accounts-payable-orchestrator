# Claims Intake Fixtures — Capstone B

Five trainee-visible cases for the DME (durable medical equipment) claims
intake transfer domain.

## Case Index

| File | Description | HITL trigger? | Expected outcome |
|---|---|---|---|
| `claim_001_routine.json` | Routine low-value claim | No | auto_approved |
| `claim_002_high_value.json` | High-value claim above threshold | Yes | pending_adjudicator_review |
| `claim_003_missing_auth.json` | Missing authorisation reference | No | refused — missing_auth |
| `claim_004_code_mismatch.json` | Procedure/diagnosis code inconsistency | No | refused — code_mismatch |
| `claim_005_duplicate.json` | Duplicate claim number | No | refused — duplicate_detected |

## Schema Reference

Claims use a different schema from AegisAP invoices. Key fields:

- `claim_number`: unique identifier (format CL-NNNNNN)
- `claimant_id`: patient identifier (anonymised in these fixtures)
- `provider_id`: DME supplier identifier
- `service_date`: date of service delivery
- `procedure_codes[]`: list of HCPCS/CPT codes
- `diagnosis_codes[]`: ICD-10 codes
- `billed_amount_usd`: total amount billed
- `authorisation_ref`: payer pre-authorisation reference
- `payer_id`: insurance payer identifier

## Transfer Note

Do not apply AegisAP invoice field names in your implementation. The schema
is intentionally different to test domain transfer, not field mapping.
