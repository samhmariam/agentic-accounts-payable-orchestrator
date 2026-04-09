# Customer Escalation - Day 14

Subject: Nothing is processing and leadership wants an answer now

We are getting an angry escalation from the client because nothing is
processing through the private deployment path. Right now the only thing the
customer can tell us is that the service looks down.

Important constraint: do not assume this is a single fault. Restore the first
visible failure, then keep tracing the same incident until you know whether a
second or third masked failure is waiting behind it.

What we need:

- restore customer traffic through the private path first
- keep the same correlation trail and prove whether identity or policy drift appears after network recovery
- continue through the next revealed stage until canary or correlation truth is established
- show rollback, canary, and trace evidence in one coherent incident packet before the CTO review
