# NFR REGISTER

## Purpose

Capture all non-functional requirements with numeric targets, zero-tolerance
classification, and ownership — before any implementation decision is made.

## Required Headings

1. NFR table (ID, category, description, target, measurement method, zero-tolerance Y/N, owner)
2. Zero-tolerance rationale — for each zero-tolerance NFR, explain why it cannot be tuned post-launch
3. Tunable NFR bounds — for each tunable NFR, state the acceptable tuning range and approver
4. Interdependency map — which NFRs trade off against each other
5. Measurement gaps — NFRs where the measurement method is uncertain

## Guiding Questions

- Which NFR, if missed by 10%, would trigger a regulatory question or audit finding?
- Who decides when a latency NFR is "close enough" without a formal threshold change?
- If two NFRs conflict under load, which wins — and is that decision documented anywhere?
- Which NFR is currently unmeasurable and what does that mean for go-live readiness?

## Acceptance Criteria

- Minimum 8 NFRs across at least 3 categories (performance, security, compliance, operability)
- Every zero-tolerance NFR has a written rationale (not just "it's important")
- Every tunable NFR has explicit bounds (e.g., "p95 ≤ 800ms, floor is 600ms")
- Interdependency map is a table or matrix, not prose
- At least one measurement gap identified with a mitigation plan
