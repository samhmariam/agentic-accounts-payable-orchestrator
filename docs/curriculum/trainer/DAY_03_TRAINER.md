# Day 3 — Retrieval Authority · Trainer Guide

> **Session duration:** 3.5 hours (60 min theory + 2.5 h lab)  
> **WAF Pillars:** Performance Efficiency · Reliability  
> **Prerequisite:** Day 2 complete; Azure AI Search index provisioned

---

## Session Goals

By the end of Day 3, every learner should be able to:
- Explain the difference between retrieval and authority
- Configure an Azure AI Search query with hybrid search enabled
- Interpret retrieval scores and understand when to distrust a high-scoring result
- Produce a citation-backed evidence synthesis
- Explain the multi-agent retrieval pattern and each agent's scope

---

## Preparation Checklist

- [ ] AI Search index populated: `uv run python scripts/ensure_day3_search_index.py`
- [ ] Fixtures uploaded: `uv run python scripts/upload_day3_fixtures_to_blob.py`
- [ ] Verify live retrieval: `uv run python scripts/verify_day3_live_retrieval.py`
- [ ] Day 2 artifact present: `build/day2/`
- [ ] Semantic search tier enabled on the Azure AI Search service
      (`Standard` tier minimum; confirm in portal or via `az search service show`)

**Expected artifact:** `build/day3/golden_thread_day3.json`

---

## Theory Segment (60 min)

### Block 1: RAG Architecture and Failure Modes (20 min)

**Talking points:**
1. Draw the RAG pipeline on the whiteboard:
   ```
   Query ──► Index ──► Chunks ──► Context ──► LLM ──► Answer
   ```
2. Ask learners: "What is the biggest difference between 'the model knows about
   VAT rules' and 'the model answers from retrieved VAT rules'?"
   Expected: the second is attributable — you can trace each answer back to
   a specific source document.
3. Walk through the four failure modes systematically:
   - **Context stuffing**: show the effect with a prompt that has 20 chunks.
     Ask: "Which chunk would you prioritise?"
   - **Hallucinated citations**: demonstrate by asking the model to cite a
     document and check whether the excerpt matches. Show how to test for this.
   - **Stale retrieval**: show a search index that hasn't been refreshed in 30
     days. Ask: "What happens if the VAT rate changed last week?"
   - **Authority confusion**: show a prompt that mixes a retrieved policy
     document with a vendor email. Highlight the risk.

**Key message:** "RAG solves the knowledge cut-off problem. It does not solve
the authority problem. Those are different problems."

---

### Block 2: Azure AI Search in Depth (25 min)

**Talking points:**
1. Show the search portal in Azure. Walk through the index schema for the Day 3
   vendor policy index:
   - Field types: `Edm.String`, `Collection(Edm.Single)` (vector), `Edm.DateTimeOffset`
   - Which fields are searchable, filterable, retrievable
2. Explain the three query modes side by side:
   ```python
   # Full-text only
   results = client.search("VAT standard rate office supplies")

   # Vector only (semantic similarity)
   results = client.search(
       "", vector_queries=[VectorizedQuery(vector=embed("VAT standard rate"), fields="content_vector")]
   )

   # Hybrid (RRF fusion)
   results = client.search(
       "VAT standard rate office supplies",
       vector_queries=[VectorizedQuery(vector=embed("VAT standard rate"), fields="content_vector")]
   )
   ```
3. Show RRF score mathematics on the board (keep it intuitive, not exhaustive).
   The key insight: a document in position 2 of keyword AND position 3 of vector
   will beat a document in position 1 of keyword only.
4. Explain managed identity access to Search:
   - Show the role assignment in Bicep (`Search Index Data Reader`)
   - Open `src/aegisap/security/credentials.py` and show that no search
     admin key is used in application code

**Interactive exercise:** Have learners run the same query with keyword only,
vector only, and hybrid mode and compare the top-3 results. Discuss why they differ.

---

### Block 3: Authority and Multi-Agent Retrieval (15 min)

**Talking points:**
1. Introduce the concept of an *authority registry*: a curated list of documents
   whose claims the system is permitted to rely on. Not everything in the index
   is authoritative — some indexed documents may be draft or superseded.
2. Draw the Day 3 multi-agent pattern:
   ```
   Orchestrator
       ├── VendorPolicyAgent  → index filter: vendor_id = VEND-001
       ├── ComplianceAgent    → index filter: doc_type = regulatory
       └── EvidenceAggregator → merge, deduplicate, authority rank
   ```
3. Emphasise: each agent queries a different *filter scope*. The orchestrator
   never queries the raw index — it trusts each agent to return only authoritative
   results for its domain.
4. Show how a citation is generated and what fields it must contain.

---

## Lab Walkthrough Notes

### Key cells to call out in `day3_retrieval_authority.py`:

1. **Index status cell** — confirms the search index is populated. If it shows
   `0 documents`, stop and run `ensure_day3_search_index.py`.

2. **`_vendor_policy_query` cell** — first live search call. Walk through the
   `SearchClient` configuration: endpoint, index, credential.

3. **`_compliance_query` cell** — same pattern, different filter scope.
   Ask learners to identify which fields are used for filtering.

4. **`_display_evidence` cell** — shows the aggregated chunks with scores.
   Discuss: "Which score threshold would you use as a minimum before trusting
   a chunk?"

5. **`_display_synthesis` cell** — LLM synthesis with citations. Open the
   citation object and trace it back to the raw chunk in the previous cell.

### Expected lab friction points

| Issue | Likely cause | Resolution |
|---|---|---|
| Search returns 0 results | Index not populated | `python scripts/ensure_day3_search_index.py` |
| 403 on search call | Missing `Search Index Data Reader` role | Re-run role assignments Bicep |
| Semantic reranking unavailable | Search service on `Basic` tier | Upgrade to `Standard` in Bicep and redeploy |
| Low similarity scores across all chunks | Embedding model mismatch between indexing and query | Confirm same embedding deployment name in index config and query code |

---

## Facilitation Addendum

### Observable Mastery Signals

- Learner can distinguish authority from retrieval score using a concrete citation.
- Learner can explain why a retrieved result is allowed or disallowed to influence the plan.
- Learner uses the artifact to justify the winning evidence rather than hand-waving the retrieval stack.

### Intervention Cues

- If “highest score wins” appears in discussion, pause and reconnect to the authority registry.
- If citations are missing, stop the lab and make the learner show the evidence chain before moving on.
- If Azure Search access is noisy, move the cohort to fixture mode rather than improvising search credentials.

### Fallback Path

- Use fixture retrieval and a saved Day 3 artifact if live search access is unavailable; keep the session centered on authority reasoning and citations.

### Exit Ticket Answer Key

1. Retrieval finds candidates; authority decides which sources are allowed to count.
2. Reader roles preserve least privilege and keep the search index off the control plane.
3. `uv run python scripts/run_day3_case.py --retrieval-mode fixture` is the fastest deterministic rebuild.

### Time-box Guidance

- Cap live Azure Search troubleshooting at 15 minutes.
- Spend the regained time on citation review and outdated-source failure modes if fixture mode is used.

---

## Common Misconceptions

| Misconception | Correction |
|---|---|
| "High similarity score means the chunk is correct" | Score measures similarity, not accuracy or authority |
| "Retrieval and authority are the same thing" | Retrieval finds relevant chunks; authority registers which are trusted to make claims |
| "Hybrid search is just faster than vector search" | It is often *more accurate* — combining two different signal types catches what each misses |
| "We can skip citations for internal systems" | Citations are required for human review and for debugging incorrect decisions |

---

## Discussion Prompts

1. "A retrieved chunk has a score of 0.95 but is from a document dated 2019.
   The current policy may have changed. How should the system handle this?"

2. "A vendor email says 'per the attached HMRC circular, VAT is 5% for our
   category.' The system cannot find that circular in the index. What outcome
   should the system produce?"

3. "What is the difference between updating the search index and updating
   the authority registry? Can a document be in the index but not the registry?"

---

## Expected Q&A

**Q: Why use Azure AI Search instead of a vector database like Pinecone or Qdrant?**  
A: Azure AI Search provides hybrid search, semantic reranking, managed scaling,
Entra-based auth, and native Azure Monitor integration in one managed service.
For enterprises already on Azure, it avoids introducing a second data store
with separate security controls. Pinecone/Qdrant are valid alternatives for
vector-only workloads or multi-cloud scenarios.

**Q: How large should chunks be?**  
A: For policy documents, paragraph-level chunking (100–300 tokens) works well
because policy clauses tend to be self-contained. Add overlap (10–20 tokens)
to avoid cutting context mid-rule. For longer evidence documents, hierarchical
chunking (small child + large parent) gives the best precision/context balance.

**Q: Can we use Azure OpenAI embeddings for the vector field?**  
A: Yes — `text-embedding-3-small` or `text-embedding-3-large` are the current
recommended models. Use the same model for both indexing and query. Switching
models requires re-indexing all documents.

---

## Next-Day Bridge (5 min)

> "Our workflow now has retrieval-backed evidence. But the execution path is
> still implicit — there's no explicit record of *which* steps were chosen
> and *why*. Tomorrow we introduce the plan-first agent: the system will generate
> a typed JSON plan, validate it, apply a policy overlay, and only then execute.
> The decision trail becomes explicit before a single task runs."
