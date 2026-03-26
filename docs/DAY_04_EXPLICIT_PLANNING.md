# Day 4 - Explicit Planning

Day 4 moves AegisAP from implicit sequencing to a plan-first controller. The
learner now asks a planner for typed JSON, validates the plan, executes the
tasks, and decides whether the case is recommendation-ready or must escalate.

## Lab Command

Fixture planner:

```bash
uv run python scripts/run_day4_case.py --planner-mode fixture
```

Live Azure OpenAI planner:

```bash
uv run python scripts/run_day4_case.py --planner-mode azure_openai
```

## Training Artifact

The script writes `build/day4/golden_thread_day4.json` containing:

- the raw planner payload
- the validated plan
- the executed workflow state
- the final recommendation or escalation package

## Exit Check

Day 4 succeeds when:

- the planner returns JSON
- the plan passes deterministic validation
- the case produces either a recommendation package or a manual escalation
  package

## What Learners Should Notice

- Azure OpenAI now participates as a planning controller, not just an extractor.
- The policy overlay outranks planner judgment.
- A plan can fail closed before any downstream recommendation work proceeds.

## Key Files

- `src/aegisap/day4/planning/azure_openai_planner.py`
- `src/aegisap/day4/graph/day4_explicit_planning_graph.py`
- `src/aegisap/day4/execution/plan_executor.py`
- `scripts/run_day4_case.py`
