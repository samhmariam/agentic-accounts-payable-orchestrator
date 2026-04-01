# AegisAP Assessment Rubric

Use this rubric for end-of-day check-ins, catch-up coaching, and the final
capstone review. The goal is not to reward notebook completion alone; it is to
measure whether the engineer can make safe, production-calibrated decisions
and defend them to auditors, executives, and hostile reviewers.

Per-day rubric weight breakdowns are the authoritative source in
`docs/curriculum/CURRICULUM_MANIFEST.yaml`. This file defines the scoring
model; the manifest defines per-day dimension names and weights.

## Scoring Model

Each day is scored out of **100 points** across five dimensions.

| Dimension | Points | What it measures |
|---|---|---|
| Technical Correctness | 35 | Artifact accuracy, gate behavior, schema contracts, tool wiring |
| Trade-off Reasoning | 20 | Rejected alternatives, blast radius logic, constraint navigation |
| Process Fluency | 15 | Correct use of approval paths, change classification, governance artifacts |
| Artifact Quality | 15 | Completeness, structure, acceptance criteria met, no pre-filled answers copied verbatim |
| Oral Defense | 15 | Clarity, precision, correct identification of decision authority and evidence |

Note: per-day variant weights (e.g. Day 1 weights agent-fit signals at 25 points
rather than the generic Technical Correctness label) are defined in
`CURRICULUM_MANIFEST.yaml → days[n].rubric_weights`.

## Pass Bars

| Bar | Threshold | Condition |
|---|---|---|
| Daily pass | ≥ 80 / 100 | Required to advance to next day |
| Zero-tolerance hard fail | 0 / 100 | Any zero-tolerance condition triggers this regardless of numeric total |
| Elite daily | ≥ 90 / 100 | Required for Top Talent graduation tier |

**Zero-tolerance scope:** Applies to assessed artifacts and technical decisions,
not oral-defense points alone. See full matrix below and in the manifest.

## Scoring Descriptors Per Dimension

### Technical Correctness (max 35)

| Band | Points | Observable behavior |
|---|---|---|
| Full | 28–35 | Artifact complete, all gate conditions met, explains why each field is correct |
| Strong | 21–27 | Minor gaps in one sub-criterion; artifact is structurally sound |
| Developing | 14–20 | Missing a contract detail, schema rule, or gate condition; outcome reached but fragile |
| At risk | 7–13 | Material errors; would fail a production review without intervention |
| Insufficient | 0–6 | Artifact absent or so incomplete it cannot be assessed |

### Trade-off Reasoning (max 20)

| Band | Points | Observable behavior |
|---|---|---|
| Full | 16–20 | Rejected alternatives named and argued; blast radius quantified; constraint correctly navigated |
| Strong | 12–15 | Rejected alternatives present; blast radius approximate but directionally correct |
| Developing | 8–11 | Only one alternative considered; blast radius vague |
| At risk | 4–7 | No rejected alternatives; decision presented as obvious |
| Insufficient | 0–3 | No reasoning beyond "this is what we did" |

### Process Fluency (max 15)

| Band | Points | Observable behavior |
|---|---|---|
| Full | 13–15 | Correct approver chain, change classification, and evidence requirements named without prompting |
| Strong | 10–12 | Approver chain mostly correct; one governance step missing or mis-classified |
| Developing | 6–9 | Identifies the right team but cannot name the process or required evidence |
| At risk | 3–5 | Treats governance as optional or an obstacle |
| Insufficient | 0–2 | No process awareness demonstrated |

### Artifact Quality (max 15)

| Band | Points | Observable behavior |
|---|---|---|
| Full | 13–15 | All required headings present; guiding questions answered with own reasoning; acceptance criteria met |
| Strong | 10–12 | One section thin or missing; rest is substantive |
| Developing | 6–9 | Template headings present but several sections are answer-key reproductions or left blank |
| At risk | 3–5 | Artifact is a form fill; no original reasoning visible |
| Insufficient | 0–2 | Template returned unchanged or near-unchanged |

### Oral Defense (max 15)

| Band | Points | Observable behavior |
|---|---|---|
| Full | 13–15 | Precise, concise, names correct approver and evidence without prompting; handles follow-up probes |
| Strong | 10–12 | Correct substance; slightly imprecise on evidence requirements or edge case |
| Developing | 6–9 | Right direction but cannot name specific approver, evidence type, or blast radius |
| At risk | 3–5 | Vague or contradicts written artifact |
| Insufficient | 0–2 | Cannot engage with the question |

See `docs/curriculum/ASSESSOR_CALIBRATION.md` for calibration anchors.

## Zero-Tolerance Conditions

The following conditions hard-fail the day regardless of numeric total.
Full matrix is in `CURRICULUM_MANIFEST.yaml → days[n].zero_tolerance`.

| Day | Condition |
|---|---|
| 7 | Mandatory escalation missed on critical slice regression |
| 7 | Refusal schema absent for high-risk action class |
| 10 | Pass declared when gate evidence is absent |
| 10 | Gate exception approved without required authority or expiry |
| 11 | Actor binding broken — payload identity accepted without OBO verification |
| 11 | OBO bypass approved for convenience without formal exception |
| 12 | Public endpoint described as acceptable in production |
| 12 | Security exception granted with no expiry or compensating control |
| 14 | Continue-service recommended when binary gates are failing |
| 14 | No rollback path identified during war-game |

A hard-fail day must be re-sat and passed before graduation.

## Graduation Tiers

| Tier | Minimum average | Additional requirements |
|---|---|---|
| Graduate | 80 | All 14 days passed; all zero-tolerance conditions passed; no major process weakness |
| Strong FDE | 85 | Defends trade-offs clearly; produces reusable artifacts; handles one hostile review |
| Top Talent | 90 | Passes transfer capstone; communicates to executives, auditors, security, and ops without loss of precision; correct go/no-go under pressure |

See `docs/curriculum/GRADUATION_RUBRIC.md` for full tier definitions.

## Checkpoint And Capstone Rules

- Mandatory production-gate checkpoints on Days 4, 8, and 10 remain pass/fail for artifact
  existence and gate behavior. They are separate from the 100-point rubric and tested by
  `tests/training/test_checkpoints.py`.
- Trainers must record the first exact failure signal before offering help.
- Capstone A (AegisAP production defence): full technical and governance pack across Days 1–14.
- Capstone B (transfer domain): Days 12–14 applied to a second domain. See `CAPSTONE_B_TRANSFER.md`.
- Release-style oral defense is required. A green notebook alone is not a pass.
