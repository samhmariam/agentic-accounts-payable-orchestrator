# Day 11 Bridge — Delegated Identity

## Portal Signal

- Entra shows the required approver group and the backend app registration.
- The runtime path can no longer prove the acting user still belongs to the required authority group.

## Notebook Proof

- Use the actor-binding preview to compare actor OID, required group ID, and returned groups.
- Prove payload identity is insufficient without token-backed group evidence.

## Production Codification

- `src/aegisap/identity/actor_verifier.py`: codify group-based actor binding.
- `src/aegisap/identity/obo.py`: only change if the delegated token path drifted.
- `scripts/verify_delegated_identity_contract.py`: keep the artifact aligned with the repaired contract.

## Export To Production

- Which group or actor identifier mattered in the portal?
- Which notebook comparison proved the safe authority rule?
- Which file permanently blocks payload-only approval?
