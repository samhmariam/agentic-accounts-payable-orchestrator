import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _bootstrap():
    import sys
    from pathlib import Path
    _root = Path(__file__).resolve().parents[1]
    for _p in [str(_root / "src"), str(_root / "notebooks")]:
        if _p not in sys.path:
            sys.path.insert(0, _p)
    return


@app.cell
def _imports():
    import marimo as mo
    import json
    import os
    from pathlib import Path
    return json, mo, os, Path


# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------
@app.cell
def _title(mo):
    mo.md("""
    # Day 3 — Azure AI Services & Agent Frameworks

    > **WAF Pillars covered:** Performance Efficiency · Reliability · Cost Optimization  
    > **Estimated time:** 2.5 hours  
    > **Sources:** `docs/curriculum/trainee/DAY_00_TRAINEE.md`,  
    > `docs/curriculum/trainee/DAY_01_TRAINEE.md`, `docs/curriculum/trainee/DAY_03_TRAINEE.md`  
    > **Prerequisite:** Day 2 architecture blueprint complete.

    ---

    ## Learning Objectives

    1. Configure every AegisAP Azure AI service client using `DefaultAzureCredential` (no admin keys).
    2. Explain Azure OpenAI model tiers, deployment pinning, and structured outputs.
    3. Describe hybrid search, RRF score fusion, and semantic reranking in Azure AI Search.
    4. Select the right agent framework (Semantic Kernel, AutoGen, LangChain, LangGraph, Azure AI Agent Service) for a given use case.
    5. Build and trace a complete RAG pipeline against mock vendor policy documents.
    6. Explain chunking strategies and when to use each.

    ---

    ## Where Day 3 Sits in the Full Arc

    ```
    Day 1 ──► Day 2 ──►[Day 3]──► Day 4 ──► Day 5 ──►
    Fund.    Arch.    SERVICES  Agent    Multi-Agent
    ```

    Today is primarily hands-on with Azure SDKs. By the end of this notebook you
    have all the building blocks for Day 4 (single-agent loops) and Day 5 (orchestration).
    """)
    return


# ---------------------------------------------------------------------------
# Section 1 – Azure OpenAI Service
# ---------------------------------------------------------------------------
@app.cell
def _s1_header(mo):
    mo.md("## 1. Azure OpenAI Service")
    return


@app.cell
def _s1_body(mo):
    mo.md("""
    **Azure OpenAI Service** is Microsoft's hosted offering of OpenAI models with
    Azure-native identity, compliance, and data residency controls.

    ### Key concepts

    | Concept | Meaning | AegisAP usage |
    |---|---|---|
    | **Resource** | An Azure OpenAI account in a specific region | `aegisap-dev-oai` in `uksouth` |
    | **Deployment** | A named instance of a specific model version | `gpt-4o-extraction`, `gpt-4o-planning` |
    | **Model** | The underlying model (`gpt-4o`, `gpt-4o-mini`, `text-embedding-3-small`) | Varies by task class |
    | **API version** | The REST API version (`2024-10-21`) | Pinned in env var |

    ### Why separate deployments per task?

    ```python
    # BAD — one deployment for everything
    os.environ["AZURE_OPENAI_DEPLOYMENT"] = "gpt-4o"

    # GOOD — separate deployments per task class
    os.environ["AZURE_OPENAI_EXTRACTION_DEPLOYMENT"] = "gpt-4o-mini-extraction"
    os.environ["AZURE_OPENAI_PLANNING_DEPLOYMENT"]   = "gpt-4o-planning"
    os.environ["AZURE_OPENAI_REVIEW_DEPLOYMENT"]     = "gpt-4o-review"
    ```

    Separate deployments enable:
    - **Model tier routing** — swap extraction to `gpt-4o-mini` without touching planning
    - **Quota isolation** — planning doesn't steal tokens from extraction
    - **Cost attribution** — cost per task class is measurable
    - **Independent rollback** — if the new review model regresses, roll it back without touching extraction

    ### Azure best practice
    - Pin the **model version** in the deployment (e.g., `gpt-4o-2024-11-20`), not just the model name.
      Automatic version upgrades can silently change behaviour.
    - Set `temperature=0` for extraction and planning — determinism over creativity.
    - Use `max_tokens` to guard against runaway responses that spike cost.
    """)
    return


@app.cell
def _model_tier_chart(mo):
    mo.md("### Model Tier Comparison")
    return


@app.cell
def _tier_chart(mo):
    try:
        import plotly.graph_objects as go

        models = ["gpt-4o-mini", "gpt-4o", "o3 (reasoning)"]
        # Relative scores 0-10
        capability = [6, 9, 10]
        cost = [1, 5, 9]   # higher = more expensive
        latency = [2, 5, 8]   # higher = slower

        fig = go.Figure(data=[
            go.Bar(name="Capability", x=models,
                   y=capability, marker_color="#27AE60"),
            go.Bar(name="Relative cost", x=models,
                   y=cost, marker_color="#E74C3C"),
            go.Bar(name="Latency (p50)", x=models,
                   y=latency, marker_color="#F5A623"),
        ])
        fig.add_annotation(
            x="gpt-4o-mini", y=6.2, text="Best for extraction & low-risk planning",
            showarrow=False, font=dict(size=10, color="#27AE60"),
        )
        fig.add_annotation(
            x="gpt-4o", y=9.2, text="Default for compliance & high-risk tasks",
            showarrow=False, font=dict(size=10, color="#4A90D9"),
        )
        fig.update_layout(
            barmode="group",
            title="Azure OpenAI Model Tier Trade-offs",
            yaxis_title="Relative score (0=lowest, 10=highest)",
            height=360,
            margin=dict(t=60, b=40),
        )
        mo.ui.plotly(fig)
    except ImportError:
        mo.callout(mo.md("Install `plotly` to see this chart."), kind="warn")
    return


@app.cell
def _structured_outputs(mo):
    mo.md("""
    ### Structured Outputs

    Azure OpenAI supports **structured outputs** — you provide a JSON Schema and
    the model guarantees its response matches exactly.

    ```python
    # NOTE: requires live Azure OpenAI endpoint
    from azure.identity import DefaultAzureCredential
    from openai import AzureOpenAI
    from pydantic import BaseModel
    import json, os

    class InvoiceCandidate(BaseModel):
        invoice_id: str | None
        vendor_id: str | None
        amount: float | None
        currency: str | None
        invoice_date: str | None
        po_number: str | None

    credential = DefaultAzureCredential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default")

    client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_ad_token=token.token,         # ← Managed Identity token, no API key
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    )

    response = client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_EXTRACTION_DEPLOYMENT"],
        messages=[{"role": "user", "content": "Extract fields from: INV-001..."}],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "InvoiceCandidate",
                "strict": True,           # ← guarantees schema compliance
                "schema": InvoiceCandidate.model_json_schema(),
            },
        },
        temperature=0,
        max_tokens=500,
    )
    candidate = json.loads(response.choices[0].message.content)
    ```

    > **`strict: True` is mandatory.** Without it, the model may add extra fields,
    > use wrong types, or omit optional fields inconsistently.
    """)
    return


# ---------------------------------------------------------------------------
# Section 2 – Azure AI Search
# ---------------------------------------------------------------------------
@app.cell
def _s2_header(mo):
    mo.md("## 2. Azure AI Search — Hybrid Search & RRF")
    return


@app.cell
def _s2_body(mo):
    mo.md("""
    **Azure AI Search** is a managed search service that underpins AegisAP's
    Retrieval-Augmented Generation (RAG) pipeline. It supports three query types:

    | Type | Algorithm | Best for |
    |---|---|---|
    | **Full-text (BM25)** | Keyword frequency + inverse document frequency | Exact terms: invoice IDs, vendor names, PO numbers |
    | **Vector** | Approximate nearest-neighbour on embeddings | Semantic similarity: "late payment" ≈ "overdue invoice" |
    | **Hybrid** | BM25 + vector fused via RRF | Both exact matches AND semantic similarity — default choice |

    ### Reciprocal Rank Fusion (RRF)

    RRF combines two ranked lists into one. For each document $d$:

    $$\\text{RRF}(d) = \\sum_{r \\in \\{\\text{BM25, vector}\\}} \\frac{1}{k + \\text{rank}_r(d)}$$

    where $k = 60$ is a smoothing constant. Documents ranked high in **both** lists
    get the best combined score.

    **Why this matters:** A vendor contract clause may use slightly different terminology
    from the invoice. Vector search finds it; BM25 finds the exact invoice ID reference.
    RRF merges both to surface the most relevant chunks.
    """)
    return


@app.cell
def _rrf_simulator(mo):
    mo.md("### RRF Score Simulator")
    return


@app.cell
def _rrf_inputs(mo):
    rank_bm25 = mo.ui.slider(start=1, stop=20, step=1, value=3,
                             label="Document rank in BM25 list (1=best):")
    rank_vec = mo.ui.slider(start=1, stop=20, step=1, value=7,
                            label="Document rank in vector list (1=best):")
    mo.vstack([
        mo.md("Simulate the RRF score for a document with the given ranks in each list:"),
        rank_bm25, rank_vec,
    ])
    return rank_bm25, rank_vec


@app.cell
def _rrf_output(mo, rank_bm25, rank_vec):
    k = 60
    score_bm25 = 1 / (k + rank_bm25.value)
    score_vec = 1 / (k + rank_vec.value)
    rrf_score = score_bm25 + score_vec

    # Compare with a document that is rank 1 in both
    best_rrf = 1/(k+1) + 1/(k+1)

    mo.callout(
        mo.md(f"""
**BM25 contribution:** 1 / (60 + {rank_bm25.value}) = {score_bm25:.6f}  
**Vector contribution:** 1 / (60 + {rank_vec.value}) = {score_vec:.6f}  
**RRF score:** {rrf_score:.6f}  

**Best possible score** (rank 1 in both): {best_rrf:.6f}  
**This document's relative quality:** {(rrf_score/best_rrf)*100:.1f}% of maximum
        """),
        kind="info",
    )
    return best_rrf, k, rrf_score, score_bm25, score_vec


@app.cell
def _search_client_code(mo):
    mo.md("""
    ### SearchClient with Managed Identity

    ```python
    # NOTE: requires live Azure AI Search endpoint + Search Index Data Reader role
    from azure.identity import DefaultAzureCredential
    from azure.search.documents import SearchClient
    from azure.search.documents.models import VectorizedQuery
    import os

    credential = DefaultAzureCredential()   # ← no admin key

    client = SearchClient(
        endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
        index_name="vendor-policies",
        credential=credential,
    )

    # Hybrid search: keyword + vector combined via RRF
    results = client.search(
        search_text="payment terms net-30",          # BM25 keywords
        vector_queries=[VectorizedQuery(
            vector=embedding_vector,                  # pre-computed embedding
            k_nearest_neighbors=5,
            fields="content_vector",
        )],
        query_type="semantic",                        # enable semantic reranking
        semantic_configuration_name="default",
        select=["chunk_id", "document_id", "content", "authority_score"],
        top=5,
    )

    chunks = [
        {"chunk_id": r["chunk_id"], "content": r["content"], "score": r["@search.score"]}
        for r in results
    ]
    ```

    > **RBAC:** The application identity needs `Search Index Data Reader` — not
    > `Search Service Contributor`. Never use admin keys in application code.
    """)
    return


# ---------------------------------------------------------------------------
# Section 3 – Chunking Strategies
# ---------------------------------------------------------------------------
@app.cell
def _s3_header(mo):
    mo.md("## 3. Chunking Strategies for the Search Index")
    return


@app.cell
def _s3_body(mo):
    mo.md("""
    Before documents can be retrieved, they must be split into **chunks** and
    embedded. Chunking strategy directly determines retrieval quality.

    | Strategy | Chunk size approx. | Pros | Cons | Best for |
    |---|---|---|---|---|
    | **Fixed-size** | 512 tokens | Simple, predictable | Cuts context mid-sentence | Technical docs with dense structure |
    | **Sentence** | 1–3 sentences | Preserves atomic meaning | Variable sizes; small chunks may lose context | FAQs, short policy clauses |
    | **Paragraph** | 1 paragraph | Self-contained policy clauses | Paragraph length varies widely | Policy documents, contracts — AegisAP's choice |
    | **Hierarchical (parent/child)** | Small child + large parent | High precision (child) + rich context (parent) | Complex indexing pipeline | Long-form documents with section structure |

    AegisAP uses **paragraph-level chunking** for vendor policy and compliance documents
    because policy clauses are self-contained — splitting a clause in half loses the nuance.
    """)
    return


@app.cell
def _chunking_demo(mo):
    mo.md("### Chunking Demo — See the Effect")
    return


@app.cell
def _chunk_strategy(mo):
    strat = mo.ui.radio(
        options=["Fixed-size (200 chars)", "Sentence", "Paragraph"],
        value="Paragraph",
        label="Chunking strategy:",
    )
    strat
    return (strat,)


@app.cell
def _chunk_output(mo, strat):
    sample_text = """Payment Terms and Conditions.

All invoices are due within 30 days of receipt (net-30). Where a purchase order number is present, payment is contingent on PO validation in the procurement system.

For invoices exceeding £10,000, controller approval is required before payment is released. The approval must be recorded in the AegisAP approval log.

Late Payment Policy. Invoices not paid within 60 days will incur a 2% per quarter late payment charge, as permitted under the Late Payment of Commercial Debts Act 1998. Vendors should contact accounts@company.com to dispute any late payment charges."""

    if "Fixed" in strat.value:
        size = 200
        chunks = [sample_text[i:i+size]
                  for i in range(0, len(sample_text), size)]
    elif "Sentence" in strat.value:
        import re
        sentences = re.split(r'(?<=[.!?])\s+', sample_text)
        chunks = [" ".join(sentences[i:i+2])
                  for i in range(0, len(sentences), 2)]
    else:
        chunks = [p.strip()
                  for p in sample_text.strip().split("\n\n") if p.strip()]

    chunk_items = []
    for i, chunk in enumerate(chunks, 1):
        chunk_items.append(mo.callout(
            mo.md(f"**Chunk {i}** ({len(chunk)} chars):\n\n> {chunk}"),
            kind="neutral",
        ))

    mo.vstack([
        mo.md(f"**Strategy: {strat.value} → {len(chunks)} chunks produced**"),
        *chunk_items,
    ])
    return chunk_items, chunks, i, sample_text


# ---------------------------------------------------------------------------
# Section 4 – Agent Framework Landscape
# ---------------------------------------------------------------------------
@app.cell
def _s4_header(mo):
    mo.md("## 4. Agent Framework Landscape")
    return


@app.cell
def _framework_selector(mo):
    fw = mo.ui.dropdown(
        options=[
            "LangGraph",
            "Azure AI Agent Service",
            "Semantic Kernel",
            "AutoGen",
            "LangChain",
        ],
        value="LangGraph",
        label="Select a framework to explore:",
    )
    fw
    return (fw,)


@app.cell
def _framework_detail(mo, fw):
    frameworks = {
        "LangGraph": {
            "vendor": "LangChain, Inc. (open source)",
            "paradigm": "Stateful directed graph — nodes are Python functions, edges are transitions",
            "state_management": "Typed state object flows through nodes; supports persistent checkpointers",
            "azure_integration": "Manual — use Azure SDKs inside nodes; no native Azure binding",
            "best_for": "Complex workflows with branching logic, durable state, and HITL requirements",
            "worst_for": "Simple single-agent Q&A or rapid prototyping (more boilerplate than alternatives)",
            "aegisap_use": "Primary orchestration layer — AegisAP's LangGraph workflow IS the Day 5 system",
            "code_style": """
# Define a LangGraph state machine node
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

class WorkflowState(TypedDict):
    invoice_amount: float
    routing: Literal["auto_approve", "review_required"] | None

def determine_routing(state: WorkflowState) -> WorkflowState:
    if state["invoice_amount"] > 10_000:
        return {**state, "routing": "review_required"}
    return {**state, "routing": "auto_approve"}

graph = StateGraph(WorkflowState)
graph.add_node("routing", determine_routing)
""",
        },
        "Azure AI Agent Service": {
            "vendor": "Microsoft Azure (managed service)",
            "paradigm": "Managed agent threads — Azure hosts conversation history, tool dispatch, and retry",
            "state_management": "Azure-managed thread objects; no self-managed state",
            "azure_integration": "Native — built on Azure AI Foundry; direct integration with Azure AI Search, Code Interpreter",
            "best_for": "Conversational agents, single-turn task completion, quick prototyping with Azure tools",
            "worst_for": "Complex multi-step orchestration with custom branching; durable workflow with PostgreSQL",
            "aegisap_use": "Discussed as an alternative but not used — LangGraph is required for durable HITL",
            "code_style": """
# Azure AI Agent Service pattern
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["AZURE_AI_PROJECT_CONNECTION_STRING"],
)
agent = client.agents.create_agent(
    model="gpt-4o",
    name="invoice-triage",
    tools=client.agents.get_file_search_tool(),
)
thread = client.agents.create_thread()
""",
        },
        "Semantic Kernel": {
            "vendor": "Microsoft (open source, MIT)",
            "paradigm": "Plugin-based — skills are C# or Python functions registered as plugins",
            "state_management": "Chat history object; plugins can use kernel memory or custom stores",
            "azure_integration": "Deep — native Azure OpenAI connector, Azure AI Search connector, Cosmos DB memory",
            "best_for": "Microsoft-stack integration, .NET projects, plugin composition with Azure services",
            "worst_for": "Complex Python-native ML workflows; teams unfamiliar with plugin composition model",
            "aegisap_use": "Not used — Python-native LangGraph was the right choice for ML/AI Python ecosystem",
            "code_style": """
# Semantic Kernel plugin pattern
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

kernel = Kernel()
kernel.add_service(AzureChatCompletion(
    deployment_name=os.environ["AZURE_OPENAI_DEPLOYMENT"],
    endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    ad_token_provider=DefaultAzureCredential(),
))
""",
        },
        "AutoGen": {
            "vendor": "Microsoft Research (open source)",
            "paradigm": "Multi-agent conversation — agents exchange messages in a configurable topology",
            "state_management": "Conversation history; custom agent memories via plugins",
            "azure_integration": "Moderate — uses Azure OpenAI; no first-class Azure data service connectors",
            "best_for": "Multi-agent debate, code generation with reviewer feedback, research workflows",
            "worst_for": "Deterministic business workflows requiring auditability; regulated financial decisions",
            "aegisap_use": "Not used — conversational topology is hard to audit for financial decisions",
            "code_style": """
# AutoGen multi-agent conversation
import autogen

planner = autogen.AssistantAgent("planner", llm_config={"model": "gpt-4o"})
reviewer = autogen.AssistantAgent("reviewer", llm_config={"model": "gpt-4o"})
user_proxy = autogen.UserProxyAgent("user", human_input_mode="NEVER")

# Agents converse until termination condition
user_proxy.initiate_chat(planner, message="Plan the invoice tasks...")
""",
        },
        "LangChain": {
            "vendor": "LangChain, Inc. (open source)",
            "paradigm": "Chain composition — LCEL (LangChain Expression Language) pipes operations",
            "state_management": "ConversationBufferMemory and similar; not naturally durable",
            "azure_integration": "Good — Azure OpenAI, Azure AI Search, Azure Cosmos DB integrations exist",
            "best_for": "Rapid prototyping, simple RAG pipelines, teams with existing LangChain knowledge",
            "worst_for": "Complex stateful workflows with branching (use LangGraph instead); production-grade HITL",
            "aegisap_use": "Dependency chain includes LangChain; LCEL used for simple retrieval chains in Day 3",
            "code_style": """
# LangChain LCEL RAG chain
from langchain_openai import AzureChatOpenAI
from langchain_core.runnables import RunnablePassthrough

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
llm = AzureChatOpenAI(deployment_name=os.environ["AZURE_OPENAI_DEPLOYMENT"])

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt_template
    | llm
)
answer = chain.invoke("What are the payment terms for ACME?")
""",
        },
    }

    d = frameworks[fw.value]
    code_block = f"```python{d['code_style']}```"
    mo.vstack([
        mo.callout(
            mo.md(f"""
**{fw.value}**

| Property | Detail |
|---|---|
| **Vendor** | {d['vendor']} |
| **Paradigm** | {d['paradigm']} |
| **State management** | {d['state_management']} |
| **Azure integration** | {d['azure_integration']} |
| **Best for** | {d['best_for']} |
| **Avoid when** | {d['worst_for']} |
| **AegisAP use** | {d['aegisap_use']} |
            """),
            kind="info",
        ),
        mo.md("**Code style example:**"),
        mo.md(code_block),
    ])
    return code_block, d, frameworks


@app.cell
def _framework_matrix(mo):
    mo.md("""
    ### Framework Selection Matrix

    | Use case | Recommended framework | Why |
    |---|---|---|
    | Complex approval workflow with branching + durable HITL | **LangGraph** | Explicit state graph + PostgreSQL checkpointer |
    | Conversational agent within Azure AI Foundry | **Azure AI Agent Service** | Managed threads, native Azure tool integration |
    | .NET / C# enterprise integration | **Semantic Kernel** | First-class .NET SDK, Azure plugin ecosystem |
    | Multi-agent code generation with review loop | **AutoGen** | Conversational topology suits debate/review |
    | Quick RAG prototype in Python | **LangChain** | Fastest path from idea to demo; upgrade to LangGraph when workflow complexity grows |

    > **There is no universally "best" framework.** The question is always:
    > "What is the workflow topology, what state guarantees do we need, and what
    > Azure services must we integrate with?"
    """)
    return


# ---------------------------------------------------------------------------
# Section 5 – RAG Pipeline Walkthrough
# ---------------------------------------------------------------------------
@app.cell
def _s5_header(mo):
    mo.md("## 5. RAG Pipeline: End-to-End Walkthrough")
    return


@app.cell
def _rag_diagram(mo):
    mo.md("""
    ```
    QUERY: "What are the payment terms for Acme Office Supplies?"
        │
        ▼
    [ embed query ]  →  text-embedding-3-small  →  float[1536]
        │
        ▼
    [ Azure AI Search: hybrid query ]
        │
        ├── BM25: "payment terms" "Acme"  →  ranked list A
        │
        └── Vector: cosine similarity     →  ranked list B
        │
        ▼
    [ RRF score fusion ]  →  merged ranked list
        │
        ▼
    [ Semantic reranking (optional) ]  →  re-ranked top-5
        │
        ▼
    [ Top-5 chunks with chunk_id + score ]
        │
        ▼
    [ Build augmented prompt ]
        │  system: "Answer using ONLY the provided documents."
        │  user:   "Documents: [chunk1]...[chunk5]"
        │  user:   "Question: What are the payment terms..."
        ▼
    [ Azure OpenAI gpt-4o ]
        │
        ▼
    Answer + citations  →  { "answer": "Net-30...", "citations": ["chunk_id_42"] }
    ```
    """)
    return


@app.cell
def _rag_demo(mo):
    mo.md("### Simulated RAG Pipeline (no Azure required)")
    return


@app.cell
def _rag_query_input(mo):
    query = mo.ui.text(
        value="What are the payment terms for Acme Office Supplies?",
        label="Search query:",
        full_width=True,
    )
    query
    return (query,)


@app.cell
def _rag_simulate(mo, query):
    import math

    # Mock document chunks (vendor policy excerpts)
    mock_chunks = [
        {
            "chunk_id": "acme_contract_s2_p1",
            "document_id": "ACME_MASTER_AGREEMENT_2024",
            "content": "Payment terms for Acme Office Supplies: all invoices are due within 30 days of receipt (net-30). Early payment discount of 2% applies if paid within 10 days.",
            "keywords": ["payment", "terms", "Acme", "net-30", "30 days"],
        },
        {
            "chunk_id": "ap_policy_s3_p4",
            "document_id": "AP_POLICY_RULEBOOK_V3",
            "content": "For invoices exceeding £10,000, controller approval is required before payment is released, regardless of vendor payment terms.",
            "keywords": ["approval", "£10,000", "controller", "payment"],
        },
        {
            "chunk_id": "acme_contract_s4_p2",
            "document_id": "ACME_MASTER_AGREEMENT_2024",
            "content": "Purchase order references are mandatory for all Acme invoices. Invoices without a valid PO number will be returned to sender.",
            "keywords": ["purchase order", "PO", "Acme", "mandatory"],
        },
        {
            "chunk_id": "late_payment_s1_p1",
            "document_id": "AP_POLICY_RULEBOOK_V3",
            "content": "Late payment charges: invoices unpaid after 60 days incur a 2% quarterly charge under the Late Payment of Commercial Debts Act 1998.",
            "keywords": ["late payment", "60 days", "2%", "charge"],
        },
        {
            "chunk_id": "vat_rules_s2_p3",
            "document_id": "HMRC_VAT_NOTICE_700",
            "content": "Standard rate of VAT at 20% applies to general business supplies including office equipment and consumables.",
            "keywords": ["VAT", "20%", "standard rate", "office"],
        },
    ]

    q_lower = query.value.lower()
    q_words = set(q_lower.split())

    # Simulated BM25 scoring (simplified: count keyword hits)
    def bm25_score(chunk):
        hits = sum(1 for kw in chunk["keywords"] if kw.lower() in q_lower)
        return hits / (len(chunk["keywords"]) + 1)

    # Simulated vector score (simplified: word overlap %)
    def vector_score(chunk):
        c_words = set(chunk["content"].lower().split())
        overlap = len(q_words & c_words) / max(len(q_words), 1)
        return min(overlap * 2, 1.0)

    k = 60
    results = []
    for chunk in mock_chunks:
        bs = bm25_score(chunk)
        vs = vector_score(chunk)
        results.append({**chunk, "bm25": bs, "vector": vs})

    # Rank by each method
    bm25_ranked = sorted(results, key=lambda x: x["bm25"], reverse=True)
    vec_ranked = sorted(results, key=lambda x: x["vector"], reverse=True)

    bm25_ranks = {r["chunk_id"]: i+1 for i, r in enumerate(bm25_ranked)}
    vec_ranks = {r["chunk_id"]: i+1 for i, r in enumerate(vec_ranked)}

    for r in results:
        r["rrf"] = 1/(k + bm25_ranks[r["chunk_id"]]) + \
            1/(k + vec_ranks[r["chunk_id"]])

    final = sorted(results, key=lambda x: x["rrf"], reverse=True)

    rows = []
    for rank, r in enumerate(final, 1):
        rows.append(
            f"| {rank} | `{r['chunk_id']}` | {r['bm25']:.3f} | {r['vector']:.3f} | **{r['rrf']:.5f}** |"
        )

    top_chunk = final[0]
    mo.vstack([
        mo.md(f"""
**Query:** _{query.value}_

**Retrieval results (simulated — not calling Azure):**

| Rank | Chunk ID | BM25 | Vector | RRF |
|---|---|---|---|---|
""" + "\n".join(rows)),
        mo.callout(
            mo.md(f"""
**Top retrieved chunk:** `{top_chunk['chunk_id']}`

> {top_chunk['content']}

**Simulated answer:** *"Based on document `{top_chunk['document_id']}`,  
payment terms for Acme Office Supplies are net-30 (30 days from receipt)."*

**Citation:** `{{"chunk_id": "{top_chunk['chunk_id']}", "document_id": "{top_chunk['document_id']}"}}`
            """),
            kind="success",
        ),
    ])
    return (
        bm25_ranked,
        bm25_ranks,
        bm25_score,
        bs,
        chunk,
        final,
        k,
        mock_chunks,
        q_lower,
        q_words,
        r,
        rank,
        results,
        rows,
        top_chunk,
        vec_ranked,
        vec_ranks,
        vec_score,
        vector_score,
        vs,
    )


# ---------------------------------------------------------------------------
# Section 6 – Multi-Agent Retrieval Pattern
# ---------------------------------------------------------------------------
@app.cell
def _s6_header(mo):
    mo.md("## 6. Multi-Agent Retrieval Pattern")
    return


@app.cell
def _s6_body(mo):
    mo.md("""
    AegisAP splits retrieval across specialised sub-agents. Each agent queries
    a different index scope and brings domain knowledge to its queries.

    ```
    Orchestrator
        │
        ├── VendorPolicyAgent
        │     └── Azure AI Search: filter=vendor_id eq 'ACME'
        │         Returns: payment terms, PO requirements, bank details
        │
        ├── ComplianceAgent
        │     └── Azure AI Search: filter=document_type eq 'regulation'
        │         Returns: VAT rules, late payment act, approval thresholds
        │
        └── EvidenceAggregator
              ├── Merges results from both agents
              ├── Deduplicates by chunk_id
              ├── Ranks by authority score (policy docs > general guidance)
              └── Returns top-N chunks with provenance chain
    ```

    **Why sub-agents rather than one big query?**

    1. **Index scope isolation** — vendor-specific rules query a vendor index; compliance rules query a regulatory index. Mixing them in one query degrades precision.
    2. **Authority clarity** — each agent knows the trust tier of its index.
    3. **Independent testability** — `VendorPolicyAgent` can be tested without the compliance index.
    4. **Failure isolation** — if the compliance index returns 0 results, the vendor evidence still flows; the orchestrator decides whether to proceed or escalate.

    ### Citations as First-Class Data

    Every claim produced by the system must reference the specific chunk that supports it:

    ```json
    {
      "claim": "VAT at 20% applies to this office supplies invoice",
      "citation": {
        "chunk_id": "vat_rules_s2_p3",
        "document_id": "HMRC_VAT_NOTICE_700",
        "score": 0.91,
        "excerpt": "Standard rate of VAT at 20% applies to general business supplies..."
      }
    }
    ```

    Without citations, the system cannot:
    - Be audited (what document justified this decision?)
    - Be debugged (which chunk caused a wrong recommendation?)
    - Be improved (low-scoring citations reveal knowledge base gaps)
    """)
    return


# ---------------------------------------------------------------------------
# Lab Exercises
# ---------------------------------------------------------------------------
@app.cell
def _exercises_header(mo):
    mo.md("## Exercises")
    return


@app.cell
def _exercise_1(mo):
    mo.accordion({
        "Exercise 1 — Configure a SearchClient (no admin key)": mo.vstack([
            mo.md("""
**Task:** Write the Python code to create an `azure.search.documents.SearchClient`
that authenticates using `DefaultAzureCredential`. Include:

1. The import statements
2. The credential instantiation (no API key)
3. The client instantiation using environment variables
4. A single keyword search call that returns the top-3 results
5. The RBAC role needed on the Search service for this to work
            """),
            mo.accordion({
                "Show solution": mo.md("""
```python
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
import os

# 1. Create credential — uses az login in dev, Managed Identity in prod
credential = DefaultAzureCredential()

# 2. Create client — no API key, no admin key
client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name="vendor-policies",
    credential=credential,
)

# 3. Keyword search
results = client.search(
    search_text="payment terms net-30",
    select=["chunk_id", "document_id", "content"],
    top=3,
)

for result in results:
    print(result["chunk_id"], result["content"][:100])

# Required RBAC role:
# "Search Index Data Reader" on the Azure AI Search service
# — not "Search Service Contributor" (admin) or "Owner"
```
                """),
            }),
        ]),
    })
    return


@app.cell
def _exercise_2(mo):
    mo.accordion({
        "Exercise 2 — Model Tier Assignment": mo.vstack([
            mo.md("""
**Task:** For each of the following AegisAP task types, state which model tier
you would choose (`gpt-4o-mini`, `gpt-4o`, or `o3`) and justify your choice
in one sentence.

1. Extracting structured fields from a standard invoice PDF (low OCR noise)
2. Generating an `ExecutionPlan` for a high-value invoice (£85,000) from a new vendor
3. Day 6 policy compliance review — determining if evidence is sufficient to authorise payment
4. Generating a brief summary of the approval reason for a dashboard notification
5. Extracting fields from a multi-language invoice with heavy OCR noise
            """),
            mo.accordion({
                "Show solution": mo.md("""
1. **gpt-4o-mini** — Standard extraction from clean text is a low-complexity structured output task; the cost saving is significant at scale.

2. **gpt-4o** — High-value invoices are high-risk; a wrong plan could authorise an incorrect payment. Do not save a few pence on planning a case where the financial exposure is £85,000.

3. **gpt-4o** (never mini) — Policy compliance is the highest-risk task class. Even a small accuracy degradation from using a lighter model is unacceptable for regulated financial decisions.

4. **gpt-4o-mini** — Notification summaries are low-stakes; the output is reviewed by a human before action is taken. A slight quality reduction is acceptable.

5. **gpt-4o** — Heavy OCR noise requires stronger semantic understanding to disambiguate garbled characters. The additional cost is justified by the accuracy gain on noisy inputs.
                """),
            }),
        ]),
    })
    return


@app.cell
def _exercise_3(mo):
    mo.accordion({
        "Exercise 3 — Build a Simple RAG Query": mo.vstack([
            mo.md("""
**Task:** Using the mock RAG simulator in Section 5, modify the search query
to find information about late payment charges.

1. How does the ranking change compared to the payment terms query?
2. Which chunks surfaced that were not in the top-3 before?
3. If you were building the prompt for the LLM, what system message would you write to prevent the model from fabricating a late payment rate that is not in the retrieved chunks?
            """),
            mo.accordion({
                "Show solution": mo.md("""
**1.** Query: *"What are the late payment charges?"*

The `late_payment_s1_p1` chunk (Late Payment Act details) moves from rank 4 to rank 1.
The `acme_contract_s2_p1` (net-30 terms) drops because it has fewer keyword overlaps.
The `vat_rules_s2_p3` chunk remains relevant because it mentions "payment" and "commercial".

**2.** `late_payment_s1_p1` surfaces as rank 1 — not previously in the top-3 for the payment terms query.

**3.** System message to prevent fabrication:
```
You are a compliance assistant for accounts payable. Answer the user's question
using ONLY the information in the provided document chunks below.

If the answer is not contained in the provided chunks, say:
"The retrieved documents do not contain information about this. I cannot provide
a figure without authoritative evidence."

Do NOT use training knowledge about late payment rates, VAT rates, or legal
requirements — only the provided documents constitute authoritative evidence.
```

This instruction enforces data-plane separation: the model's training knowledge
(control-plane, internal) cannot override retrieved documents (data-plane, external).
                """),
            }),
        ]),
    })
    return


@app.cell
def _exercise_4(mo):
    mo.accordion({
        "Exercise 4 — Framework Selection Scenario": mo.vstack([
            mo.md("""
**Scenario:** You are building a legal document review agent for a law firm.
The agent must:
- Accept a PDF contract and a list of review questions
- Retrieve relevant clauses from a document store (Azure AI Search)
- For each question, produce an answer + specific clause citation
- Flag 'high-risk' clauses for the lead solicitor to review
- Store review history so a case can be resumed if the solicitor interrupts

**Task:** Choose one framework from the selection matrix and justify your choice.
State one advantage and one limitation of your choice for this use case.
            """),
            mo.accordion({
                "Show solution": mo.md("""
**Recommended: LangGraph**

**Justification:** The use case has:
- Multi-step workflow (retrieve → answer each question → flag high-risk → await solicitor)
- Durable state requirement (case must be resumable)
- Branching logic (different paths for high-risk vs. standard clauses)
- HITL pause/resume (solicitor interrupts; system must persist state)

All of these point to LangGraph's directed graph with a PostgreSQL checkpointer.

**Advantage:** Full workflow auditability — every node transition is a timestamped
state record. Law firms require complete audit trails for legal defensibility.

**Limitation:** LangGraph requires more upfront design than LangChain or AIAS.
You must explicitly define the state schema and graph topology before writing
logic nodes. For a one-question, one-answer prototype, LangChain LCEL would be
faster; plan to migrate to LangGraph when case resumability is required.
                """),
            }),
        ]),
    })
    return


# ---------------------------------------------------------------------------
# Artifact
# ---------------------------------------------------------------------------
@app.cell
def _artifact_write(mo, json, Path):
    import datetime

    artifact = {
        "day": 3,
        "title": "Azure AI Services & Agent Frameworks",
        "completed_at": datetime.datetime.utcnow().isoformat() + "Z",
        "framework_selection": {
            "orchestration": "LangGraph",
            "rationale": "Durable state graph with HITL checkpoint/resume",
        },
        "model_tier_decisions": {
            "extraction_standard": "gpt-4o-mini",
            "extraction_complex": "gpt-4o",
            "planning_high_risk": "gpt-4o",
            "review_compliance": "gpt-4o",
        },
        "chunking_strategy": "paragraph",
        "search_type": "hybrid_rrf",
        "gate_passed": True,
    }

    out_dir = Path(__file__).resolve().parents[1] / "build" / "day3"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "framework_selection.json"
    out_path.write_text(json.dumps(artifact, indent=2))

    mo.callout(
        mo.md(
            f"Artifact written to `{out_path.relative_to(Path(__file__).resolve().parents[1])}`"),
        kind="success",
    )
    return artifact, datetime, out_dir, out_path


# ---------------------------------------------------------------------------
# Production Reflection
# ---------------------------------------------------------------------------
@app.cell
def _reflection(mo):
    mo.md("""
    ## Production Reflection

    1. **Framework lock-in:** What is the cost of choosing LangChain for a project
       that later needs durable state and HITL? Describe the migration path.

    2. **Chunking in production:** A vendor adds a 10-clause amendment to their
       contract and your RAG pipeline starts returning wrong payment terms.
       What is the most likely cause, and how do you detect it before it affects invoice processing?

    3. **Citation integrity:** A solicitor asks "which document supports the 20% VAT rate
       in this approval?" What does AegisAP need to have stored to answer this question,
       and where is that data persisted?
    """)
    return


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
@app.cell
def _summary(mo):
    mo.md("""
    ## Day 3 Summary Checklist

    - [ ] Explain why separate Azure OpenAI deployments per task class are preferable to a single deployment
    - [ ] Configure a `SearchClient` with `DefaultAzureCredential` (not an admin key)
    - [ ] Explain hybrid search and RRF score fusion with the mathematical formula
    - [ ] Select a chunking strategy for a given document type and justify it
    - [ ] Select an agent framework for a given use case and state one advantage and one limitation
    - [ ] Build a RAG query and explain what a citation must contain to be auditable
    - [ ] Artifact `build/day3/framework_selection.json` exists and `gate_passed = true`
    - [ ] Name the four Azure identity planes and state which Day introduces deployment-grade controls for each
    - [ ] Explain what On-Behalf-Of (OBO) is and why `DefaultAzureCredential` alone is insufficient for delegated approval flows
    """)
    return


@app.cell
def _forward(mo):
    mo.callout(
        mo.md("""
**Tomorrow — Day 4: Building Single-Agent Loops with Tools, Memory & Planning**

We go from service clients to a working agent. You will implement the AegisAP extraction
pipeline (`InvoiceCandidate → CanonicalInvoice`), build the planner-executor pattern with
a typed JSON plan, apply a policy overlay, and verify that the system fails closed on every
invalid plan or policy violation.

Open `notebooks/day_4_single_agent_loops.py` when ready.
        """),
        kind="success",
    )
    return


# ---------------------------------------------------------------------------
# Section 7 – Identity Plane Bridge
# (Bridges Day 1 blast-radius concept → Day 8 deployment planes → Day 11 OBO)
# ---------------------------------------------------------------------------
@app.cell
def _s_identity_bridge_header(mo):
    mo.md("## 7. Identity Plane Bridge")
    return


@app.cell
def _s_identity_bridge_body(mo):
    mo.md("""
    > **Bridge note:** Day 1 introduced the concept of identity *blast radius* — the damage
    > that occurs if a runtime identity is over-privileged. Day 8 will implement
    > *deployment-grade* identity controls (OIDC workload federation for CI/CD, Managed
    > Identity for all runtime paths). **Day 11** extends this with the delegated-identity
    > (On-Behalf-Of) pattern required when the orchestrator must act on behalf of a human
    > approver. This section is the connective tissue between those three Days.

    ### The Four Azure Identity Planes

    | Plane | What it controls | Primary mechanism | Day hardened |
    |---|---|---|---|
    | **Control plane** | ARM operations — create/delete/resize resources | Azure RBAC (Contributor, Owner, etc.) | 8, 11 |
    | **Data plane** | Service-level operations — read blobs, query Search index, post to OpenAI | Service RBAC (Search Index Reader, Cognitive Services User) | 1, 3, 8 |
    | **Application plane** | Business logic — which invoices the agent can approve, which vendors it can query | Custom Entra App Roles + policy overlay | 4, 11 |
    | **Delegation plane** | Acting on behalf of a human — OBO token exchange so the agent's approval carries the human‑approver's identity | OAuth 2.0 On-Behalf-Of + MSAL | **11** |

    ### Why `DefaultAzureCredential` Is Not Enough for Day 11

    `DefaultAzureCredential` acquires a token for the **application's own identity** (a
    Managed Identity or a service principal). This is correct for the data plane —
    querying Azure AI Search or posting a completion request.

    However, in a regulated AP workflow, an approval must carry the *human approver's*
    identity, not the orchestrator's. If a payment is challenged in an audit, the audit
    trail must show **who** approved it, not merely *which system* processed it.

    The On-Behalf-Of (OBO) flow solves this:
    1. The human approver authenticates with Entra and receives an access token scoped
       to the AegisAP front-end application.
    2. The front-end passes that token to the orchestrator API.
    3. The orchestrator calls the MSAL OBO endpoint to exchange **the user's token** for
       a downstream service token — still carrying the user's `oid`, `upn`, and group claims.
    4. The `ActorVerifier` (Day 11) confirms the `oid` belongs to the correct Entra group
       before the approval is committed.

    > **Forward pointer:** Day 11 (`notebooks/day_11_delegated_identity_obo.py`) implements
    > this end-to-end, adds the `gate_delegated_identity` acceptance gate, and produces
    > `build/day11/obo_contract.json`.

    ### Identity Blast Radius — Updated for Four Planes

    ```
    Compromised Managed Identity (data plane only)
    → Can read/write blobs, query Search, call OpenAI
    → CANNOT create/delete resources (no control-plane role)
    → CANNOT approve invoices above threshold (no app role)
    → CANNOT forge a human-signed approval (no OBO token)

    Blast radius = bounded to data-plane operations within this resource group.
    ```

    This is why each plane must be hardened independently. A data-plane breach is serious;
    a delegation-plane breach means fraudulent approvals carry valid human identities.
    """)
    return


# ---------------------------------------------------------------------------
# Section 8 – Azure AI Foundry / Agent Service Lab
# ---------------------------------------------------------------------------
@app.cell
def _s_foundry_header(mo):
    mo.md("## 8. Azure AI Foundry / Agent Service Lab")
    return


@app.cell
def _s_foundry_body(mo):
    mo.md("""
    **Azure AI Foundry** (formerly Azure AI Studio + Azure Machine Learning unified portal)
    is the managed platform for deploying, evaluating, and operating AI agents at
    enterprise scale. **Azure AI Agent Service** is the hosted agent runtime within Foundry —
    it provides durable threads, built-in tool calling, file search, and code interpreter
    without requiring you to manage LangGraph checkpointers or state storage yourself.

    ### When to Use Azure AI Agent Service vs LangGraph

    | Criterion | Azure AI Agent Service | LangGraph |
    |---|---|---|
    | Hosting | Fully managed (no infra) | Self-managed (ACA/AKS) |
    | State durability | Built-in thread persistence | PostgreSQL checkpointer — you manage schema |
    | Custom checkpointing | ❌ | ✅ (full control) |
    | Tool calling | OpenAI function-calling format | Any Python callable |
    | Streaming | Native | Via LangGraph streaming API |
    | Cost model | Per-token + agent overhead | Infra cost only |
    | **Best for** | Rapid prototyping, low-ops | Production with custom state, HITL, complex graph |

    > **AegisAP choice:** LangGraph for production (Days 4–10) because we need custom
    > PostgreSQL checkpointing for durable state replay (Day 5), explicit policy overlay
    > on the plan graph (Day 4), and the ability to inject HITL nodes at arbitrary points
    > (Day 6). Azure AI Agent Service is appropriate for the Day 3 lab exercise below.

    ### Lab: Minimal Invoice-Triage Agent with Azure AI Agent Service

    The cell below builds a minimal invoice-triage agent using the `azure-ai-projects`
    SDK. It demonstrates how Foundry manages threads, how tool calls appear in the
    thread run, and what a framework-selection rubric artifact looks like.
    """)
    return


@app.cell
def _s_foundry_lab(mo, json, os):
    from pathlib import Path

    # ------------------------------------------------------------------
    # Framework selection rubric — written as artifact regardless of
    # whether a live Foundry endpoint is available.
    # ------------------------------------------------------------------
    _rubric = {
        "evaluated_at": "day3_lab",
        "use_case": "invoice_triage",
        "criteria": {
            "multi_step_workflow": True,
            "durable_state_required": True,
            "hitl_pause_resume": True,
            "custom_tool_calling": True,
            "low_ops_priority": False,
        },
        "scores": {
            "azure_ai_agent_service": {
                "total": 2,
                "advantage": "zero_ops_overhead",
                "limitation": "no_custom_checkpointing",
            },
            "langgraph": {
                "total": 5,
                "advantage": "full_graph_control_and_hitl",
                "limitation": "requires_postgres_checkpointer_setup",
            },
        },
        "recommendation": "langgraph",
        "gate_passed": True,
    }
    _out = Path(__file__).resolve().parents[1] / "build" / "day3"
    _out.mkdir(parents=True, exist_ok=True)
    (_out / "framework_rubric_day3.json").write_text(json.dumps(_rubric, indent=2))

    # ------------------------------------------------------------------
    # Live Foundry demo — only runs if AZURE_AI_PROJECT_ENDPOINT is set.
    # ------------------------------------------------------------------
    _endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "")
    if _endpoint:
        try:
            # type: ignore[import-untyped]
            from azure.ai.projects import AIProjectClient
            from azure.identity import DefaultAzureCredential

            _client = AIProjectClient(
                endpoint=_endpoint, credential=DefaultAzureCredential())
            _agent = _client.agents.create_agent(
                model="gpt-4o-mini",
                name="invoice-triage-demo",
                instructions=(
                    "You are a triage assistant. Given an invoice description, "
                    "classify it as AUTO_APPROVE, ESCALATE, or REJECT and give one reason."
                ),
            )
            _thread = _client.agents.create_thread()
            _client.agents.create_message(
                thread_id=_thread.id,
                role="user",
                content="Invoice: ACME Corp, £450, office supplies. Approve?",
            )
            _run = _client.agents.create_and_process_run(
                thread_id=_thread.id, agent_id=_agent.id
            )
            _msgs = _client.agents.list_messages(thread_id=_thread.id)
            _reply = next(
                (m.content[0].text.value for m in _msgs.data if m.role == "assistant"),
                "No reply",
            )
            _client.agents.delete_agent(_agent.id)
            _result = mo.callout(
                mo.md(
                    f"**Foundry agent reply:** {_reply}\n\nRubric artifact written → `build/day3/framework_rubric_day3.json`"),
                kind="success",
            )
        except Exception as _exc:
            _result = mo.callout(
                mo.md(
                    f"Foundry live call skipped: `{_exc}`\n\nRubric artifact written → `build/day3/framework_rubric_day3.json`"),
                kind="warn",
            )
    else:
        _result = mo.callout(
            mo.md(
                "**No `AZURE_AI_PROJECT_ENDPOINT` set** — live Foundry demo skipped. "
                "Set the env var to run the agent against a real AI Foundry project.\n\n"
                "Rubric artifact written → `build/day3/framework_rubric_day3.json`"
            ),
            kind="neutral",
        )
    _result
    return



@app.cell
def _fde_learning_contract(mo):
    mo.md(r"""
    ---
    ## FDE Learning Contract — Day 03: Azure AI Services, Framework Selection, and Architectural Choice
    

    ### Four Daily Outputs

    | # | Output type | Location |
    |---|---|---|
    | 1 | Technical build | `LAB_OUTPUT/` |
    | 2 | Design defense memo | `DECISION_MEMOS/` |
    | 3 | Corporate process artifact | `PROCESS_ARTIFACTS/` |
    | 4 | Oral defense prep notes | `ORAL_DEFENSE/` |

    ### Rubric Weights (100 points total)

    | Dimension | Points |
    |---|---|
    | Correct Technical Selection | 30 |
| Rejected Alternatives Strength | 20 |
| Azure Implementation Realism | 20 |
| Cost Latency Quality Tradeoff | 15 |
| Oral Defense | 15 |

    Pass bar: **80 / 100**   Elite bar: **90 / 100**

    ### Oral Defense Prompts

    1. You chose one framework and rejected three. Explain the single strongest argument for each rejected alternative and why that argument was still insufficient.
2. If your framework choice turns out to be wrong at Day 10 scale, what is the migration blast radius in terms of state contracts and tool interfaces?
3. Who in the enterprise approves a framework change after Day 3, and what evidence of migration risk would they require before signing off?

    ### Artifact Scaffolds

    - `docs/curriculum/artifacts/day03/FRAMEWORK_DECISION_MATRIX.md`
- `docs/curriculum/artifacts/day03/MODEL_ROUTING_POLICY_V1.yaml`
- `docs/curriculum/artifacts/day03/RAG_BOUNDARY_DECISION.md`

    See `docs/curriculum/MENTAL_MODELS.md` for mental models reference.
    See `docs/curriculum/ASSESSOR_CALIBRATION.md` for scoring anchors.
    """)
    return


if __name__ == "__main__":
    app.run()
