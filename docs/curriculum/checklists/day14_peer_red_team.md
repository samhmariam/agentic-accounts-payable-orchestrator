# Day 14 Peer Red-Team Checklist

Use this checklist before capstone CAB approval.

- Replay at least one saved KQL query from `build/day14/kql_evidence.json` and confirm it returns the claimed incident footprint.
- Demand live replay of one saved native or rollback proof when the CAB chair requests it.
- Verify Revert Proof includes the rollback mechanism, last-known-good ref or deployment target, recovery time-box, and exercised or dry-run evidence.
- Probe for missing dual-sink evidence, broken private-network assumptions, weak rollback posture, and unsafe exception handling.
- Ask at least 2 skeptical questions and require at least 1 concrete evidence artifact before approval.
