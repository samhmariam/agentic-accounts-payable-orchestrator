# Day 3 - Evaluation

Day 3 starts evaluation early with lightweight scoring rather than waiting for a larger benchmark suite.

## Baseline metrics

The workflow records:

- `faithfulness`
- `completeness`
- `policy_grounding`
- `notes`

These scores are stored on the Day 3 workflow state in `eval_scores`.

## What is scored

- Faithfulness checks whether the decision cites evidence IDs that actually exist in the registry.
- Completeness checks whether both specialist findings and the final decision are present.
- Policy grounding checks whether the final answer visibly respects source-priority rules.

These checks are still intentionally lightweight, but they now apply to both fixture-backed retrieval runs and the Day 3 live Azure Search smoke path.

## Judge prompts

Day 3 also includes G-Eval-style rubric prompts for:

- faithfulness
- completeness
- policy grounding

These prompts are intentionally simple. The goal is to establish a stable contract and fixture format that later days can extend.

## Persisted fixtures

Evaluation fixtures stay in `data/day3/eval/` so expected behavior can be regression-tested alongside the retrieval and workflow logic.

## What Day 4 should inherit

Before Day 4 introduces planning, evaluation should already be able to answer:

- did the workflow cite real evidence IDs
- did the workflow cover the specialist decision surfaces
- did the workflow respect source-of-truth rules

Day 4 planning should add a new control layer on top of these measurements, not replace them.
