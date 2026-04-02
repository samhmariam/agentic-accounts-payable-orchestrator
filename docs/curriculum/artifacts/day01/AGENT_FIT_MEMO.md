# AGENT FIT MEMO

## Purpose

State the justification for introducing an agentic system to this workflow.

## Required Headings

1. Pain point description (one paragraph)
2. Five agent-fit signals — evidence for each
3. WAF trust and control assessment
4. Go / no-go recommendation with conditions
5. Decision rights — who can overturn this decision and under what condition

## Guiding Questions

- Which of the five fit signals is present here and how do you know from the domain description?
- What would make this automation NOT require an agent?
- If the agent acts on a misclassified record, which downstream system gets incorrect data first?
- What human approval step exists today that the agent would bypass, and under what condition must it be preserved?

## Structural Example — Fit Signal Table

| Signal | Evidence observed | Strength | Design consequence |
|---|---|---|---|
| Input variability | Supplier invoices arrive as PDFs from dozens of formats | Strong | Use extraction + typed validation, not fixed parsing |
| Decision complexity | Approval path depends on amount, PO, supplier status, and policy text | Strong | Agent loop justified; policy overlay mandatory |
| Exception rate | High-value invoices escalate to controller | Strong | HITL path must be first-class, not fallback |
| Auditability | Payment recommendations must be defensible after the fact | Strong | Citations and machine-readable gate evidence required |
| Change velocity | Policy thresholds and supplier controls change quarterly | Partial | Externalize policy and review triggers rather than hard-code |

## Anti-Pattern To Avoid

- Do not write "all five signals are strong" without naming evidence.
- Do not treat "uses AI" as a fit signal by itself.
- Do not recommend an agent without stating at least one reversal condition.

## Acceptance Criteria

- All five fit signals explicitly addressed (not implied)
- At least one fit signal acknowledged as weak/partial with a condition
- WAF section names a specific trust boundary concern (not just "security")
- Recommendation includes a reversal condition (when to stop and revert)
- Decision rights section names an approval role, not just "the team"
