# Day 2 - Resilience Under Load, NFR Enforcement, and Ownership

Primary learner entrypoint: `modules/day_02_resilience_ownership/README.md`.

## Why This Matters to an FDE

Enterprise FDE work starts with constraints, not code. If you cannot make reliability and ownership legible, the customer experiences every retry storm as your fault.

## Customer Context

The customer architecture board is pressing for throughput gains during an invoice spike, but the service owner refuses any change that weakens queue safety or approval lines.

## Cost of Failure

If queue and retry controls drift under load, invoice SLAs slip and the customer loses confidence in the team's operational ownership.

## Persistent Constraints

- `regulated_invoice_auditability`: Every financial decision path must leave auditable evidence that survives hostile review.
- `latency_budget_guardrails`: Queue, retry, and latency controls must be explicit enough to defend under customer SLA pressure.

## Incident Entry

```bash
uv run aegisap-lab incident start --day 02
```

## Mastery Gate

- `uv run python -m pytest tests/day2/test_resilience_controls.py tests/day8/test_retry_policy.py -q && uv run aegisap-lab artifact rebuild --day 02`

## Active Inception

- Delivery mode: triad roleplay
- Facilitator script: `scenarios/day02/facilitator_script.yaml`
- Role cards: `scenarios/day02/role_cards/`
- Capture artifact: `docs/curriculum/artifacts/day02/ACTIVE_DISCOVERY_LOG.md`
- Observer scorecard: `docs/curriculum/templates/ACTIVE_INCEPTION_OBSERVER_SCORECARD.md`

The interviewer must extract the hidden queue-safety NFR, the ownership boundary,
and the rollback trigger before opening the repo targets.

## Verification Commands

```bash
uv run python -m pytest tests/day2/test_resilience_controls.py tests/day8/test_retry_policy.py -q
uv run aegisap-lab artifact rebuild --day 02
```

## Key Files

- `modules/day_02_resilience_ownership/README.md`
- `notebooks/day_2_requirements_architecture.py`
- `notebooks/bridges/day02_resilience_controls.md`
- `src/aegisap/observability/retry_policy.py`
- `src/aegisap/resilience/backpressure.py`
- `docs/curriculum/artifacts/day02/ACTIVE_DISCOVERY_LOG.md`
- `scenarios/day02`

## Automated Drill

- `uv run aegisap-lab drill list --day 02`
- `uv run aegisap-lab drill inject --day 02`
- `uv run aegisap-lab drill reset --day 02`
- `uv run aegisap-lab mastery --day 02` writes `build/day2/constraint_lineage.json` so later reviews can see the inherited rules this day still carries.
