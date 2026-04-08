# Day 11 - Delegated Identity Rescue Mission

Day 11 is now an actor-binding incident. Start with:

```bash
uv run aegisap-lab incident start --day 11
```

Use `notebooks/day_11_delegated_identity_obo.py` to prove the authority-confusion
bug, then repair the OBO actor-binding boundary and verify with:

```bash
uv run python -m pytest tests/day11/test_actor_verification.py tests/day11/test_obo_flow.py tests/day11/test_obo_simulation.py -q
uv run aegisap-lab artifact rebuild --day 11
```

Success means actor-bound approval only passes when the OBO token and Entra
group evidence agree, and `build/day11/obo_contract.json` is regenerated.
