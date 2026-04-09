# AegisAP Assessment Rubric

Use this rubric for end-of-day check-ins, catch-up coaching, and the final
capstone review. The goal is not to reward notebook completion alone; it is to
measure whether the engineer can make safe, production-calibrated decisions
and defend them to auditors, executives, and hostile reviewers.

Per-day rubric weight breakdowns are the authoritative source in
`docs/curriculum/CURRICULUM_MANIFEST.yaml`. This file defines the scoring
model; the manifest defines per-day dimension names and weights.

## Scoring Model

Each day is scored out of **100 points** across five base dimensions. Days 8-14
replace 15 points of generic weighting with `Diagnostic Independence`, so the
learner is scored on how they found the fault before they are scored on how
smoothly they defended the fix.

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

### Diagnostic Independence (Days 8-14 only, max 15)

This dimension is scored from saved evidence, not assessor intuition.

| Band | Points | Observable behavior |
|---|---|---|
| Full | 13–15 | Learner captures pre-patch telemetry first, narrows the subsystem from native evidence or KQL, and records a replayable timeline before touching the repo patch. |
| Strong | 10–12 | Learner uses telemetry first but the saved evidence is thin in one place, such as a missing correlation reference or an incomplete interpretation note. |
| Developing | 6–9 | Learner eventually finds the right subsystem, but the evidence chain is partial, out of order, or not clearly pre-patch. |
| At risk | 1–5 | Learner relies on local repo search, memory, or post-patch screenshots more than saved telemetry. |
| Insufficient | 0 | No pre-patch telemetry proof, only post-patch evidence, hint ladder used, or repo search occurred before first telemetry capture. |

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
| Full | 28–35 | Artifact complete, all gate conditions met, explains why each field is correct, and maps the observed portal state to the exact durable code or IaC change |
| Strong | 21–27 | Minor gaps in one sub-criterion; artifact is structurally sound and the production target is mostly clear |
| Developing | 14–20 | Missing a contract detail, schema rule, or gate condition; outcome reached but fragile, or the learner can explain the portal but names the wrong permanent code change |
| At risk | 7–13 | Material errors; would fail a production review without intervention, or the learner relies on manual portal repair with no durable codification path |
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
| Full | 13–15 | Correct approver chain, change classification, evidence requirements, and codification path named without prompting |
| Strong | 10–12 | Approver chain mostly correct; one governance or codification step missing or mis-classified |
| Developing | 6–9 | Identifies the right team but cannot name the process, required evidence, or exact durable change |
| At risk | 3–5 | Treats governance as optional or an obstacle, or cannot move from portal observation to automation |
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

## Translation Requirement

Explaining the portal is not enough. A passing learner must be able to say:

- which Azure or runtime state proved the failure
- which notebook proof reproduced the fix safely
- which exact file or IaC module made the change permanent

If the learner can inspect the portal but cannot codify the fix, score
`Technical Correctness` and `Process Fluency` down accordingly.

For Days 8-14, diagnostic independence is only scoreable when the artifact pack
contains:

- `LAB_OUTPUT/DIAGNOSTIC_PROOF/kql_evidence.json`
- `LAB_OUTPUT/DIAGNOSTIC_PROOF/native_operator_evidence.json`
- `LAB_OUTPUT/DIAGNOSTIC_PROOF/diagnostic_timeline.md`

Assessors must be able to verify from saved evidence that the learner captured
the first telemetry signal before patching. If that proof is absent, assign
`Diagnostic Independence = 0 / 15` even if the learner repaired the issue.

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
- Day 8 break-glass recovery uses a mandatory hint ladder. `T+30` and `T+60`
  hints unblock progression but force `Diagnostic Independence = 0 / 15`.
- Day 14 is scored as a cascading crucible: network first, identity second,
  correlation or regression third. Later-stage evidence should not appear until
  the earlier masking fault is cleared.
- Capstone A foundation packet is built on Day 10 and closed on Day 14 with the final CAB packet.
- Capstone A (AegisAP production defence): full technical and governance pack across Days 1–14, with required Day 10-14 evidence continuity.
- Day 14 also scores the blank-slate architecture drill under the existing Day 14 reasoning and process dimensions.
- Capstone B (transfer domain): Days 12–14 applied to a second domain for Top Talent evaluation. See `capstone/CAPSTONE_B.md`.
- Release-style oral defense is required. A green notebook alone is not a pass.
