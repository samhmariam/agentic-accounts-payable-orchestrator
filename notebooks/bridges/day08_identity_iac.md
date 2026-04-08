# Day 08 Bridge — Identity And IaC

## Portal Signal

- Azure AI Search IAM shows the runtime principal holding the wrong role.
- Container App identity wiring or search auth posture no longer matches least privilege.

## Notebook Proof

- Use the assignment preview and contract check.
- Prove runtime must be reader-only and local auth must remain disabled.

## Production Codification

- `infra/modules/role_assignments.bicep`: codify the correct role binding.
- `infra/foundations/search_service.bicep`: codify the auth posture.
- `infra/modules/container_app.bicep`: only change if the runtime principal wiring drifted.

## Export To Production

- Which principal and role were wrong in the portal?
- Which notebook snippet proved the correct contract?
- Which Bicep resource must change to make the fix permanent?
