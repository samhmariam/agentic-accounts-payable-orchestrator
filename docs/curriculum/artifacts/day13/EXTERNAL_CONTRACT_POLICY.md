# EXTERNAL CONTRACT POLICY

<!-- CAPSTONE_B: This artifact applies to both AP and claims intake transfer domain -->

## Purpose

Define the rules governing API and data contracts exposed to or consumed from
external systems — ensuring versioning discipline and breaking-change communication.

## Required Headings

1. Contract inventory — every external contract in scope (API, event schema, data feed)
2. Versioning strategy — how contracts are versioned and what constitutes a breaking vs non-breaking change
3. Deprecation rules — minimum notice period, notification mechanism, and grace period per contract class
4. Consumer obligation — what downstream consumers are required to do before a breaking change lands
5. Breaking change authority — who approves the introduction of a breaking change

## Guiding Questions

- Which contract is most likely to have undocumented consumers?
- What is the blast radius of a breaking change that is not communicated to a single consumer?
- Who holds accountability when a consumer fails to migrate by the deprecation deadline?
- What is the minimum notice period for the most tightly-coupled external consumer?

## Acceptance Criteria

- Minimum 3 external contracts in inventory
- Breaking vs non-breaking change classification has concrete examples for each
- Deprecation rules have a minimum notice period in calendar days (not "sufficient notice")
- Consumer obligation is enforceable (not aspirational)
- Breaking change authority names a role — not "the team"
