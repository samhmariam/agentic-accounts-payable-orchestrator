# Day 3 - Retrieval, Authority, and Multi-Agent Handoffs

Day 3 adds retrieval ahead of specialist reasoning. Azure AI Search becomes the
required exit path for unstructured evidence, while local authority rules still
decide what counts as truth.

## Lab Command

Ensure the Day 3 index is loaded first:

```bash
uv run python scripts/ensure_day3_search_index.py \
  --endpoint "$AZURE_SEARCH_ENDPOINT" \
  --index-name "$AZURE_SEARCH_DAY3_INDEX"

uv run python scripts/ingest_day3_search_docs.py \
  --endpoint "$AZURE_SEARCH_ENDPOINT" \
  --index-name "$AZURE_SEARCH_DAY3_INDEX"
```

Run the case:

```bash
uv run python scripts/run_day3_case.py --retrieval-mode azure_search_live
```

## Training Artifact

The script writes `build/day3/golden_thread_day3.json` containing:

- the input invoice payload
- the retrieval mode
- ranked evidence buckets
- specialist findings
- evaluation scores

## Exit Check

Day 3 succeeds when live Azure AI Search evidence is returned and the workflow
still prefers the authoritative structured vendor source of record.

## What Learners Should Notice

- Retrieval is separate from judgment.
- Typed specialist findings replace free-form agent chatter.
- Azure Search is live infrastructure, but authority and recency logic remain
  in local workflow code.

## Key Files

- `src/aegisap/day3/graph.py`
- `src/aegisap/day3/retrieval/azure_ai_search_adapter.py`
- `scripts/ingest_day3_search_docs.py`
- `scripts/run_day3_case.py`
