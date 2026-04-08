# Day 10 Bridge — Release Evidence

## Portal Signal

- The candidate revision or upstream gate is unhealthy.
- The generated release envelope still looks green.

## Notebook Proof

- Use the release-envelope preview with mixed gate results.
- Prove any failed gate must force a non-green release outcome.

## Production Codification

- `src/aegisap/deploy/gates.py`: codify release aggregation logic.
- `scripts/check_all_gates.py`: codify CLI evidence packaging.
- `src/aegisap/training/checkpoints.py`: only change if checkpoint evidence is miswired.

## Export To Production

- Which gate was failing in reality?
- Which notebook case proved the false-green path?
- Which file now enforces the permanent go or no-go decision?
