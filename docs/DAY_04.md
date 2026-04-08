# Day 4 - Single-Agent Loops, Policy Overlay, and Fail-Closed Repair

Primary learner entrypoint: `modules/day_04_single_agent_loops/README.md`.

## Why This Matters to an FDE

Single-agent loops only become production-safe when policy can override model enthusiasm. FDEs get paid to keep irreversible actions inside a fail-closed boundary.

## Customer Context

The customer CISO banned public exposure for production-bound AI services and wants proof that risky recommendation paths still stop for review instead of acting optimistically.

## Persistent Constraints

- `regulated_invoice_auditability`: Every financial decision path must leave auditable evidence that survives hostile review.
- `latency_budget_guardrails`: Queue, retry, and latency controls must be explicit enough to defend under customer SLA pressure.
- `authoritative_retrieval_sources`: Retrieval must prefer authoritative source systems over stale or ambiguous evidence.
- `no_public_endpoints`: Production-bound AI and data services must not expose public network access.
- `fail_closed_decisions`: Risky automation paths must fail closed and require explicit human review.

## Incident Entry

```bash
uv run aegisap-lab incident start --day 04
```

## Mastery Gate

- `uv run python -m pytest tests/day4/unit/planning/test_policy_overlay.py tests/day4/unit/recommendation/test_recommendation_gate.py -q && uv run aegisap-lab artifact rebuild --day 04`
- `uv run aegisap-lab audit-production --day 04 --strict`

## Stakeholder Inject

- Executive sponsor request: bypass the HITL pause and auto-issue payments.
- Required internal artifact: `adr/ADR-002_irreversible_actions_and_hitl.md`
- Required sponsor-facing artifact: `docs/curriculum/artifacts/day04/SPONSOR_PUSHBACK_EMAIL.md`

## Verification Commands

```bash
uv run python -m pytest tests/day4/unit/planning/test_policy_overlay.py tests/day4/unit/recommendation/test_recommendation_gate.py -q
uv run aegisap-lab artifact rebuild --day 04
```

## Key Files

- `modules/day_04_single_agent_loops/README.md`
- `notebooks/day_4_single_agent_loops.py`
- `notebooks/bridges/day04_fail_closed_planning.md`
- `src/aegisap/day4/planning/policy_overlay.py`
- `src/aegisap/day4/recommendation/recommendation_gate.py`
- `adr/ADR-002_irreversible_actions_and_hitl.md`
- `docs/curriculum/artifacts/day04/SPONSOR_PUSHBACK_EMAIL.md`
- `scenarios/day04`

## Automated Drill

- `uv run aegisap-lab drill list --day 04`
- `uv run aegisap-lab drill inject --day 04`
- `uv run aegisap-lab drill reset --day 04`
- `uv run aegisap-lab mastery --day 04` writes `build/day4/constraint_lineage.json` so later reviews can see the inherited rules this day still carries.
