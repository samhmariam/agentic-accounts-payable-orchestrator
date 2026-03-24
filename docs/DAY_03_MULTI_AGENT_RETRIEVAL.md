# Day 3 - Minimal Multi-Agent Retrieval

Day 3 keeps the explicit workflow style from Day 2, but splits reasoning into narrow specialists and places retrieval ahead of specialist judgment.

## Package layout

Day 3 now follows the same convention as Day 1 and Day 2:

```text
src/aegisap/day3/
  agents/
  evaluation/
  policies/
  retrieval/
  state/
  graph.py

tests/day3/
data/day3/
docs/DAY_03_*.md
```

The primary workflow entrypoint is `aegisap.day3.graph.run_day3_workflow`.

The workflow supports three unstructured retrieval modes:

- `fixture` for deterministic local tests
- `azure_search_live` for live Azure AI Search-backed retrieval
- `pgvector_fixture` for a local cost-sensitive stand-in

## Node flow

The workflow executes a deterministic sequence of nodes:

1. `intake_router`
2. `retrieve_vendor_context`
3. `vendor_risk_verifier`
4. `retrieve_po_context`
5. `po_match_agent`
6. `decision_synthesizer`
7. `evaluation_scoring`
8. `finalize_case`

Retrieval is separate from reasoning. Specialists read compact evidence bundles from shared state and return typed findings. They do not call each other directly.

## What Day 3 now proves

By the end of Day 3 in this repo, the system now has:

- typed specialist handoffs instead of free-form agent chatter
- structured and unstructured evidence flowing into shared workflow state
- local authority and recency ranking over retrieved evidence
- fixture-backed development mode for deterministic tests
- one live Azure AI Search-backed smoke path for unstructured retrieval

That means Day 3 is no longer only a mock collaboration exercise. It now has a real enterprise-managed retrieval path while preserving a fast local fallback.

## Contracts

Retrieval normalizes every result into a Day 3 `EvidenceItem` containing:

- provenance
- authority tier
- timestamps
- retrieval score
- authority-adjusted score
- citation text

The specialist contracts are:

- `VendorRiskFinding`
- `POMatchFinding`
- `DecisionRecommendation`

The synthesizer reads only specialist findings and cited evidence IDs.

## Data layout

Fixtures stay under `data/day3/`:

- `structured/` for vendor master, PO, and goods receipt data
- `unstructured/` for onboarding emails, policy docs, and notes
- `eval/` for case sheets and expected scoring fixtures

## Live Azure retrieval

Day 3 now has a dedicated live Azure AI Search path for unstructured evidence.

- The dedicated index is `AZURE_SEARCH_DAY3_INDEX`, separate from the starter Day 0 `AZURE_SEARCH_INDEX`.
- Structured vendor and PO lookups remain deterministic/local for Day 3.
- Azure Search returns retrieval candidates, and local Day 3 code still applies authority and recency rules.
- The Day 3 smoke path has been validated with `ensure_day3_search_index.py`, `ingest_day3_search_docs.py`, and `verify_day3_live_retrieval.py`.

### Operator runbook

1. Provision the core or full track.
2. Load the generated environment with `setup-env`.
3. Ensure the dedicated Day 3 Search index exists:
   `uv run python scripts/ensure_day3_search_index.py --endpoint "$AZURE_SEARCH_ENDPOINT" --index-name "$AZURE_SEARCH_DAY3_INDEX"`
4. Ingest the Day 3 unstructured evidence:
   `uv run python scripts/ingest_day3_search_docs.py --endpoint "$AZURE_SEARCH_ENDPOINT"`
5. Run the live smoke path:
   `uv run python scripts/verify_day3_live_retrieval.py --endpoint "$AZURE_SEARCH_ENDPOINT" --index-name "$AZURE_SEARCH_DAY3_INDEX"`

Optional Blob-backed source parity:

1. Upload the Day 3 markdown fixtures:
   `uv run python scripts/upload_day3_fixtures_to_blob.py`
2. Re-ingest from Blob instead of local files:
   `uv run python scripts/ingest_day3_search_docs.py --endpoint "$AZURE_SEARCH_ENDPOINT" --source blob`

## Day 4 readiness checklist

Before starting Day 4 planning, all of the following should be true:

- the Day 1 canonical invoice remains the only invoice shape consumed downstream
- the Day 2 workflow state still routes and records evidence correctly
- Day 3 specialists consume typed evidence bundles and return typed findings
- the stale-email-versus-vendor-master authority conflict is covered by tests
- the Day 3 fixture test suite passes locally
- one live Azure Search-backed Day 3 smoke path passes successfully

Day 4 should build planning on top of these contracts rather than re-solving retrieval or authority logic inside the planner.

## Learning goal

The Day 3 exit check is the key safeguard: when stale unstructured evidence conflicts with fresher authoritative records, the workflow must surface both but trust the structured source of record.
