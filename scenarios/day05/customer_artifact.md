# Customer Escalation: Approval Resume Boundary Drift

Subject: Approval thread resumed against the wrong checkpoint

Operations report:

We replayed an approval thread after a checkpoint change and the resume guard did
not stop it. That is unacceptable. A stale resume token should never be able to
act on a different checkpoint or duplicate a side effect.

You need to restore the safety boundary so we can defend this system:

1. Approval tasks must remain bound to the original checkpoint.
2. Resume must reject drift before any side effect runs.
3. The Day 5 governance docs must explain the pause/resume boundary in plain English.

- Staff Engineer, Runtime Safety
