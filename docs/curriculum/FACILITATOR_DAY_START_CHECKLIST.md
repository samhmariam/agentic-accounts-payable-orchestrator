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
- the day notebook
- `docs/curriculum/FDE_DEBUGGING_FRAMEWORK.md`
- the primary day doc
- `docs/curriculum/TRAINER_OPERATIONS.md`
- `docs/curriculum/NATIVE_TOOLING_POLICY.md`
- the prior day's handoff notes

If you are teaching Day 0, also open `docs/curriculum/portal/DAY_00_PORTAL.md`.

## Cohort Control Check

- Which learners are already `yellow` or `red` from the previous day?
- Which upstream artifacts are still missing?
- Which learners are not safe to advance without catch-up?
- Which live Azure steps today can fall back to preview mode, and which cannot?
- Is `uv run aegisap-lab audit-production` expected today or only the local verification path?
- Is `uv run aegisap-lab mastery --day XX` the blocking gate today, and which inherited constraints must it prove?

## Day-Start Script For Facilitators

Say these five things out loud before the lab begins:

1. What the day is trying to prove.
2. What artifact or evidence the day must leave behind.
3. What counts as a blocker versus normal struggle.
4. Which oral-defense prompts matter most today.
5. Whether authoritative Azure evidence is expected today or preview mode is acceptable.

## Native Tooling Audit Rule

- From Day 05 onward, native operator evidence and KQL evidence are blocking daily outputs.
- During investigation and evidence capture, learners may not use `aegisap-lab` helper commands or canned verification wrappers to discover the answer.
- After both evidence files are complete, wrappers may be used again only for artifact rebuild, mastery, and reset flows.
- Facilitators may randomly require a learner to clear recent terminal-history context, rerun one saved raw command or KQL query live, and explain the interpretation before mastery is accepted.

## High-Risk Day Add-Ons

### Day 5-11

- Confirm the room knows the Day 05 native-tooling policy is now in force: raw proof first, wrappers later.
- Confirm learners know every Day 05-11 submission needs both `native_operator_evidence.json` and `kql_evidence.json`.

### Day 8

- Confirm the release/gate story is explicit, not just the IaC mechanics.
- Confirm the rebuild path for missing `build/day8/regression_baseline.json`.

### Day 11

- Confirm learners understand preview-mode OBO artifacts do not satisfy live delegated-identity proof.
- Confirm Key Vault / client-secret handling expectations are clear before the lab starts.

### Day 12

- Confirm the difference between static proof and live posture proof is stated before learners run cells.
- Confirm the room knows that public fallback is not an acceptable production shortcut.
- Confirm learners know the native-tool gate bans helper CLI commands, requires `build/day12/native_operator_evidence.json`, and includes a live rerun.

### Day 13

- Confirm learners know the DLQ and MCP cells may run in preview mode unless live env vars are available.
- Confirm the hidden-case discussion does not leak the assessor-only case contents.

### Day 14

- Confirm whether the cohort is expected to stay in preview mode or produce authoritative canary/trace evidence.
- Confirm rollback, partial continuation, and gate-override language stays evidence-based.
- Confirm the capstone CAB chair is ready to select one saved native proof for a live rerun.

### Day 9

- Confirm learners know Day 9 native evidence is blocking and must be replay-ready for the Day 10 CAB board.
- Confirm the room knows that raw KQL and raw Azure commands are expected during the native-tool section.

## First 15 Minutes Of The Session

- Check that learners can open the repo and activate the right shell.
- Check that learners know Day 0 starts in the portal, while Days 1-14 start with `uv run aegisap-lab incident start --day XX`.
- Check that learners know the notebook now includes a `Codification Bridge` step before the repo patch.
- Confirm who already ran the trainee preflight and who did not.
- Identify the first artifact or prerequisite that could stall the room.
- State the fallback path before the first live command is run.

## During The Lab

- Sweep for `yellow` and `red` learners every 10-15 minutes.
- Prefer one exact command or one precise hint over broad reteaching.
- Keep the room moving toward the day's outputs, not just notebook completion.

## Chaos Gate Intervention Protocol

- During a timeboxed chaos failure, the trainer may not touch the learner's keyboard.
- The trainer may not use the learner's mouse.
- The trainer may not point at the screen to identify the fix.
- The trainer may only ask Socratic questions using the four pillars:
  expected topology, network proof, RBAC or identity proof, and log evidence.
- If the learner misses `time_box_minutes`, they fail the chaos gate for the day.
- The trainer must reset the conversation around
  `docs/curriculum/FDE_DEBUGGING_FRAMEWORK.md`.
- If the learner cannot navigate to the relevant logs or probes themselves, they
  fail the day and enter remediation.

## Before You End The Day

- Record who is `green`, `yellow`, and `red`.
- Record which exact artifact or checkpoint is missing for anyone not safe to advance.
- Record the fallback or remediation command that was assigned.
- Leave the next facilitator a short handoff note before you close the session.
