# ADR-001 — Scope and Boundaries

## Purpose

Record the architectural decision that defines the scope of the AegisAP system
and its boundaries with external systems, data owners, and human actors.

## Required Sections

1. **Title**: ADR-001 Scope and Boundaries
2. **Status**: Proposed / Accepted / Superseded
3. **Date**:
4. **Context**: What forced this decision to be made explicitly
5. **Options considered**: (minimum two options)
   - Option A — [description]
   - Option B — [description]
6. **Decision**: Which option was chosen
7. **Rationale**: Why this option wins on the key criteria
8. **Consequences**
   - Positive: what this decision enables
   - Negative / downside: what this decision constrains or excludes
   - Blast radius if wrong: what breaks and who is affected
9. **Decision rights**: Who can reverse or supersede this ADR, under what condition, and what evidence they would require

## Guiding Questions

- What is explicitly out of scope, and is that exclusion formally agreed with a stakeholder?
- If the scope grows after Day 3, what approval step is required?
- Which boundary is most likely to be violated by a feature request and who holds the line?
- What would a hostile architecture reviewer challenge first in the rationale section?

## Structural Example — Option Comparison

| Option | Boundary choice | Why it is attractive | Why it loses or wins |
|---|---|---|---|
| A | AegisAP performs extraction, routing, and low-value approval only | Keeps blast radius bounded and lets finance retain authority for high-value cases | Wins because it matches the Day 4 MVP and still leaves a clean path to Day 10 governance |
| B | AegisAP becomes the full system of record for invoice approvals and vendor policy | Fewer hops for the user and a stronger automation story | Loses because it collapses ERP authority boundaries and expands audit risk too early |

## Anti-Patterns To Avoid

- Do not write "future integrations are out of scope" without naming the actual system boundary today.
- Do not choose the broadest option just because it sounds more strategic.
- Do not leave decision rights at "the architecture team"; name the role that can reverse the ADR.

## Acceptance Criteria

- At least two options considered, each with a specific distinguishing characteristic
- Consequences section has both a positive and a downside entry
- Blast-radius-if-wrong entry names a system or role (not "things could go wrong")
- Decision rights section names a role, not "the team"
- Status is one of the three valid values (not "draft")
