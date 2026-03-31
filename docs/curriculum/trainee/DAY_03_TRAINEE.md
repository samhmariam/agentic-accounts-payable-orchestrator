# Day 3 — Retrieval Authority · Trainee Pre-Reading

> **WAF Pillars:** Performance Efficiency · Reliability  
> **Time to read:** 25 min  
> **Lab notebook:** `notebooks/day3_retrieval_authority.py`

---

## Learning Objectives

By the end of Day 3 you will be able to:

1. Explain Retrieval-Augmented Generation (RAG) and its failure modes.
2. Distinguish between a *retrieval system* and an *authority system*.
3. Describe Azure AI Search's hybrid search capability and when to use it.
4. Explain what a citation is and why it is required in an enterprise AI system.
5. Describe the multi-agent retrieval pattern and the roles each agent plays.

---

## 1. Retrieval-Augmented Generation (RAG)

LLMs are trained on data with a knowledge cut-off date. They cannot know your
company's current vendor contracts, compliance rules, or invoice history.

**RAG** solves this by retrieving relevant external knowledge at inference time
and injecting it into the prompt as context. The model's job becomes
"answer using this context" rather than "recall from training data."

```
User query
    │
    ▼
[ Retrieval ] ── searches knowledge base ──► relevant chunks
    │
    ▼
[ Augmentation ] ── injects chunks into prompt
    │
    ▼
[ Generation ] ── LLM answers using retrieved context
    │
    ▼
Answer + citations
```

### Common RAG failure modes

| Failure | Description | Mitigation |
|---|---|---|
| **Context stuffing** | Retrieve too many chunks; model ignores the relevant ones | Rank and truncate; limit context window |
| **Hallucinated citations** | Model cites a document that does not support its claim | Require citations to reference real retrieved chunk IDs |
| **Stale retrieval** | Index is not updated; model uses outdated rules | Set index refresh SLAs and alert on staleness |
| **Authority confusion** | Model blends retrieved rules with training knowledge | Instruction: "answer ONLY from the provided documents" |

---

## 2. Authority: Who Gets to Decide?

Retrieval gives the model access to more information. That is not the same as
giving the model authority to decide what is true.

**Authority** in AegisAP means: for each claim the system makes, there must be a
traceable chain from the claim to a document that an authorised party has
accepted as truth.

```
Claim: "VAT rate 20% applies to this invoice"
  └── Evidence: chunk_id=VAT_RULES_2024_S3, document=HMRC_VAT_NOTICE_700.pdf
        └── Authoritative source: approved policy document registry
```

Without this chain, the system cannot explain its decisions to an auditor.

### Authority vs. retrieval

| Property | Retrieval | Authority |
|---|---|---|
| Question answered | "What documents are relevant?" | "Which documents are trusted to make a claim?" |
| Governed by | Similarity score | Policy registry + version control |
| Failure mode | Missing relevant context | Using outdated or unverified documents |

---

## 3. Azure AI Search

**Azure AI Search** is a managed search service that supports:

| Feature | Description | When to use |
|---|---|---|
| **Full-text search** | BM25-based keyword matching | When exact terms matter (e.g., invoice IDs, vendor names) |
| **Vector search** | Nearest-neighbour search on embeddings | When semantic similarity matters (e.g., "late payment" ≈ "overdue invoice") |
| **Hybrid search** | BM25 + vector combined with RRF fusion | Best of both; default choice for enterprise RAG |
| **Semantic reranking** | Azure ML model re-ranks top results | Use when top-5 precision matters and latency allows |
| **Semantic captions** | Extractive summaries from retrieved chunks | Reduces the context passed to the LLM |

### Hybrid search with Reciprocal Rank Fusion (RRF)

RRF combines two ranked lists into one by computing:

$$\text{RRF score}(d) = \sum_{r \in \text{rankers}} \frac{1}{k + \text{rank}_r(d)}$$

where $k = 60$ (a default constant). Documents appearing in top positions of
*both* the keyword and vector rankings score highest — capturing both exact match
and semantic similarity.

### Managed Identity access to Azure AI Search

```python
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient

credential = DefaultAzureCredential()
client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name="invoices",
    credential=credential,   # <-- no admin key in code
)
```

### Azure best practice
- Grant the application identity the `Search Index Data Reader` role on the
  search service — not `Search Service Contributor`.
- Never use admin keys in application code. Admin keys have full control of
  the service including deleting indexes.
- Set `queryLanguage` and `semanticConfiguration` in your query to opt in to
  semantic reranking only where the latency budget allows.

---

## 4. Chunking Strategy

Before documents can be retrieved, they must be split into **chunks** and
embedded. Chunking strategy directly impacts retrieval quality.

| Strategy | Chunk size | Pros | Cons |
|---|---|---|---|
| Fixed-size | ~512 tokens | Simple, predictable | Cuts context mid-sentence |
| Sentence | 1–3 sentences | Preserves meaning | Variable size |
| Paragraph | 1 paragraph | Good for policy documents | Paragraphs vary widely |
| Hierarchical (parent/child) | Small child + large parent | High precision + high context | More complex indexing |

For policy documents (Day 3), paragraph-level chunks work well because policy
clauses are self-contained.

---

## 5. Multi-Agent Retrieval Pattern

Day 3 introduces a **multi-agent** pattern where retrieval is split across
specialised sub-agents:

```
Orchestrator
    │
    ├── VendorPolicyAgent ──► retrieves vendor-specific rules
    │
    ├── ComplianceAgent ───► retrieves tax and regulatory rules
    │
    └── EvidenceAggregator ► merges, deduplicates, ranks by authority
```

Each sub-agent queries a different index or filter scope. The orchestrator never
calls the index directly — it delegates to agents that understand their own
data's authority model.

This pattern keeps retrieval logic encapsulated and independently testable.

---

## 6. Citations

Every claim made by the system must reference the specific retrieved chunk that
supports it.

```json
{
  "claim": "VAT at 20% is standard for office supplies",
  "citation": {
    "document_id": "HMRC_VAT_NOTICE_700",
    "chunk_id": "section_3_para_2",
    "score": 0.91,
    "excerpt": "Standard rate of VAT at 20% applies to general business supplies..."
  }
}
```

Citations make the system:
- **Auditable**: an auditor can verify the claim against the source
- **Debuggable**: a developer can see exactly which chunk drove a decision
- **Improvable**: low-scoring citations reveal gaps in the knowledge base

---

## Glossary

| Term | Definition |
|---|---|
| **RAG** | Retrieval-Augmented Generation — enhancing LLM prompts with retrieved context |
| **Hybrid search** | Combining keyword (BM25) and vector search with RRF score fusion |
| **RRF** | Reciprocal Rank Fusion — algorithm that merges multiple ranked lists |
| **Semantic reranking** | Post-retrieval re-ordering of results by semantic relevance using a dedicated ML model |
| **Chunk** | A unit of text indexed individually in the search index |
| **Authority** | A registered, versioned source document whose claims the system is permitted to rely on |
| **Citation** | A reference from a system claim back to the retrieved chunk that supports it |
| **Multi-agent retrieval** | Pattern where multiple specialised agents each query their own scope and return results to an orchestrator |

---

## Check Your Understanding

1. What is the difference between retrieval and authority in an enterprise AI context?
2. What does "hybrid search" mean in Azure AI Search, and what is RRF?
3. Why should an application use the `Search Index Data Reader` role rather than an admin key?
4. What is a citation, and why is it required for an auditable AI system?
5. Describe the multi-agent retrieval pattern used in Day 3: what are the agents, and what does each retrieve?

---

## Lab Readiness

- **Lab duration:** 2.5 hours
- **Required inputs:** `build/day2/golden_thread_day2.json`, retrieval fixtures or Azure AI Search access, and `notebooks/day3_retrieval_authority.py`
- **Expected artifact:** `build/day3/golden_thread_day3.json`

### Pass Criteria

- The artifact contains retrieved evidence and authority-ranked citations.
- A seeded authority-ranking regression is corrected so the authoritative source wins.
- You can explain why the chosen evidence is allowed to influence the next-day plan.

### Common Failure Signals

- Retrieval score is treated as equivalent to authority.
- A cited chunk comes from an unapproved or stale source.
- The artifact shows evidence but not the citation path that justifies the claim.

### Exit Ticket

1. What is the difference between “highest score” and “highest authority” in this system?
2. Why is a search reader role safer than a search admin credential?
3. What exact command would you use to rerun the Day 3 case in fixture mode?

### Remediation Task

Rebuild the retrieval artifact with:

```bash
uv run python scripts/run_day3_case.py --retrieval-mode fixture
```

Then identify which citation you would inspect first if a reviewer said the
system relied on the wrong policy clause.

### Stretch Task

Explain how you would detect that a highly ranked result is obsolete even when
its lexical and vector scores both look strong.
