# AegisAP Capstone PR Review

This review happens before the release-style defense. A learner does not pass
the capstone by producing a green packet alone; they must also survive review
on the change itself.

## Required PR-Style Packet

Every learner submits a short review packet containing:

- change summary
- risk assessment
- test evidence
- KQL replay evidence
- Revert Proof
- rollback plan
- release evidence
- one known limitation
- native proof artifact references where applicable

## Review Cycle

1. Learner submits the PR-style summary before the final defense.
2. Trainer or peer reviewer records at least one substantive finding.
3. Learner updates code, evidence, or rationale in response.
4. Reviewer confirms the response quality.
5. Only then does the release-style defense begin.

For Day 10 and capstone CAB reviews:

- each peer reviewer must ask at least 2 skeptical questions
- each peer reviewer must demand at least 1 concrete evidence artifact
- each peer reviewer must replay at least one saved KQL query and confirm it returns the claimed footprint
- each peer reviewer must inspect Revert Proof and challenge the stated recovery time box
- the board may require the learner to rerun the selected native proof live
- the facilitator records `peer_reviewer_challenge_quality` for each reviewer
- capstone peer roles are `client_ciso` and `infra_lead`, with the facilitator acting as CAB chair

## Review Finding Standard

A substantive finding must address one of:

- correctness risk
- security gap
- observability or release blind spot
- rollback weakness
- missing or weak KQL proof
- missing or weak test evidence

“Looks good” is not a valid review cycle.

Rubber-stamping is scored as reviewer failure, not kindness.

## Pass Contract

Capstone defense cannot start until:

- `build/capstone/<trainee_id>/release_packet.json` exists
- the PR-style review is complete
- at least one review finding has been addressed or defended with evidence

Record review quality in `review_response_quality` on the daily scorecard.
Record reviewer rigor in `peer_reviewer_challenge_quality` on the reviewer's own scorecard.
