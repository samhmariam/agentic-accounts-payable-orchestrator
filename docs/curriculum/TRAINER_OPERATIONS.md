# AegisAP Trainer Operations

Use this guide as the delivery control plane for the bootcamp. The day guides
teach content. This document governs pacing, intervention, scoring, and learner
movement through the program.

## Cohort Model

- Target cohort size: 8-16 learners
- Preferred trainer-to-learner ratio: 1:8
- Mixed-skill cohorts are expected; use the learner status model below rather
  than informal judgment to decide who gets intervention first
- If the cohort exceeds 16 learners, add a second trainer or teaching assistant
  for the lab blocks and incident drills

## Daily Operating Rhythm

1. Pre-brief: review the day guide, expected artifact, checkpoint status, and
   any open remediation notes from the prior day.
2. Theory block: deliver the theory segment before learners open notebooks.
3. Lab block: keep the room moving toward the artifact and exit ticket, not
   toward notebook completion for its own sake.
4. Intervention sweep: scan for yellow/red learners every 10-15 minutes.
5. Exit-ticket scoring: record artifact status, rubric scores, and remediation
   in `docs/curriculum/templates/DAILY_SCORECARD.md`.
6. End-of-day handoff: leave concise notes for the next trainer on blockers,
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

- required artifact missing
- mandatory checkpoint failed
- `Technical Correctness` scored `1`
- `Security Reasoning` scored `1`
- learner cannot name the exact recovery command for their blocker

## Required Delivery Tools

- [README.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/README.md)
- [ASSESSMENT_RUBRIC.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/ASSESSMENT_RUBRIC.md)
- [CAPSTONE_REVIEW.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/CAPSTONE_REVIEW.md)
- [CAPSTONE_PR_REVIEW.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/CAPSTONE_PR_REVIEW.md)
- [INCIDENT_DRILL_RUNBOOK.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/INCIDENT_DRILL_RUNBOOK.md)
- [docs/curriculum/templates/DAILY_SCORECARD.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/templates/DAILY_SCORECARD.md)
