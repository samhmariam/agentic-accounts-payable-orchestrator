# Day 1 - Agentic Systems Fundamentals, Business Value, and FDE Judgment

Primary learner entrypoint: `modules/day_01_trust_boundary/README.md`.

## Why This Matters to an FDE

Trust-boundary failures are customer-facing finance incidents. An FDE has to prove whether the system is lying, parsing badly, or violating the review contract before anyone retries money movement.

## Customer Context

A finance operations lead is blocking go-live after a valid European supplier invoice was rejected. They want proof that the deterministic trust boundary can be repaired without widening the blast radius.

## Cost of Failure

Every hour this locale parsing failure survives, valid supplier invoices remain unpaid and finance risks breach-of-contract escalation.

## Persistent Constraints

- `regulated_invoice_auditability`: Every financial decision path must leave auditable evidence that survives hostile review.

## Incident Entry

```bash
uv run aegisap-lab incident start --day 01
```

## Mastery Gate

- `uv run python -m pytest tests/test_day_01_money.py tests/test_day_01_fixtures.py -q && uv run aegisap-lab artifact rebuild --day 01`

## Verification Commands

```bash
uv run python -m pytest tests/test_day_01_money.py tests/test_day_01_fixtures.py -q
uv run aegisap-lab artifact rebuild --day 01
```

## Key Files

- `modules/day_01_trust_boundary/README.md`
- `notebooks/day_1_agentic_fundamentals.py`
- `notebooks/bridges/day01_trust_boundary.md`
- `src/aegisap/day_01/normalizers.py`
- `src/aegisap/day_01/service.py`
- `scenarios/day01`

## Automated Drill

- `uv run aegisap-lab drill list --day 01`
- `uv run aegisap-lab drill inject --day 01`
- `uv run aegisap-lab drill reset --day 01`
- `uv run aegisap-lab mastery --day 01` writes `build/day1/constraint_lineage.json` so later reviews can see the inherited rules this day still carries.
