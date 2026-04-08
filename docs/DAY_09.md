# Day 9 - Routing Regression Rescue Mission

Day 9 is now a routing and budget-control incident. Start with:

```bash
uv run aegisap-lab incident start --day 09
```

Use `notebooks/day_9_scaling_monitoring_cost.py` to prove the bad routing
decision, then repair the routing policy and verify with:

```bash
uv run python -m pytest tests/day9/test_routing_policy.py tests/day9/test_cache_and_cost.py tests/day9/test_runtime_day9_contract.py -q
uv run aegisap-lab artifact rebuild --day 09
```

Success means risky work routes back to the strong tier and
`build/day9/routing_report.json` is regenerated.
