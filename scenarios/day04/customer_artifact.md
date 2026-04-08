# Customer Escalation: Planner Looks Safe but the Gate Is Failing Open

Subject: High-value invoice almost skipped manual review

Controller escalation:

The planner produced a path for a high-value invoice with no PO and changed bank
details, but the manual escalation requirement did not fire consistently. We cannot
have a system that behaves safely only on happy-path invoices.

Before this goes back in front of Finance Ops, prove that:

1. Combined-risk invoices are always marked as manual-review-only.
2. The recommendation gate stays fail-closed when mandatory escalation is present.
3. The Day 4 risk register and precedence docs explain the control clearly.

- Principal Engineer, Finance Controls
