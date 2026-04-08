# Customer Escalation: Release Envelope Lied

Subject: CAB saw green while a gate was red

Release Management found a candidate build where one gate failed, another passed,
and the aggregated release envelope still looked green enough to promote.

That breaks the change-approval boundary.

You need to restore the Day 10 release contract:

1. Any failed gate must force a non-green release envelope.
2. Failed-gate evidence must remain visible for CAB review.
3. The executive brief must explain why schedule pressure does not override missing release evidence.

- Change Advisory Board Chair
