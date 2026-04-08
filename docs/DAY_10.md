# Day 10 - Release Board Rescue Mission

Day 10 is now a false-green release incident. Start with:

```bash
uv run aegisap-lab incident start --day 10
```

Use `notebooks/day_10_production_operations.py` to inspect the release-envelope
logic, then repair the go/no-go boundary and verify with:

```bash
uv run python -m pytest tests/day10/test_deployment_contract.py tests/day10/test_release_security.py tests/day10/test_release_envelope.py tests/training/test_checkpoints.py tests/api/test_app.py -q
uv run aegisap-lab artifact rebuild --day 10
```

Success means any failing gate blocks release readiness again and both
`build/day10/release_envelope.json` and
`build/day10/checkpoint_gate_extension.json` are regenerated.
