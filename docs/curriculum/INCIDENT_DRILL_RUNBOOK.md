# AegisAP Incident Drill Runbook

Run one unsignposted failure drill late in the bootcamp. The goal is to test
debugging discipline under realistic ambiguity, not notebook memorization. Day
14 extends this into the chaos command review, where MTTR and executive signal
quality matter as much as the raw fix.

## Command Surface

Use the Phase 2 drill CLI instead of ad-hoc manual breakage.

- `uv run aegisap-lab drill list --day XX`
- `uv run aegisap-lab drill inject --day XX`
- `uv run aegisap-lab drill reset --day XX`
- `uv run aegisap-lab mastery --day XX` writes `build/dayXX/constraint_lineage.json`
  so the learner and facilitator can see which inherited customer rules were in scope.

## When To Run It

- Preferred window: Day 7 onward, with the default drill for that day unless a facilitator intentionally selects an alternate drill id.
- Run one drill per learner or pair.
- Do not reveal the root cause in advance.
- Reset the drill before the next learner starts.

## Preferred Mapping

- Days 1-10 use the day scenario as the default Phase 2 automated drill.
- Day 7 now defaults to probabilistic prompt authority drift rather than a binary outage. The learner must patch the authority policy and re-run the enforced eval suite.
- Day 11 defaults to IAM drift, with OBO scope mismatch as an alternate.
- Day 12 defaults to DNS misconfiguration, with public endpoint re-enabled as an alternate.
- Day 13 defaults to DLQ overflow, with MCP contract break as an alternate.
- Day 14 defaults to rollback failure, with canary regression, data residency violation, and correlation gap as alternates.

For Days 05-14, pair the drill with the native-tool gate described in
`docs/curriculum/NATIVE_TOOLING_POLICY.md`. The learner must save raw operator
proof to `native_operator_evidence.json` before patching and may not use
`aegisap-lab` helper commands or canned verification wrappers to discover the
answer during evidence capture.
For Days 05-14, the learner must also save `kql_evidence.json` before patching
so the facilitator or CAB reviewer can replay the exact Log Analytics query
that proved the failure surface.
Facilitators may randomly require a learner to clear recent terminal-history
context, rerun one saved raw command or KQL query live, and explain the
interpretation before the drill result is accepted.

## Scoring Priority

Score the drill primarily on `Debugging Discipline`, then on correctness:

- did the learner start from the failure signal?
- did they use artifacts, logs, or documented commands methodically?
- did they avoid trial-and-error thrashing?
- did they recover within the time box?
- could they explain which inherited constraints still applied while they fixed the drill?

Record the result as `pass`, `partial`, or `fail` in `incident_drill_result`
on the daily scorecard.

For Day 14, also record:

- `mean_time_to_recovery_minutes`
- `max_time_to_recovery_minutes`
- whether the executive packet was updated before the time box expired

## Time Box

- Individual drill budget: 15-20 minutes for standard days
- Day 14 can extend to 20-35 minutes depending on the drill selected
- If unresolved at the time limit, stop the drill, record the score, and move
  the learner into remediation
