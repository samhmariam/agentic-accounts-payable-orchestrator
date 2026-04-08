# Day 2 - Quota Storm and Resilience Repair

Day 2 is the first resilience day. The learner is dropped into a quota storm
where Azure OpenAI is returning `429` errors and the protected planning path is
not queueing safely under load.

## Incident Entry

```bash
uv run aegisap-lab incident start --day 02
```

## Verification Commands

```bash
uv run python -m pytest tests/day2/test_resilience_controls.py tests/day8/test_retry_policy.py -q
uv run aegisap-lab artifact rebuild --day 02
```

## Evidence Contract

The repair is not complete until the learner updates the Day 2 evidence that
explains the change:

- `docs/curriculum/artifacts/day02/NFR_REGISTER.md`
- `docs/curriculum/artifacts/day02/ADR_001_SCOPE_AND_BOUNDARIES.md`

## Exit Check

Day 2 succeeds when:

- `429` retry behavior is correct for idempotent paths
- protected planning paths queue instead of ignoring capacity pressure
- the learner can explain why the fix lives in resilience policy rather than in a privilege change

## Key Files

- `scenarios/day02/scenario.yaml`
- `src/aegisap/observability/retry_policy.py`
- `src/aegisap/resilience/backpressure.py`
- `tests/day2/test_resilience_controls.py`
