# RACI MATRIX

## Purpose

Define ownership and accountability for every material decision and activity
in the AegisAP system, from design through operation.

## Required Headings

1. RACI definitions (Responsible, Accountable, Consulted, Informed)
2. Activities table (activity × role → R/A/C/I/–)
3. Single-accountable verification — confirm no activity has more than one A
4. Gap analysis — activities with no Accountable owner
5. Escalation owner — who holds A when the normal accountable role is absent

## Guiding Questions

- Which activity has the most stakeholder confusion about ownership?
- Is there any activity where the Accountable owner cannot take the Responsible action alone?
- Who is Accountable for the agent's classification decision at 23:00 on a Friday?
- Which role is over-consulted (present in Consulted on nearly every row) and is that realistic?

## Structural Example — Activity Rows

| Activity | Product owner | FDE | Platform engineer | Security lead | Operations lead |
|---|---|---|---|---|---|
| Approve Day 2 scope boundary | A | R | C | C | I |
| Update Bicep for staging deployment | I | C | A/R | C | I |
| Decide whether to override a failing gate | C | R | C | C | A |
| Execute rollback during live incident | I | C | R | I | A |

## Anti-Patterns To Avoid

- Do not assign two Accountable owners because both are senior.
- Do not hide a gap by marking everyone Responsible and no one Accountable.
- Do not invent role names here that do not match the stakeholder map.

## Acceptance Criteria

- Minimum 10 distinct activities covering design, build, deploy, operate, and audit phases
- No activity has more than one Accountable owner
- At least one gap identified and assigned an interim owner
- Escalation owner row is present and not the same as every Accountable default
- Role column uses roles from the STAKEHOLDER_MAP (consistent naming)
