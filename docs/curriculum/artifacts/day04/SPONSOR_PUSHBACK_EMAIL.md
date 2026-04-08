# Sponsor Pushback Email

Subject: Payment release automation request and required control boundary

We cannot approve automatic payment release without a human review step for this
workflow. The current request moves an irreversible financial action outside the
approved control boundary, which creates direct loss exposure if the model or
retrieval evidence is wrong on even a small number of invoices.

From a business-risk perspective, the issue is not only technical correctness.
If the system releases funds on the wrong supplier, stale bank details, or an
incomplete approval chain, the result is financial loss, compliance exposure,
and a failed audit trail. Those are board-level risks, not acceptable tuning
trade-offs.

The approved path is to keep the agent responsible for preparation, routing, and
recommendation while preserving a human-in-the-loop pause before payment
release. That gives you cycle-time improvement on the reversible work while
keeping the final irreversible action inside a defensible production control.
