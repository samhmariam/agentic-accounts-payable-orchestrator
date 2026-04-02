# Curriculum Remediation Backlog

## Purpose

Convert the curriculum review into an ordered implementation backlog that raises
the programme toward the target bar of `>= 9.4 / 10` for depth, breadth,
teaching quality, and mastery reinforcement.

## Success Criteria

- Every late-stage gate distinguishes clearly between training previews and
  authoritative production evidence.
- Day 10 focuses on production decision-making rather than re-teaching Day 8.
- Days 12-14 integrate Capstone B directly into the notebook flow.
- Core artifact templates include at least one strong structural example or
  anti-pattern note so trainees are not forced to infer quality from headings
  alone.
- Notebook progression is explicit: fallback paths remain useful for practice,
  but they do not masquerade as mastery or elite-readiness proof.

## Priority 0

### 1. Training vs Authoritative Evidence Enforcement

Problem:
Several Days 12-14 notebook cells can emit stub artifacts that look green enough
 to satisfy downstream reasoning, even when no live Azure validation occurred.

Files:
- `src/aegisap/deploy/gates_v2.py`
- `notebooks/day_12_private_networking_constraints.py`
- `notebooks/day_13_integration_boundary_and_mcp.py`
- `notebooks/day_14_breaking_changes_elite_ops.py`

Acceptance criteria:
- Stub artifacts carry `training_artifact: true`
- Live artifacts carry `authoritative_evidence: true`
- Gates fail closed on training-only evidence for elite/prod claims
- Notebook copy explicitly states that training previews do not satisfy elite
  promotion evidence

Status:
- Completed

### 2. Day 13 Artifact Shape Alignment

Problem:
Day 13 notebook output shapes are not fully aligned with the gates that consume
them, especially around MCP and DLQ reports.

Files:
- `notebooks/day_13_integration_boundary_and_mcp.py`
- `src/aegisap/deploy/gates_v2.py`

Acceptance criteria:
- MCP lab writes `passed` and `errors`
- DLQ lab writes `total` and `error_count`
- Notebook messages match actual gate behavior

Status:
- Completed

### 3. Day 3 Progression Honesty

Problem:
Day 3 fallback paths are useful for learning but currently under-communicate
that they are lineage fallbacks rather than mastery proof.

Files:
- `notebooks/day_3_azure_ai_services.py`

Acceptance criteria:
- Fallback state is called out as training-only
- The Day 2 dependency is explained as a lineage requirement, not a convenience
- No unbound-variable behavior when Day 2 artifacts are absent

Status:
- Completed

## Priority 1

### 4. Re-center Day 10 on Production Operations

Problem:
Day 10 overlaps heavily with Day 8 instead of adding enough operator-grade depth.

Files:
- `notebooks/day_10_production_operations.py`

Acceptance criteria:
- Day 10 explicitly marks Day 8 mechanics as refresh material
- New production content covers halt criteria, error budgets, release authority,
  incident command, and gate exceptions
- The teaching arc from Day 8 -> Day 10 is obvious and non-duplicative

Status:
- Completed

### 5. Inline Capstone B Integration

Problem:
Capstone B exists in docs and fixtures, but the notebook flow underuses it.

Files:
- `notebooks/day_12_private_networking_constraints.py`
- `notebooks/day_13_integration_boundary_and_mcp.py`
- `notebooks/day_14_breaking_changes_elite_ops.py`
- `docs/curriculum/CAPSTONE_B_TRANSFER.md`

Acceptance criteria:
- Each late-stage notebook includes a transfer-domain orientation cell
- Claims-intake fixture paths are notebook-visible
- Oral-defense framing in the notebook mirrors the transfer domain, not only the
  separate curriculum docs

Status:
- Completed

## Priority 2

### 6. Exemplar Density Upgrade

Problem:
Too many artifact templates are structurally sound but under-modeled.

Files:
- `docs/curriculum/artifacts/day01/AGENT_FIT_MEMO.md`
- `docs/curriculum/artifacts/day03/MODEL_ROUTING_POLICY_V1.yaml`
- `docs/curriculum/artifacts/day10/CAB_PACKET.md`
- `docs/curriculum/artifacts/day14/ELITE_READINESS_SCORECARD.md`

Acceptance criteria:
- Each file includes a structural example or anti-pattern guidance
- Examples demonstrate quality without pre-answering the exercise
- Acceptance criteria remain strict enough to discourage template copying

Status:
- Partially completed; continue expanding exemplar coverage

### 7. Follow-on Work After This Patch

Remaining backlog:
- Continue exemplar upgrades only where future curriculum additions create new thin templates

Status:
- Completed

### 8. Late-Stage Lineage Maps & Mastery Checkpoints

Problem:
Days 10 and 12-14 contain strong technical content, but the learner still has to
infer too much of the evidence flow and readiness bar between sections.

Files:
- `notebooks/day_10_production_operations.py`
- `notebooks/day_12_private_networking_constraints.py`
- `notebooks/day_13_integration_boundary_and_mcp.py`
- `notebooks/day_14_breaking_changes_elite_ops.py`

Acceptance criteria:
- Each notebook includes a visual artifact-to-gate map
- Each notebook includes an explicit mastery checkpoint before progression
- Day 10 includes a short operator decision drill, not only static explanation

Status:
- Completed

### 9. Late-Stage Exemplar Upgrade

Problem:
Several Day 12-14 templates still ask for high-quality operational output without
showing the learner the shape of a credible answer.

Files:
- `docs/curriculum/artifacts/day12/EGRESS_CONTROL_POLICY.md`
- `docs/curriculum/artifacts/day12/NETWORK_DEPENDENCY_REGISTER.md`
- `docs/curriculum/artifacts/day12/SECURITY_EXCEPTION_REQUEST.md`
- `docs/curriculum/artifacts/day13/COMPENSATING_ACTION_CATALOG.md`
- `docs/curriculum/artifacts/day14/EXECUTIVE_INCIDENT_BRIEF.md`
- `docs/curriculum/artifacts/day14/INCIDENT_COMMAND_PLAYBOOK.md`

Acceptance criteria:
- Each file includes a structural example or anti-pattern note
- Examples demonstrate operator-grade quality without pre-writing the exercise
- The transfer-domain framing remains usable in both AP and claims-intake modes

Status:
- Completed
