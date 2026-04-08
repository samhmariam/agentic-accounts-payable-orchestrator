# Day 14 - Chaos Command Rescue Mission

Day 14 is now a war-room incident. Start with:

```bash
uv run aegisap-lab incident start --day 14
```

Use `notebooks/day_14_breaking_changes_elite_ops.py` to prove the false-green
trace or rollback story, then repair the elite-operations boundary and verify
with:

```bash
uv run python -m pytest tests/day14/test_breaking_changes.py -q
uv run python scripts/run_chaos_capstone.py
uv run aegisap-lab artifact rebuild --day 14
```

Success means the Day 14 gates respect dual-sink evidence again, the chaos
capstone writes `build/day14/breaking_changes_drills.json`, and the CTO trace
report is regenerated.

## CAPSTONE_B

Day 14 closes the capstone transfer track with the chaos and executive
leadership evidence required for final readiness review.
