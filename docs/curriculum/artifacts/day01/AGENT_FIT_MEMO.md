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

## Acceptance Criteria

- All five fit signals explicitly addressed (not implied)
- At least one fit signal acknowledged as weak/partial with a condition
- WAF section names a specific trust boundary concern (not just "security")
- Recommendation includes a reversal condition (when to stop and revert)
- Decision rights section names an approval role, not just "the team"
