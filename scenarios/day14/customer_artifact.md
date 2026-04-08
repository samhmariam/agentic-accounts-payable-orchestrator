# Customer Escalation - Day 14

Subject: Release board wants to proceed without complete trace evidence

The release candidate is under executive pressure, but operations cannot prove
the private-network deployment has the second sink required for full trace
correlation. The current gate is still reading green.

What we need:

- restore the gate so missing dual-sink evidence blocks promotion again
- show rollback, canary, and trace evidence in one coherent incident packet
- record the chaos drill outcome with MTTR before the CTO review
