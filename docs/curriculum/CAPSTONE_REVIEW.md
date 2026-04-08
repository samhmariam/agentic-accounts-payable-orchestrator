# AegisAP Capstone Review

Use this guide to run the scored end-of-bootcamp release review. The capstone is
not a demo. It is a bounded engineering change, a release packet, and a
release-style defense.

## Capstone Menu

Each learner must choose one bounded enhancement:

- Trust-boundary or policy hardening:
  improve safety without increasing false refusals on the golden path
- Durable workflow or human-in-the-loop enhancement:
  improve recoverability without weakening idempotency or auditability
- Observability or regression-gate enhancement:
  improve diagnosability without exposing new sensitive data
- Cost-routing or cache-governance improvement:
  improve efficiency without increasing projected daily spend or hiding
  critical-slice regressions

Every option includes built-in ambiguity. The learner must state:

- the chosen assumption
- one rejected alternative
- the risk of the assumption being wrong
- the validation plan for that assumption

## Required Deliverables

- One bounded code or configuration change
- One new or updated test, eval, or gate
- One updated artifact or release packet
- One rollback command
- One completed PR-style review cycle from [CAPSTONE_PR_REVIEW.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/CAPSTONE_PR_REVIEW.md)
- One 10-minute release-style defense

Use the Day 10 helper command to build the release packet:

```bash
uv run python scripts/build_capstone_release_packet.py \
  --trainee-id <your-id> \
  --enhancement-category observability_or_policy \
  --checkpoint-artifact build/day4/checkpoint_policy_overlay.json \
  --checkpoint-artifact build/day8/checkpoint_trace_extension.json \
  --checkpoint-artifact build/day10/checkpoint_gate_extension.json \
  --rollback-command "uv run python scripts/check_all_gates.py --skip-deploy --out build/day10/release_envelope.json" \
  --summary "Describe the bounded enhancement, tests, and release evidence."
```

The output contract is:

- `build/capstone/<trainee_id>/release_packet.json`

The final Day 14 chaos command review adds:

- `build/day14/breaking_changes_drills.json`
- `build/day14/chaos_capstone_report.json`
- `build/day14/cto_trace_report.json`

Generate the Day 14 chaos artifacts with:

```bash
uv run python scripts/run_chaos_capstone.py
```

## Scoring

The capstone uses the shared rubric in
[ASSESSMENT_RUBRIC.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/ASSESSMENT_RUBRIC.md).

- Pass bar: `13/16`
- No score below `3` in `Technical Correctness`
- No score below `3` in `Security Reasoning`
- All required tests and release gates must be green
- Any failed gate must be recovered during review or routed to remediation
- `review-response quality` must be acceptable or strong on the trainer scorecard

## Review Flow

1. Learner submits the one-page design brief with scope, risk, rollback,
   expected artifacts, and assumption handling.
2. Learner completes the PR-style review cycle defined in [CAPSTONE_PR_REVIEW.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/CAPSTONE_PR_REVIEW.md).
3. Session runs in `cab_board` mode with facilitator as CAB chair and peer reviewers assigned as `client_ciso` and `infra_lead`.
4. Learner walks through the bounded enhancement and why it belongs in the chosen category.
5. Learner shows the test, eval, or gate evidence for the change.
6. Learner opens the Day 10 release envelope and checkpoint artifacts.
7. Learner presents the rollback command and explains when they would use it.
8. CAB chair may require the learner to rerun the selected native proof live.
9. Facilitator scores the release-style defense and records `peer_reviewer_challenge_quality` for each reviewer.

Peer reviewers are not observers. They are accountable for adversarial, evidence-seeking questions and can force revision before approval.
