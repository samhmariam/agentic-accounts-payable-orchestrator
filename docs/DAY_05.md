# Day 5 - Durable State Rescue Mission

Day 5 is now a pause/resume safety incident. Start with:

```bash
uv run aegisap-lab incident start --day 05
```

Use `notebooks/day_5_multi_agent_orchestration.py` to reason about checkpoint
binding, then repair the resume boundary and verify with:

```bash
uv run python -m pytest tests/day5/integration/test_resume_service.py tests/day5/integration/test_idempotent_recommendation_resume.py -q
uv run aegisap-lab artifact rebuild --day 05
```

Success means stale resume material is rejected safely and both
`build/day5/golden_thread_day5_pause.json` and
`build/day5/golden_thread_day5_resumed.json` are regenerated.
