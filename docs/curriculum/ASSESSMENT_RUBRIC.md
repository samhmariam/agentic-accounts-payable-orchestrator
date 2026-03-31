# AegisAP Assessment Rubric

Use this rubric for end-of-day check-ins, catch-up coaching, and the final
capstone review. The goal is not to reward notebook completion alone; it is to
measure whether the engineer can make safe, production-calibrated decisions.

## Scoring Scale

| Score | Meaning |
|---|---|
| 4 | Production-ready: explains tradeoffs clearly, executes accurately, and debugs independently |
| 3 | Strong: completes the work correctly with minor guidance |
| 2 | Developing: reaches the outcome but misses important reasoning or recovery steps |
| 1 | At risk: can follow steps mechanically but cannot defend or recover the design |

## Dimensions

### Technical Correctness

| Score | Observable behavior |
|---|---|
| 4 | Produces the expected artifact, validates outputs, and explains why the result is correct |
| 3 | Produces the expected artifact with only minor corrections |
| 2 | Produces output but misses a contract detail, schema rule, or gate condition |
| 1 | Cannot complete the exercise without substantial intervention |

### Debugging Discipline

| Score | Observable behavior |
|---|---|
| 4 | Uses logs, traces, artifacts, and exact recovery commands methodically |
| 3 | Diagnoses common failures with moderate prompting |
| 2 | Relies on trial and error or portal clicking without isolating the issue |
| 1 | Gets blocked by routine environment or artifact failures |

### Security Reasoning

| Score | Observable behavior |
|---|---|
| 4 | Protects trust boundaries, identity scope, and secret posture without prompting |
| 3 | Spots most obvious security regressions and explains why they matter |
| 2 | Understands the controls only after they are pointed out |
| 1 | Treats security requirements as optional implementation detail |

### Production-Readiness Judgment

| Score | Observable behavior |
|---|---|
| 4 | Connects implementation choices to WAF pillars, rollback, observability, and cost |
| 3 | Explains most operational consequences of a design |
| 2 | Understands the happy path but misses reliability or release implications |
| 1 | Frames success as “it worked once” rather than “it can run safely in production” |

## Pass Guidance

- Daily pass: mostly 3s, with no 1s in Security Reasoning or Technical Correctness
- Bootcamp distinction: mostly 4s, especially on Debugging Discipline and Production-Readiness Judgment
- Remediation required: any 1, or repeated 2s on the same dimension across multiple days

## Checkpoint And Capstone Rules

- Mandatory checkpoints on Days 4, 8, and 10 are pass/fail. A learner who cannot produce the required checkpoint artifact enters same-day remediation.
- Trainers should record the first exact failure signal that blocked the learner before offering help.
- Capstone pass bar: `13/16`
- Capstone minimums: no score below `3` in `Technical Correctness` or `Security Reasoning`
- Release-style defense is required. A green notebook alone is not a pass.
