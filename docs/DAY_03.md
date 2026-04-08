# Day 3 - Retrieval Authority, Search Evidence, and Boundary Repair

Primary learner entrypoint: `modules/day_03_retrieval_authority/README.md`.

## Why This Matters to an FDE

Retrieval authority is where elegant demos become enterprise liabilities. An FDE must defend why one source wins and how stale evidence is surfaced without corrupting decisions.

## Customer Context

A procurement stakeholder discovered that the system cited an outdated vendor record. They need you to prove which source is authoritative and codify that boundary permanently.

## Persistent Constraints

- `regulated_invoice_auditability`: Every financial decision path must leave auditable evidence that survives hostile review.
- `latency_budget_guardrails`: Queue, retry, and latency controls must be explicit enough to defend under customer SLA pressure.
- `authoritative_retrieval_sources`: Retrieval must prefer authoritative source systems over stale or ambiguous evidence.

## Incident Entry

```bash
uv run aegisap-lab incident start --day 03
```

## Mastery Gate

- `uv run python -m pytest tests/day3/test_vendor_authority_ranking.py tests/day3/test_day3_exit_check.py -q && uv run aegisap-lab artifact rebuild --day 03`

## Verification Commands

```bash
uv run python -m pytest tests/day3/test_vendor_authority_ranking.py tests/day3/test_day3_exit_check.py -q
uv run aegisap-lab artifact rebuild --day 03
```

## Key Files

- `modules/day_03_retrieval_authority/README.md`
- `notebooks/day_3_azure_ai_services.py`
- `notebooks/bridges/day03_retrieval_authority.md`
- `src/aegisap/day3/policies/source_authority_rules.yaml`
- `src/aegisap/day3/retrieval/ranker.py`
- `src/aegisap/day3/retrieval/authority_policy.py`
- `scenarios/day03`

## Automated Drill

- `uv run aegisap-lab drill list --day 03`
- `uv run aegisap-lab drill inject --day 03`
- `uv run aegisap-lab drill reset --day 03`
- `uv run aegisap-lab mastery --day 03` writes `build/day3/constraint_lineage.json` so later reviews can see the inherited rules this day still carries.
