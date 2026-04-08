# Day 12 - Private Network Rescue Mission

Day 12 is now a network-isolation incident. Start with:

```bash
uv run aegisap-lab incident start --day 12
```

Use `notebooks/day_12_private_networking_constraints.py` to prove the static
and live posture drift, then repair the private-network checker and verify with:

```bash
uv run python -m pytest tests/day12/test_network_posture.py tests/day12/test_bicep_policy_checker.py -q
uv run aegisap-lab artifact rebuild --day 12
```

Success means the static checker catches public endpoints again and the Day 12
artifacts under `build/day12/` are regenerated.

## CAPSTONE_B

Day 12 feeds the capstone transfer track by establishing the private-network
posture and exception evidence that later release decisions must inherit.
