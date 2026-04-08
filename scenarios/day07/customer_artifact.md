# Customer Escalation: Audit Evidence Leaked Sensitive Data

Subject: Your refusal logs exposed bank details

Compliance reported that a Day 7 refusal event still exposed personally
identifiable and banking information in the audit trail.

That is a release blocker.

You need to restore the guardrail boundary immediately:

1. Audit evidence must be redacted before persistence.
2. Redaction must still preserve enough operator context to investigate the case.
3. The Day 7 governance packet must explain why this is a hard stop for release.

- Director of Risk Engineering
