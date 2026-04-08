# Day 6 - Review Boundary Rescue Mission

Day 6 now begins with an injection-tainted review incident. Start with:

```bash
uv run aegisap-lab incident start --day 06
```

Use `notebooks/day_6_data_ml_integration.py` to inspect the review boundary,
repair prompt-injection detection or authority checks, and verify with:

```bash
uv run python -m pytest tests/day6/test_review_gate.py tests/day6/test_training_runtime_integration.py -q
uv run aegisap-lab artifact rebuild --day 06
```

Success means the review gate again refuses unsafe progression and
`build/day6/golden_thread_day6.json` is refreshed.
