# Customer Escalation - Day 11

Subject: Approval was attributed to the wrong authority chain

Finance security flagged a payment approval where the runtime could not prove
the acting approver still belonged to the required Entra group at execution
time. We need a same-day fix.

What we know:

- the OBO exchange still appears to run
- the approval record is not trustworthy unless actor binding is proved against the group object ID
- audit wants a refreshed threat model and exception posture before close of business
