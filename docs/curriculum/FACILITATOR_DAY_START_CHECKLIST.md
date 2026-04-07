# Facilitator Day-Start Checklist

Use this checklist at the start of each live training day. It is designed to
reduce avoidable trainer-side surprises before learners hit the notebooks.

## Before Learners Arrive

1. Pull the latest curriculum branch and confirm you are on the intended commit.
2. Sync dependencies:

```bash
uv sync --extra dev --extra day9
```

3. Run the curriculum validator:

```bash
uv run python scripts/validate_curriculum.py
```

4. Confirm Azure access if the day requires it:

```bash
az account show
```

5. Open these side by side:
- `docs/curriculum/CURRICULUM_MANIFEST.yaml`
- the day portal guide in `docs/curriculum/portal/`
- the day notebook
- `docs/curriculum/TRAINER_OPERATIONS.md`
- the prior day's handoff notes

## Cohort Control Check

- Which learners are already `yellow` or `red` from the previous day?
- Which upstream artifacts are still missing?
- Which learners are not safe to advance without catch-up?
- Which live Azure steps today can fall back to preview mode, and which cannot?

## Day-Start Script For Facilitators

Say these five things out loud before the lab begins:

1. What the day is trying to prove.
2. What artifact or evidence the day must leave behind.
3. What counts as a blocker versus normal struggle.
4. Which oral-defense prompts matter most today.
5. Whether authoritative Azure evidence is expected today or preview mode is acceptable.

## High-Risk Day Add-Ons

### Day 8

- Confirm the release/gate story is explicit, not just the IaC mechanics.
- Confirm the rebuild path for missing `build/day8/regression_baseline.json`.

### Day 11

- Confirm learners understand preview-mode OBO artifacts do not satisfy live delegated-identity proof.
- Confirm Key Vault / client-secret handling expectations are clear before the lab starts.

### Day 12

- Confirm the difference between static proof and live posture proof is stated before learners run cells.
- Confirm the room knows that public fallback is not an acceptable production shortcut.

### Day 13

- Confirm learners know the DLQ and MCP cells may run in preview mode unless live env vars are available.
- Confirm the hidden-case discussion does not leak the assessor-only case contents.

### Day 14

- Confirm whether the cohort is expected to stay in preview mode or produce authoritative canary/trace evidence.
- Confirm rollback, partial continuation, and gate-override language stays evidence-based.

## First 15 Minutes Of The Session

- Check that learners can open the repo and activate the right shell.
- Check that learners know the portal guide is today's first surface before the notebook.
- Confirm who already ran the trainee preflight and who did not.
- Identify the first artifact or prerequisite that could stall the room.
- State the fallback path before the first live command is run.

## During The Lab

- Sweep for `yellow` and `red` learners every 10-15 minutes.
- Prefer one exact command or one precise hint over broad reteaching.
- Keep the room moving toward the day's outputs, not just notebook completion.

## Before You End The Day

- Record who is `green`, `yellow`, and `red`.
- Record which exact artifact or checkpoint is missing for anyone not safe to advance.
- Record the fallback or remediation command that was assigned.
- Leave the next facilitator a short handoff note before you close the session.
