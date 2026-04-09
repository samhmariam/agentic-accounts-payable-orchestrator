# Capstone A - Day 10 Kickoff to Day 14 Final CAB Defense

Capstone A is the end-to-end AegisAP production defense.

## Structure

- Day 10 is the foundation checkpoint, not the closeout.
- Days 11, 12, and 13 accumulate the enterprise evidence that distinguishes a release-ready system from a merely green one.
- Day 14 is the final `cab_board` defense and closes Capstone A.

## Required Commands

Build the Day 10 foundation packet:

```bash
uv run python scripts/build_capstone_release_packet.py \
  --trainee-id <your-id> \
  --enhancement-category observability_or_policy \
  --checkpoint-artifact build/day4/checkpoint_policy_overlay.json \
  --checkpoint-artifact build/day8/checkpoint_trace_extension.json \
  --checkpoint-artifact build/day10/checkpoint_gate_extension.json \
  --rollback-command "uv run python scripts/check_all_gates.py --skip-deploy --out build/day10/release_envelope.json" \
  --summary "Describe the bounded enhancement, tests, and release evidence."
```

Build the Day 14 final CAB packet:

```bash
uv run python scripts/build_capstone_final_packet.py \
  --trainee-id <your-id> \
  --summary "Summarise the Day 10 foundation plus Day 11-14 enterprise evidence."
```

## Review Mode

- Day 10 review remains CAB-facing, but it feeds the final capstone rather than replacing it.
- Day 14 is the final Capstone A `cab_board` session.
- The final Day 14 board operates on `build/capstone/<trainee_id>/final_packet.json`.
