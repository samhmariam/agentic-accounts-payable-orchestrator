# Customer Escalation - Day 12

Subject: Security found a public endpoint in the supposedly private deployment

The network review team found evidence that one AI endpoint can still be
reached publicly even though the release package claimed private-only access.

What we need:

- prove whether the static checker or the live posture evidence is lying
- restore the private-network gate before the next deployment window
- update the exception packet so nobody can wave this through as a dev-only issue
