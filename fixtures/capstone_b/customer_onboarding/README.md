# Customer Onboarding Fixtures — Capstone B (Secondary Domain)

Two trainee-visible cases for the customer onboarding secondary transfer domain.

## Case Index

| File | Description | HITL trigger? | Expected outcome |
|---|---|---|---|
| `onboarding_001_standard.json` | Standard enterprise onboarding — all required steps complete | No | provisioned |
| `onboarding_002_compliance_hold.json` | Compliance attestation not yet submitted | Yes | pending_compliance_review |

## Schema Reference

Customer onboarding uses a different schema from both invoices and claims.
Key fields:

- `onboarding_id`: unique identifier (format ON-NNNNNN)
- `customer_org_id`: enterprise customer identifier
- `contact_role`: primary contact role at the customer
- `contract_ref`: signed contract reference
- `compliance_attestation_status`: submitted / pending / not_required
- `requested_tier`: product tier being provisioned
- `estimated_seats`: number of user seats
- `identity_provisioning_status`: completed / pending / blocked

## Corroboration Use

Assessors may introduce these cases in Day 12/13 oral defenses as a second
transfer domain to verify that the trainee understands the pattern generally,
not just in claims intake. They are not the primary scoring domain for any day.
