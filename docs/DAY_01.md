# Day 1 - Intake and Canonicalization

Day 1 teaches the intake boundary: take a raw invoice package, extract a
candidate with Azure OpenAI or a fixture payload, and deterministically convert
that candidate into a trusted `CanonicalInvoice`.

## Lab Command

Fixture mode:

```bash
uv run python scripts/run_day1_intake.py --mode fixture
```

Live Azure OpenAI mode:

```bash
uv run python scripts/run_day1_intake.py --mode live
```

## Training Artifact

The script writes `build/day1/golden_thread_day1.json` containing:

- the source package metadata
- the execution mode
- the canonical invoice payload

## Exit Check

Day 1 succeeds when the system emits a canonical invoice or raises an explicit
intake rejection. No malformed data should cross the Day 1 boundary.

## What Learners Should Notice

- Azure OpenAI is used only for extraction.
- Deterministic Python owns normalization, reconciliation, and rejection.
- The Day 1 artifact is the handoff object for Day 2.

## Golden Thread Input

The default training case uses:

- `fixtures/golden_thread/package.json`
- `fixtures/golden_thread/candidate.json`

## Key Files

- `src/aegisap/day_01/agent.py`
- `src/aegisap/day_01/normalizers.py`
- `src/aegisap/day_01/service.py`
- `scripts/run_day1_intake.py`

---

## FDE Rubric — Day 1 (100 points)

| Dimension | Points |
|---|---|
| Agent-fit signals | 25 |
| Rejection criteria | 20 |
| WAF / trust trade-off | 20 |
| Business framing | 15 |
| Oral defense | 20 |

**Pass bar: 80.  Elite bar: 90.**

## Oral Defense Prompts

1. What alternative automation approach did you reject for this pain point, and why does the agent design win on this dimension?
2. What is the blast radius if the agent acts on a misclassified invoice? Name the downstream systems and approvers affected.
3. Who in a real enterprise must sign off on introducing an agentic system into a financial workflow, and what audit evidence would they demand before go-live?

## Artifact Scaffolds

- `docs/curriculum/artifacts/day01/AGENT_FIT_MEMO.md`
- `docs/curriculum/artifacts/day01/NO_AGENT_MEMO.md`
- `docs/curriculum/artifacts/day01/FDE_MENTAL_MODELS.md`
