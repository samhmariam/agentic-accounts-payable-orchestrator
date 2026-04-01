# POLICY PRECEDENCE MEMO

## Purpose

Define the precedence order when agent model output, policy rules, and human
override instructions conflict — and document who governs that precedence order.

## Required Headings

1. Precedence statement — a numbered, unambiguous ordered list
2. Conflict scenario table — at least three scenarios where two rules collide, and which wins each time
3. Override authority — who can issue a human override and under what conditions
4. Audit trail requirement — what evidence must exist for every precedence decision made at runtime
5. Change control — who can change the precedence order and what evidence they need

## Guiding Questions

- Which precedence conflict is most likely to appear in production within the first month?
- Is it ever acceptable for model output to override a compliance policy? If so, under what encoded condition?
- Who holds the audit evidence if a precedence rule causes incorrect behaviour?
- What is the mechanism to escalate a runtime precedence conflict to a human?

## Acceptance Criteria

- Precedence list is numbered (not bulleted — ordering must be unambiguous)
- At least three conflict scenarios, each with a single clear winner and a rationale
- Override authority section names a role, a method of issuance, and an expiry condition
- Audit trail requirement is specific (names the fields logged, not just "we log things")
- Change control names a role and names the evidence required
