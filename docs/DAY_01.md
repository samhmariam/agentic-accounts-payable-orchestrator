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
