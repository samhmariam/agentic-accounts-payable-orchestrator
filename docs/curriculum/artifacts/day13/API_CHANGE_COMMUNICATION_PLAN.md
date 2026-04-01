# API CHANGE COMMUNICATION PLAN

<!-- CAPSTONE_B: This artifact applies to both AP and claims intake transfer domain -->

## Purpose

Provide a concrete communication plan for a planned breaking API change,
targeting all consumer types at the right altitude and with the right lead time.

## Required Headings

1. Change summary — what is changing and why (one paragraph, consumer-facing language)
2. Consumer inventory — all known consumers, their criticality, and their estimated migration effort
3. Communication schedule — notification dates, channels, and message owners per milestone
4. Migration support — what the API team commits to provide during the migration window
5. Deadline and fallback — the cutover date, what happens to consumers that miss it, and who decides

## Guiding Questions

- Which consumer has the least capacity to migrate and what extra support do they need?
- What is the blast radius if the cutover date is missed by one important consumer?
- Who approves extending the migration window and what evidence is required?
- What is the post-cutover monitoring plan to detect consumers still on the old version?

## Communication Schedule Example Structure

| Milestone | Calendar date | Channel | Audience | Owner |
|---|---|---|---|---|
| Initial notice | `<date>` | `<channel>` | All consumers | `<role>` |
| Migration guide published | `<date>` | `<channel>` | Technical leads | `<role>` |
| Final reminder | `<date>` | `<channel>` | Non-migrated consumers | `<role>` |
| Cutover | `<date>` | `<channel>` | All consumers | `<role>` |

## Acceptance Criteria

- Consumer inventory has at least 3 distinct consumer types
- Communication schedule has at least 3 milestones with dates
- Migration support commitment is specific (named deliverables)
- Cutover fallback is explicit — not "we'll handle it case by case"
- Post-cutover monitoring plan names an observable signal
