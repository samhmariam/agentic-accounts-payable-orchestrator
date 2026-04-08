# Day 3 - Retrieval Authority Rescue Mission

Day 3 now begins from a live retrieval-authority incident instead of a framework
tour. Start with:

```bash
uv run aegisap-lab incident start --day 03
```

Then open `notebooks/day_3_azure_ai_services.py`, investigate the ranking failure,
repair the authority boundary, and verify with:

```bash
uv run python -m pytest tests/day3/test_vendor_authority_ranking.py tests/day3/test_day3_exit_check.py -q
uv run aegisap-lab artifact rebuild --day 03
```

Success means structured authority outranks stale email history again and
`build/day3/golden_thread_day3.json` is regenerated.
