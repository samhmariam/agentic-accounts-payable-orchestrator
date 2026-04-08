# Day 10 Peer Red-Team Checklist

Use this checklist before Day 10 CAB approval.

- Replay at least one saved KQL query from `build/day10/kql_evidence.json` and confirm it returns the claimed failure footprint.
- Demand one concrete release-evidence artifact, not just a verbal summary.
- Verify Revert Proof includes the rollback mechanism, last-known-good target, time-box, and exercised or dry-run evidence.
- Probe for hardcoded credentials, public exposure, over-privileged RBAC, and missing exception expiry.
- Ask at least 2 skeptical questions and record whether the learner answered with evidence or guesswork.
