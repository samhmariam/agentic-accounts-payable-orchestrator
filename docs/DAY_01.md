# Day 1 - Trust Boundary Rescue Mission

Day 1 now begins with a live incident, not a theory tour. The learner injects a
broken Day 1 environment, proves the trust-boundary failure, prototypes the fix
in Marimo, then patches the real deterministic code under `src/`.

## Incident Entry

```bash
uv run aegisap-lab incident start --day 01
```

## Verification Commands

```bash
uv run python -m pytest tests/test_day_01_money.py tests/test_day_01_fixtures.py -q
uv run aegisap-lab artifact rebuild --day 01
```

## Training Artifact

The repaired path should still regenerate `build/day1/golden_thread_day1.json`.

## Exit Check

Day 1 succeeds when:

- the mixed-separator incident is reproduced and explained correctly
- the deterministic normalization or validation bug is fixed in `src/`
- valid locale inputs canonicalize and malformed inputs still fail closed
- the learner can defend the blast radius of a fail-open trust boundary

## Key Files

- `scenarios/day01/scenario.yaml`
- `src/aegisap/day_01/normalizers.py`
- `src/aegisap/day_01/service.py`
- `tests/test_day_01_money.py`
- `tests/test_day_01_fixtures.py`
