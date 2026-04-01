# RAG BOUNDARY DECISION

## Purpose

Document the decision about where retrieval-augmented generation applies,
what it does not own, and what authority rules override retrieved evidence.

## Required Headings

1. Context — what retrieval is being used for
2. What RAG owns vs what deterministic policy owns
3. Authority hierarchy for conflicting evidence
4. Failure modes — what happens when retrieval returns nothing, wrong content, or stale content
5. ADR-style decision rights — who can expand the RAG boundary post-Day 3

## Guiding Questions

- Which document or data type must NEVER be retrieved (only fetched from the source of record)?
- If a retrieved document contradicts a deterministic compliance rule, which wins and why?
- What is the blast radius if the retrieval index returns a stale policy document?
- Who owns the index refresh SLA and what happens if it is missed?

## Acceptance Criteria

- Explicit boundary drawn between RAG-owned and policy-owned decisions
- Authority hierarchy is a numbered list (not a prose paragraph)
- At least two failure modes covered with a mitigation for each
- ADR section names a role for the decision right (not "the team")
- Cost/latency trade-off explicitly addressed (not implied)
