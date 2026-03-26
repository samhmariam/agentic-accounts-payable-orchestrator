# Day 2 - Stateful Workflow Orchestration

Day 2 wraps the Day 1 canonical invoice in explicit workflow state and routes it
through deterministic review steps. The point is to make control flow,
recommendations, and evidence inspectable.

## Lab Command

```bash
uv run python scripts/run_day2_workflow.py \
  --day1-artifact build/day1/golden_thread_day1.json \
  --known-vendor
```

## Training Artifact

The script writes `build/day2/golden_thread_day2.json` containing the serialized
Day 2 workflow state.

## Exit Check

Day 2 succeeds when the learner can inspect:

- the chosen route
- the route reason
- completed nodes
- emitted recommendations

## What Learners Should Notice

- Day 2 consumes the Day 1 artifact instead of inventing a new invoice shape.
- Routing is deterministic and evidence-backed.
- The state object is now the contract for later orchestration work.

## Key Files

- `src/aegisap/day2/state.py`
- `src/aegisap/day2/router.py`
- `src/aegisap/day2/graph.py`
- `scripts/run_day2_workflow.py`
