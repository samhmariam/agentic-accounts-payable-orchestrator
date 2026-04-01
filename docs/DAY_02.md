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

---

## FDE Rubric — Day 2 (100 points)

| Dimension | Points |
|---|---|
| Discovery completeness | 20 |
| NFR quality with numeric targets | 20 |
| Zero-tolerance NFR identification | 20 |
| Stakeholder / ownership realism | 20 |
| ADR trade-off defense | 20 |

**Pass bar: 80.  Elite bar: 90.**

## Oral Defense Prompts

1. Which NFR did you classify as zero-tolerance and why can it not be tuned post-launch without a full change-board review?
2. If the security stakeholder and the process owner disagree on latency vs control, whose position wins and through what governance mechanism?
3. Who must approve the scope ADR in production, what evidence section would they challenge first, and what would trigger a rollback?

## Artifact Scaffolds

- `docs/curriculum/artifacts/day02/STAKEHOLDER_MAP.md`
- `docs/curriculum/artifacts/day02/RACI_MATRIX.md`
- `docs/curriculum/artifacts/day02/NFR_REGISTER.md`
- `docs/curriculum/artifacts/day02/ADR_001_SCOPE_AND_BOUNDARIES.md`
