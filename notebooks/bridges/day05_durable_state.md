# Day 05 Bridge — Durable State

## Portal Signal

- The approval task and checkpoint no longer agree.
- Failed-resume or DLQ evidence shows the checkpoint-binding invariant drifted.

## Notebook Proof

- Use the resume-token prototype to compare token checkpoint versus task checkpoint.
- Prove stale resume material must be rejected before side effects execute.

## Production Codification

- `src/aegisap/day5/workflow/resume_service.py`: codify checkpoint-bound token validation.
- `src/aegisap/day5/workflow/checkpoint_manager.py`: codify any supporting state contract changes.

## Export To Production

- Which identifier proved the mismatch?
- Which notebook comparison demonstrated the safe rule?
- Which runtime file must reject the stale path permanently?
