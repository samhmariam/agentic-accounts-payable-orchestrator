# Day 3 - Live Azure Retrieval Runbook

This document captures the minimum live Azure retrieval path that should be working before Day 4 begins.

## Goal

Prove that Day 3 can retrieve unstructured evidence from a real Azure AI Search index, feed that evidence into the workflow, and still apply local authority-ranking rules correctly.

The target is not full production ingestion maturity yet. The target is one reliable smoke-tested live path.

## Prerequisites

The Day 0 core or full track must already be provisioned and loaded into the current shell:

- `AZURE_SEARCH_ENDPOINT`
- `AZURE_SEARCH_DAY3_INDEX`
- `AZURE_STORAGE_ACCOUNT_URL`
- `AZURE_STORAGE_CONTAINER`

Authentication should come from `az login` or another `DefaultAzureCredential` path.

## Recommended sequence

1. Verify the base Azure environment:

```bash
uv run python scripts/verify_env.py --track core
```

2. Ensure the dedicated Day 3 Search index exists:

```bash
uv run python scripts/ensure_day3_search_index.py \
  --endpoint "$AZURE_SEARCH_ENDPOINT" \
  --index-name "$AZURE_SEARCH_DAY3_INDEX"
```

3. Ingest the Day 3 unstructured markdown evidence into the dedicated index:

```bash
uv run python scripts/ingest_day3_search_docs.py \
  --endpoint "$AZURE_SEARCH_ENDPOINT" \
  --index-name "$AZURE_SEARCH_DAY3_INDEX"
```

4. Run the live Day 3 smoke path:

```bash
uv run python scripts/verify_day3_live_retrieval.py \
  --endpoint "$AZURE_SEARCH_ENDPOINT" \
  --index-name "$AZURE_SEARCH_DAY3_INDEX"
```

## Expected success condition

The smoke path should confirm:

- the dedicated Day 3 index is reachable through RBAC
- indexed Day 3 documents are queryable through Azure AI Search
- the workflow can run with `retrieval_mode="azure_search_live"`
- the final recommendation still cites the authoritative vendor master record
- the stale onboarding email is still surfaced as historical context, not current truth

## Optional Blob-backed source parity

The simplest ingestion path is local markdown files directly into Search.

If you want the Day 3 documents to exist in Blob first, run:

```bash
uv run python scripts/upload_day3_fixtures_to_blob.py
uv run python scripts/ingest_day3_search_docs.py \
  --endpoint "$AZURE_SEARCH_ENDPOINT" \
  --index-name "$AZURE_SEARCH_DAY3_INDEX" \
  --source blob
```

Blob parity is useful for future ingestion hardening, but it is not required for the Day 3 completion gate.

## Known boundaries

At the end of Day 3:

- structured vendor and PO retrieval are still deterministic/local
- Azure AI Search is used only for unstructured retrieval
- authority, recency, and conflict resolution remain local workflow logic
- the dedicated Day 3 index is intentionally separate from the starter Day 0 `documents` index

This keeps the live Azure path real without forcing a larger index migration before Day 4.
