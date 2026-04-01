# REFUSAL REASON CODE CATALOG

## Purpose

Define the complete set of typed refusal codes the system can emit, with audit
requirements, consumer-facing descriptions, and escalation linkage.

## Required Headings

1. Refusal code table (code, display name, trigger condition, action class, audit required Y/N, escalation path)
2. Completeness assertion — confirmation that every high-risk action class has at least one refusal code
3. Consumer-facing messages — what the human-facing output says for each code (must not leak internal state)
4. Audit record format — required fields in the log entry for a refusal event
5. Gap log — any action class without a refusal code (must be explicitly acknowledged, not omitted)

## Guiding Questions

- Which action class is most likely to be missing a refusal code after Day 7?
- What is the blast radius of a refusal code that leaks internal policy details to the caller?
- Who owns the refusal code catalog — the agent team, security, or compliance?
- What is the minimum audit record that would satisfy an external auditor reviewing a refused transaction?

## Acceptance Criteria

- Minimum 6 codes, covering at least 3 distinct action classes
- No code leaks internal implementation detail in the consumer-facing message
- Completeness assertion is explicit — not implied
- Audit record format names specific fields (not just "relevant fields")
- Gap log is present even if empty (note "no gaps identified as of this version")
