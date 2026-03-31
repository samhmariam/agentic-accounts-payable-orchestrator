# AegisAP Capstone PR Review

This review happens before the release-style defense. A learner does not pass
the capstone by producing a green packet alone; they must also survive review
on the change itself.

## Required PR-Style Packet

Every learner submits a short review packet containing:

- change summary
- risk assessment
- test evidence
- rollback plan
- release evidence
- one known limitation

## Review Cycle

1. Learner submits the PR-style summary before the final defense.
2. Trainer or peer reviewer records at least one substantive finding.
3. Learner updates code, evidence, or rationale in response.
4. Reviewer confirms the response quality.
5. Only then does the release-style defense begin.

## Review Finding Standard

A substantive finding must address one of:

- correctness risk
- security gap
- observability or release blind spot
- rollback weakness
- missing or weak test evidence

“Looks good” is not a valid review cycle.

## Pass Contract

Capstone defense cannot start until:

- `build/capstone/<trainee_id>/release_packet.json` exists
- the PR-style review is complete
- at least one review finding has been addressed or defended with evidence

Record review quality in `review_response_quality` on the daily scorecard.
