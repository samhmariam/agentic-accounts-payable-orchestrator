# AegisAP Trainer Operations

Use this guide as the delivery control plane for the bootcamp. The day guides
teach content. This document governs pacing, intervention, scoring, and learner
movement through the program.

Start each live day with
[FACILITATOR_DAY_START_CHECKLIST.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/FACILITATOR_DAY_START_CHECKLIST.md).
Use
[TRAINEE_PREFLIGHT_CHECKLIST.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/TRAINEE_PREFLIGHT_CHECKLIST.md)
as the required pre-cohort readiness contract for learners.

## Cohort Model

- Target cohort size: 8-16 learners
- Preferred trainer-to-learner ratio: 1:8
- Mixed-skill cohorts are expected; use the learner status model below rather
  than informal judgment to decide who gets intervention first
- If the cohort exceeds 16 learners, add a second trainer or teaching assistant
  for the lab blocks and incident drills

## Daily Operating Rhythm

Every day produces **four outputs**. The artifact pack is the exit ticket.
See `docs/curriculum/templates/DAILY_ARTIFACT_PACK.md` for folder structure.
The exact artifact filenames for each day are the authoritative source in
`docs/curriculum/CURRICULUM_MANIFEST.yaml` under `artifact_files`.

1. Pre-brief: review the day's manifest entry, expected artifact filenames,
   checkpoint status, incident or bootstrap entrypoint, and any open remediation notes from the
   prior day. Run the facilitator day-start checklist before learners enter
   the lab block.
2. Theory block: for Day 0, start with the portal-first bootstrap walkthrough.
   For Days 1-14, start with the incident, then use the notebook's portal
   investigation section to anchor the Azure evidence before learners patch the
   repo. Force the learner through the codification bridge before they open the
   editor: what exact state did the portal show, what exact notebook proof
   reproduced it, and what exact file must change? Introduce the three oral
   defense prompts for the day so learners can build toward them during the lab.
3. Lab block: keep the room moving toward all four outputs (technical build,
   decision memo, corporate process artifact, oral defense prep). Notebook
   completion alone is not the goal.
4. Intervention sweep: scan for yellow/red learners every 10–15 minutes.
5. Oral defense sessions: run after the lab block. Two assessors per trainee.
   Score using `docs/curriculum/templates/ORAL_DEFENSE_SCORECARD.md` and the
   band anchors in `docs/curriculum/ASSESSOR_CALIBRATION.md`.
6. Exit-ticket scoring: record artifact status, 100-point rubric scores, and
   remediation in `docs/curriculum/templates/DAILY_SCORECARD.md`. Mandatory
   checkpoint days are Day 4, Day 8, and Day 10 — gate evidence must be
   complete before the trainee enters capstone review.
7. Zero-tolerance verification (Days 7, 10, 11, 12, 14): complete the
   zero-tolerance check in the scorecard before finalising any score for
   those days. A hard-fail overrides the total to 0.
8. End-of-day handoff: leave concise notes for the next trainer on blockers,
   remediation, and who is not safe to advance.

## Learner Status Model

- `green`: independent progress, artifact on track, can explain the design
- `yellow`: blocked for more than 10 minutes, repeated conceptual confusion,
  or exit-ticket answers show partial understanding
- `red`: missing artifact, failed checkpoint, rubric score of `1`, or cannot
  recover from a failure signal with the documented command path

## Intervention Rules

- `green`: leave the learner in independent mode and use them for peer support
  only after they have completed their own artifact
- `yellow`: intervene with one focused hint, one exact command, or one artifact
  comparison; do not solve the whole exercise for them
- `red`: stop forward motion, assign remediation immediately, and do not let
  the learner advance to the next checkpoint or capstone without recovery

## Timeboxed Chaos Intervention

When a learner enters the daily chaos gate, the facilitator must behave like a
lead engineer under incident discipline, not a helper.

- trainer may not touch the learner's keyboard
- trainer may not use the learner's mouse
- trainer may not point at the screen to reveal the fix
- trainer may only ask Socratic questions grounded in the four pillars:
  expected topology, network proof, RBAC or identity proof, and log evidence
- if the learner misses `time_box_minutes`, they fail the chaos gate for the day
- the facilitator must walk the learner through
  `docs/curriculum/FDE_DEBUGGING_FRAMEWORK.md`
- if the learner cannot navigate to the relevant logs or probes themselves, they
  fail the day and move into remediation

## Catch-Up Policy

- Rejoin the main flow only after the missing day artifact and exit ticket are
  complete
- If a learner misses a checkpoint day, they must complete the checkpoint
  artifact before continuing to the next mandatory checkpoint
- If a learner misses Day 8, Day 9, or Day 10 evidence, they do not enter the
  capstone review flow until the missing release inputs are rebuilt

## Trainer Handoff Template

Record the following at the end of each day:

- Which learners are `yellow` or `red`
- Which exact artifact or checkpoint is missing
- Which remediation task was assigned
- Whether the learner should proceed tomorrow or remain in catch-up mode
- Whether any trainer follow-up is needed during the first 30 minutes

## Escalation Criteria

Do not let a learner proceed to the next checkpoint or capstone if any of the
following are true:

- required artifact missing (any of the four daily outputs)
- mandatory checkpoint failed (Days 4, 8, 10)
- `Technical Correctness` scored below 18 (beginning band)
- `Security Reasoning` scored below 7 on any zero-tolerance day (Days 7, 10, 11, 12, 14)
- learner cannot name the exact recovery command for their blocker
- zero-tolerance hard-fail on a zero-tolerance day (score becomes 0 regardless of total)

Scores are on the 100-point scale. The daily pass bar is **80**. The elite
pass bar for Top Talent tier is **90**. See `docs/curriculum/ASSESSMENT_RUBRIC.md`
for full band descriptors and `docs/curriculum/GRADUATION_RUBRIC.md` for
graduation tier thresholds.

## Required Delivery Tools

- [README.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/README.md)
- [portal/README.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/portal/README.md)
- [TRAINEE_PREFLIGHT_CHECKLIST.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/TRAINEE_PREFLIGHT_CHECKLIST.md)
- [FACILITATOR_DAY_START_CHECKLIST.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/FACILITATOR_DAY_START_CHECKLIST.md)
- [FDE_DEBUGGING_FRAMEWORK.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/FDE_DEBUGGING_FRAMEWORK.md)
- [CURRICULUM_MANIFEST.yaml](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/CURRICULUM_MANIFEST.yaml)
- [ASSESSMENT_RUBRIC.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/ASSESSMENT_RUBRIC.md)
- [GRADUATION_RUBRIC.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/GRADUATION_RUBRIC.md)
- [MENTAL_MODELS.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/MENTAL_MODELS.md)
- [ASSESSOR_CALIBRATION.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/ASSESSOR_CALIBRATION.md)
- [CAPSTONE_REVIEW.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/CAPSTONE_REVIEW.md)
- [CAPSTONE_PR_REVIEW.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/CAPSTONE_PR_REVIEW.md)
- [INCIDENT_DRILL_RUNBOOK.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/INCIDENT_DRILL_RUNBOOK.md)
- [templates/ORAL_DEFENSE_SCORECARD.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/templates/ORAL_DEFENSE_SCORECARD.md)
- [templates/DAILY_ARTIFACT_PACK.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/templates/DAILY_ARTIFACT_PACK.md)
- [templates/DAILY_SCORECARD.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/templates/DAILY_SCORECARD.md)

Use `portal/README.md` and `DAY_00_PORTAL.md` only for the bootstrap exception.
For Days 1-14, the live delivery path is `incident start -> portal investigation -> notebook proof -> codification bridge -> repo patch -> verification`.
