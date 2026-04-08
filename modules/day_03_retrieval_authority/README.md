# Day 3 Module Wormhole

## Why This Matters to an FDE

Retrieval authority is where elegant demos become enterprise liabilities. An FDE must defend why one source wins and how stale evidence is surfaced without corrupting decisions.

## Customer Context

A procurement stakeholder discovered that the system cited an outdated vendor record. They need you to prove which source is authoritative and codify that boundary permanently.

## Persistent Constraints

- `regulated_invoice_auditability`: Every financial decision path must leave auditable evidence that survives hostile review.
- `latency_budget_guardrails`: Queue, retry, and latency controls must be explicit enough to defend under customer SLA pressure.
- `authoritative_retrieval_sources`: Retrieval must prefer authoritative source systems over stale or ambiguous evidence.

## FDE Implementation Cycle

- Customer Reality: inspect the live incident and portal surface before you theorize.
- Diagnostic Bridge: prove the state in Marimo and name the API or SDK call that matches the portal behavior.
- Production Engineering: patch the durable code in the repo, not inside the notebook.
- Chaos Gate: recover under the time box and defend the trade-off in review language.

## Mastery Gate

- `uv run python -m pytest tests/day3/test_vendor_authority_ranking.py tests/day3/test_day3_exit_check.py -q && uv run aegisap-lab artifact rebuild --day 03`

## Chaos Gate

- Failure signal: Search evidence disagrees with the source-of-truth policy and the ranker surfaces the wrong authority.
- Diagnostic surface: Azure AI Search index state, notebook retrieval proof, and authority policy files under src/aegisap/day3/.
- Expected recovery artifact: `build/day3/golden_thread_day3.json`
- Time box: 25 minutes

## Day X File Manifest

Do not edit code in this module folder.

- Diagnostic Notebook: `notebooks/day_3_azure_ai_services.py`
- Primary Day Doc: `docs/DAY_03.md`
- Rosetta Stone Bridge: `notebooks/bridges/day03_retrieval_authority.md`
- Production Target: `src/aegisap/day3/policies/source_authority_rules.yaml`
- Production Target: `src/aegisap/day3/retrieval/ranker.py`
- Production Target: `src/aegisap/day3/retrieval/authority_policy.py`
- Scenario Pack: `scenarios/day03`
- Verification Command: `uv run python -m pytest tests/day3/test_vendor_authority_ranking.py tests/day3/test_day3_exit_check.py -q`
- Verification Command: `uv run aegisap-lab artifact rebuild --day 03`

## Automated Drill

- List drills: `uv run aegisap-lab drill list --day 03`
- Inject default drill: `uv run aegisap-lab drill inject --day 03`
- Reset active drill: `uv run aegisap-lab drill reset --day 03`
- Constraint lineage artifact after mastery: `build/day3/constraint_lineage.json`
