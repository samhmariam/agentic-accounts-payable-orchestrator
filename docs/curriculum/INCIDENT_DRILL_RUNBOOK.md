# AegisAP Incident Drill Runbook

Run one unsignposted failure drill late in the bootcamp. The goal is to test
debugging discipline under realistic ambiguity, not notebook memorization. Day
14 extends this into the chaos command review, where MTTR and executive signal
quality matter as much as the raw fix.

## When To Run It

- Preferred window: Day 8, Day 9, Day 10, or the Day 14 chaos command block
- Run one drill per learner or pair
- Do not reveal the root cause in advance

## Approved Injected Failures

### 1. Missing Day 8 Baseline Artifact

- Failure signal: Day 10 `eval_regression` gate fails because
  `build/day8/regression_baseline.json` is missing
- Expected learner action: identify the missing artifact, rebuild it, and rerun
  the affected gate

### 2. Altered Threshold Causing Gate Failure

- Failure signal: regression or budget gate fails after a threshold change
- Expected learner action: determine whether the gate is correctly failing or
  misconfigured, then justify the recovery

### 3. Broken ACA Health Environment Variable

- Failure signal: `aca_health` fails because a deployment variable is missing
- Expected learner action: isolate the missing variable, restore the env
  contract, and rerun the gate

### 4. Missing Or Stale Checkpoint Artifact

- Failure signal: Day 10 training checkpoint fails because
  `build/day4/checkpoint_policy_overlay.json` or
  `build/day8/checkpoint_trace_extension.json` is missing or stale
- Expected learner action: regenerate the correct upstream checkpoint artifact
  and prove the release path is healthy again

## Scoring Priority

Score the drill primarily on `Debugging Discipline`, then on correctness:

- did the learner start from the failure signal?
- did they use artifacts, logs, or documented commands methodically?
- did they avoid trial-and-error thrashing?
- did they recover within the time box?

Record the result as `pass`, `partial`, or `fail` in `incident_drill_result`
on the daily scorecard.

For Day 14, also record:

- `mean_time_to_recovery_minutes`
- `max_time_to_recovery_minutes`
- whether the executive packet was updated before the time box expired

## Time Box

- Individual drill budget: 15-20 minutes
- If unresolved at the time limit, stop the drill, record the score, and move
  the learner into remediation
