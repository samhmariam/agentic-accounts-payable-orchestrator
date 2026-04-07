# Day 03 — Portal-First Retrieval Setup

> **Portal mode:** `Configure`  
> **Intent:** understand Azure AI Search as a real control-plane object before the repo prepares the Day 3 retrieval path for you.

## Portal-First Outcome

You can inspect or prepare the Day 3 search surface manually, explain the role
of the index and its IAM model, and then map that manual work to the repo helpers.

## Portal Mode

This is a bounded manual setup day. If you use the live Azure path, it is worth
touching the Search service and index surface directly before relying on scripts.

## Azure Portal Path

1. Open the Azure AI Search service created on Day 0.
2. Inspect **Indexes** and note whether the Day 3 index already exists.
3. If you are using the live path, walk through the index creation surface and inspect the fields, key field, searchable fields, and semantic configuration expected by the curriculum.
4. Open **Access control (IAM)** and verify the query path uses reader-style roles while indexing uses contributor-style roles.
5. Inspect the service endpoint, region, and tier so performance and cost constraints are not abstract.
6. If the service supports it in your tenant, inspect index statistics or search explorer so you can connect schema to runtime behavior.

## What To Capture

- Search service name, endpoint, tier, and region.
- Day 3 index name and the key fields or semantic settings that matter.
- The split between query-only identity and indexing identity.

## Three-Surface Linkage

- `Portal`: inspect the Search service, the Day 3 index surface, Search explorer, and IAM roles directly in Azure.
- `Notebook`: open [day_3_azure_ai_services.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_3_azure_ai_services.py) and use the retrieval and authority sections to explain why raw relevance is not the same as business truth.
- `Automation`: run `scripts/ensure_day3_search_index.py`, `scripts/ingest_day3_search_docs.py`, and finally `scripts/run_day3_case.py`.
- `Evidence`: the live index schema and query behavior, the notebook's authority-ranking explanation, and `build/day3/golden_thread_day3.json` should all agree on why cited evidence is trustworthy.

## Handoff To Notebook

- Open [day_3_azure_ai_services.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_3_azure_ai_services.py).
- Use [DAY_03_FRAMEWORK_SELECTION_AND_CHOICE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_03_FRAMEWORK_SELECTION_AND_CHOICE.md) to interpret the Azure Search surface in terms of retrieval versus authority.

## Handoff To Automation

After the manual inspection, let the repo rebuild the same surface:

```bash
uv run python scripts/ensure_day3_search_index.py --endpoint "$AZURE_SEARCH_ENDPOINT" --index-name "$AZURE_SEARCH_DAY3_INDEX"
uv run python scripts/ingest_day3_search_docs.py --endpoint "$AZURE_SEARCH_ENDPOINT" --index-name "$AZURE_SEARCH_DAY3_INDEX"
uv run python scripts/run_day3_case.py --retrieval-mode azure_search_live
```
