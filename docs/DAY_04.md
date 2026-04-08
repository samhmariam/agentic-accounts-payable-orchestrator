# Day 4 - Fail-Closed Planning Rescue Mission

Day 4 is now a combined-risk planning incident. Start with:

```bash
uv run aegisap-lab incident start --day 04
```

Use `notebooks/day_4_single_agent_loops.py` to prove the overlay and
recommendation gate still fail closed, then ship the repair and verify with:

```bash
uv run python -m pytest tests/day4/unit/planning/test_policy_overlay.py tests/day4/unit/recommendation/test_recommendation_gate.py -q
uv run aegisap-lab artifact rebuild --day 04
```

Success means the risky slice always routes to manual review and
`build/day4/golden_thread_day4.json` is refreshed.
