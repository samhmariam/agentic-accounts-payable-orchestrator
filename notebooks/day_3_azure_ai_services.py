import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _bootstrap():
    import sys
    from pathlib import Path

    _root = Path(__file__).resolve().parents[1]
    for _p in [str(_root / "src"), str(_root / "notebooks")]:
        if _p not in sys.path:
            sys.path.insert(0, _p)
    return (Path,)


@app.cell
def _imports():
    import json
    import time
    from datetime import date

    import marimo as mo

    return date, json, mo, time


@app.cell
def _title(mo):
    mo.md("""
    # Day 3 — Retrieval Authority with Azure AI Search

    > **WAF Pillars covered:** Performance Efficiency · Reliability
    > **Estimated time:** 2.5 hours
    > **Primary source:** `docs/curriculum/trainee/DAY_03_TRAINEE.md`
    > **Canonical run path:** `scripts/run_day3_case.py`
    > **Expected artifact:** `build/day3/golden_thread_day3.json`
    > **Prerequisite:** Day 2 artifact strongly preferred. Fixture fallback is valid for practice, not for lineage-complete mastery.

    ---

    ## Learning Objectives

    1. Explain Retrieval-Augmented Generation (RAG) and its common failure modes.
    2. Distinguish between a retrieval system and an authority system.
    3. Describe Azure AI Search hybrid search and when semantic reranking helps.
    4. Explain why citations are mandatory for enterprise auditability.
    5. Describe AegisAP's multi-agent retrieval pattern and inspect the typed handoffs it produces.

    ---

    ## Microsoft Learn Anchors

    - [Hybrid search overview](https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview)
    - [Create a hybrid query](https://learn.microsoft.com/en-us/azure/search/hybrid-search-how-to-query)
    - [Semantic ranking overview](https://learn.microsoft.com/en-us/azure/search/semantic-ranking)
    - [Connect using Azure roles](https://learn.microsoft.com/en-us/azure/search/search-security-rbac)
    - [Keyless connection quickstart](https://learn.microsoft.com/en-us/azure/search/search-get-started-rbac)
    """)
    return


@app.cell
def _full_day_agenda(mo):
    from _shared.curriculum_scaffolds import render_full_day_agenda

    render_full_day_agenda(
        mo,
        day_label="Day 3 Azure AI service selection and framework choice",
        core_outcome="justify the Azure service stack and framework choices against the Day 2 architecture and authority boundaries",
    )
    return


@app.cell
def _lab_contract(mo):
    mo.callout(
        mo.md(
            """
    **Lab contract**

    Required inputs:
    - `build/day2/golden_thread_day2.json` or the Day 3 fixture invoice
    - Retrieval backend selection: `fixture`, `azure_search_live`, or `pgvector_fixture`
    - Azure AI Search access only if you want the live path

    Pass criteria:
    - Retrieved evidence is shown with citations and authority-adjusted ranking
    - A stale, lower-authority source does not outrank the current system of record
    - `build/day3/golden_thread_day3.json` is written and can hand off to Day 4

    **Lineage rule:** if Day 2 is missing, today is still valuable practice, but the
    resulting run should be treated as a fallback rehearsal rather than a
    lineage-complete progression through the curriculum.

    Canonical command:

    ```bash
    uv run python scripts/run_day3_case.py --retrieval-mode fixture
    ```
    """
        ),
        kind="info",
    )
    return


@app.cell
def _load_inputs(Path, json, mo):
    day2_path = Path(__file__).resolve().parents[1] / "build" / "day2" / "golden_thread_day2.json"
    fixture_path = Path(__file__).resolve().parents[1] / "fixtures" / "golden_thread" / "day3_invoice.json"
    vendor_master_path = (
        Path(__file__).resolve().parents[1] / "data" / "day3" / "structured" / "vendor_master.json"
    )

    invoice_data = None
    invoice_source = ""
    payload = None

    if day2_path.exists():
        payload = json.loads(day2_path.read_text(encoding="utf-8"))
        workflow_state = payload.get("workflow_state", payload)
        canonical_invoice = workflow_state.get("invoice", {})
        vendor_rows = json.loads(vendor_master_path.read_text(encoding="utf-8"))

        supplier_name = canonical_invoice.get("supplier_name") or workflow_state.get("vendor", {}).get(
            "vendor_name"
        )
        vendor_row = next(
            (
                row
                for row in vendor_rows
                if row.get("vendor_name", "").lower() == str(supplier_name or "").lower()
            ),
            {},
        )

        invoice_number = canonical_invoice.get("invoice_number") or workflow_state.get("invoice_id") or "INV-UNKNOWN"
        invoice_data = {
            "case_id": f"case_{str(invoice_number).lower().replace('-', '_')}",
            "invoice_id": invoice_number,
            "invoice_date": canonical_invoice.get("invoice_date"),
            "vendor_id": vendor_row.get("vendor_id") or "VEND-UNKNOWN",
            "vendor_name": supplier_name or "Unknown Vendor",
            "po_number": canonical_invoice.get("po_reference") or "PO-9001",
            "amount": float(canonical_invoice.get("gross_amount") or 0.0),
            "currency": canonical_invoice.get("currency") or "GBP",
            "bank_account_last4": vendor_row.get("bank_account_last4") or "",
        }
        invoice_source = "Loaded from `build/day2/golden_thread_day2.json`."
    elif fixture_path.exists():
        invoice_data = json.loads(fixture_path.read_text(encoding="utf-8"))
        invoice_source = (
            "Day 2 artifact not found, so the notebook fell back to "
            "`fixtures/golden_thread/day3_invoice.json`."
        )
    else:
        invoice_data = {
            "case_id": "CASE-MISSING",
            "invoice_id": "INV-MISSING",
            "invoice_date": "2026-03-01",
            "vendor_id": "VEND-001",
            "vendor_name": "Acme Office Supplies",
            "po_number": "PO-9001",
            "amount": 12500.0,
            "currency": "GBP",
            "bank_account_last4": "4421",
        }
        invoice_source = "Neither Day 2 artifact nor fixture invoice was found; using a safe in-notebook fallback."

    _fallback_used = "fell back" in invoice_source or "safe in-notebook fallback" in invoice_source
    _source_kind = "warn" if _fallback_used else "success"
    _lineage_note = (
        "This run is excellent for practising retrieval authority, but it does **not** prove "
        "the full Day 2 -> Day 3 evidence chain. Re-run after producing the Day 2 artifact "
        "before treating Day 3 as mastery-complete."
        if _fallback_used
        else "Lineage is intact: Day 3 is consuming Day 2 output as intended."
    )

    mo.vstack(
        [
            mo.md("## Active Invoice Context"),
            mo.callout(mo.md(invoice_source), kind=_source_kind),
            mo.callout(mo.md(_lineage_note), kind="warn" if _fallback_used else "info"),
            mo.hstack(
                [
                    mo.stat(label="Invoice ID", value=invoice_data["invoice_id"]),
                    mo.stat(label="Vendor", value=invoice_data["vendor_name"]),
                    mo.stat(label="PO Number", value=invoice_data.get("po_number", "—") or "—"),
                ]
            ),
        ]
    )
    return invoice_data, payload


@app.cell
def _rag_header(mo):
    mo.md("""
    ## 1. Retrieval-Augmented Generation
    """)
    return


@app.cell
def _rag_body(mo):
    mo.md("""
    RAG improves an LLM by retrieving external evidence at inference time and grounding
    the answer in that evidence. In AegisAP, the LLM must not treat training knowledge as
    authoritative policy.

    ```
    User question
        │
        ▼
    [ Retrieval ]  -> candidate evidence
        │
        ▼
    [ Authority policy ]  -> allowed evidence ordering
        │
        ▼
    [ Specialist agents ]  -> typed findings + citations
        │
        ▼
    Decision recommendation
    ```

    ### Common failure modes

    | Failure mode | What goes wrong | Day 3 mitigation |
    |---|---|---|
    | Context stuffing | Too many chunks, weak grounding | Keep top results small and inspect ranking |
    | Hallucinated citations | Model names a source it never retrieved | Persist real chunk IDs and evidence IDs |
    | Stale retrieval | Old evidence looks relevant | Apply recency weighting and inspect event dates |
    | Authority confusion | High relevance is mistaken for truth | Rank by source authority after retrieval |
    """)
    return


@app.cell
def _authority_header(mo):
    mo.md("""
    ## 2. Retrieval vs Authority
    """)
    return


@app.cell
def _authority_body(mo):
    mo.md("""
    Retrieval answers **"what looks relevant?"**. Authority answers **"what are we allowed
    to trust?"**. Day 3 exists because those are not the same question.

    | Property | Retrieval system | Authority system |
    |---|---|---|
    | Primary signal | BM25, vectors, semantic reranking | Source tier, effective date, explicit policy |
    | Typical infrastructure | Azure AI Search | Local workflow policy + typed evidence models |
    | Failure when misused | Missing useful context | Letting stale or unofficial sources drive decisions |
    | Correct enterprise boundary | Candidate generation | Truth and auditability enforcement |

    **AegisAP rule:** Azure AI Search finds candidate evidence. The workflow code decides whether
    that evidence is authoritative enough to influence payment decisions.
    """)
    return


@app.cell
def _search_header(mo):
    mo.md("""
    ## 3. Azure AI Search Best-Practice Boundary
    """)
    return


@app.cell
def _search_body(mo):
    mo.md("""
    Azure AI Search is the Day 3 retrieval engine for unstructured evidence. Microsoft Learn
    guidance supports the same choices this repo makes:

    - Use **hybrid search** when you want both exact matches and semantic similarity.
    - Add **semantic reranking** only when the latency and billing budget allow it.
    - Use **Microsoft Entra ID / RBAC** for application access; avoid admin keys in app code.
    - Keep **authority policy outside the search service**. Search relevance is not business truth.

    ### Managed identity / keyless query pattern

    ```python
    from azure.identity import DefaultAzureCredential
    from azure.search.documents import SearchClient
    import os

    credential = DefaultAzureCredential()

    client = SearchClient(
        endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
        index_name=os.environ["AZURE_SEARCH_DAY3_INDEX"],
        credential=credential,
    )

    results = client.search(
        search_text="Acme bank change approved account 4421",
        query_type="semantic",
        semantic_query="Acme bank change approved account 4421",
        semantic_configuration_name="day3-semantic-config",
        top=5,
        select=[
            "id",
            "doc_id",
            "title",
            "content",
            "source_name",
            "source_type",
            "authority_tier",
            "event_time",
            "vendor_id",
            "bank_account_last4",
        ],
    )
    ```

    ### Operational notes from Microsoft Learn

    - `Search Index Data Reader` is the least-privilege role for query-only app paths.
    - Semantic reranking reranks an initial result set; it does not replace your authority logic.
    - Semantic captions can reduce grounding token load, but they still come from retrieved content.
    - Do not add explicit sorting when you want relevance-driven semantic results.
    """)
    return


@app.cell
def _rrf_header(mo):
    mo.md("""
    ### Why Hybrid Search Helps
    """)
    return


@app.cell
def _rrf_body(mo):
    mo.md(r"""
    Hybrid search merges keyword and vector rankings with Reciprocal Rank Fusion (RRF):

    $$
    \text{RRF}(d) = \sum_{r \in \{\text{keyword, vector}\}} \frac{1}{k + \text{rank}_r(d)}
    $$

    RRF is useful because it gives us a stronger **candidate set**. It still does **not**
    answer the authority question. Day 3 adds a second scoring layer after retrieval:

    $$
    \text{final\_score} =
    \text{retrieval\_score} \times
    \text{authority\_weight} \times
    \text{recency\_weight} +
    \text{exact\_match\_bonus}
    $$
    """)
    return


@app.cell
def _multi_agent_header(mo):
    mo.md("""
    ## 4. Multi-Agent Retrieval Pattern
    """)
    return


@app.cell
def _multi_agent_body(mo):
    mo.md("""
    Day 3 does not use one giant free-form agent. It uses specialist retrieval and typed handoffs.

    ```
    Intake router
        │
        ├── retrieve_vendor_context
        │     ├── structured vendor master lookup
        │     └── Azure AI Search or fixture search for unstructured docs
        │
        ├── vendor_risk_verifier
        │     └── returns typed vendor-risk finding
        │
        ├── retrieve_po_context
        │     └── structured PO lookup
        │
        ├── po_match_agent
        │     └── returns typed PO-match finding
        │
        └── decision_synthesizer
              └── merges specialist findings into a recommendation
    ```

    This structure is deliberate:

    - Retrieval stays separate from judgment.
    - Each specialist can be tested independently.
    - The final decision retains explicit evidence IDs and policy notes.
    """)
    return


@app.cell
def _authority_sim_header(mo):
    mo.md("""
    ## 5. Authority Ranking Simulator
    """)
    return


@app.cell
def _authority_sim_inputs(mo):
    stale_email_score = mo.ui.slider(
        start=40,
        stop=100,
        step=5,
        value=95,
        label="Stale onboarding email retrieval score (%)",
    )
    approved_email_score = mo.ui.slider(
        start=40,
        stop=100,
        step=5,
        value=80,
        label="Approved bank-change email retrieval score (%)",
    )
    policy_score = mo.ui.slider(
        start=40,
        stop=100,
        step=5,
        value=65,
        label="AP policy retrieval score (%)",
    )

    mo.vstack(
        [
            mo.md(
                "These sliders only change **retrieval relevance**. The simulator still applies the "
                "repo's Day 3 authority policy afterwards."
            ),
            stale_email_score,
            approved_email_score,
            policy_score,
        ]
    )
    return approved_email_score, policy_score, stale_email_score


@app.cell
def _authority_sim_output(
    Path,
    approved_email_score,
    date,
    mo,
    policy_score,
    stale_email_score,
):
    from aegisap.day3.export import evidence_to_table
    from aegisap.day3.retrieval.authority_policy import load_authority_policy
    from aegisap.day3.retrieval.azure_ai_search_adapter import evidence_item_from_markdown
    from aegisap.day3.retrieval.interfaces import parse_front_matter_markdown
    from aegisap.day3.retrieval.ranker import apply_authority_ranking
    from aegisap.day3.retrieval.structured_vendor_lookup import StructuredVendorLookup

    repo_root = Path(__file__).resolve().parents[1]
    policy = load_authority_policy(repo_root / "src" / "aegisap" / "day3" / "policies" / "source_authority_rules.yaml")

    vendor_master = StructuredVendorLookup().search(
        vendor_id="VEND-001",
        vendor_name="Acme Office Supplies",
    )

    stale_email = evidence_item_from_markdown(
        parse_front_matter_markdown(repo_root / "data" / "day3" / "unstructured" / "supplier_onboarding_old_email.md"),
        retrieval_score=stale_email_score.value / 100,
        backend="simulated_hybrid",
    )
    approved_email = evidence_item_from_markdown(
        parse_front_matter_markdown(repo_root / "data" / "day3" / "unstructured" / "bank_change_approval_email.md"),
        retrieval_score=approved_email_score.value / 100,
        backend="simulated_hybrid",
    )
    policy_doc = evidence_item_from_markdown(
        parse_front_matter_markdown(repo_root / "data" / "day3" / "unstructured" / "ap_policy_bank_change.md"),
        retrieval_score=policy_score.value / 100,
        backend="simulated_hybrid",
    )

    ranked = apply_authority_ranking(
        vendor_master + [stale_email, approved_email, policy_doc],
        policy=policy,
        query_terms={
            "vendor_id": "VEND-001",
            "vendor_name": "Acme Office Supplies",
            "bank_account_last4": "4421",
        },
        today=date.fromisoformat("2026-03-01"),
        recency_mode="mutable_fact",
    )

    rows = evidence_to_table(ranked)
    winner = rows[0]

    mo.vstack(
        [
            mo.ui.table(rows, selection=None),
            mo.callout(
                mo.md(
                    f"""
                **Top-ranked evidence:** `{winner["evidence_id"]}`

                This is the behavior Day 3 is designed to enforce: even when the stale email
                retrieves strongly, the current authoritative vendor record should still win.
                """
                ),
                kind="success",
            ),
        ]
    )
    return


@app.cell
def _workflow_header(mo):
    mo.md("""
    ## 6. Run the Canonical Day 3 Workflow
    """)
    return


@app.cell
def _workflow_mode(mo):
    retrieval_mode = mo.ui.dropdown(
        options=["fixture", "azure_search_live", "pgvector_fixture"],
        value="fixture",
        label="Retrieval backend",
    )
    retrieval_mode
    return (retrieval_mode,)


@app.cell
def _workflow_run(invoice_data, mo, retrieval_mode, time):
    from aegisap.training.labs import run_day3_case_artifact

    t0 = time.monotonic()
    try:
        artifact_path, payload = run_day3_case_artifact(
            invoice=invoice_data,
            retrieval_mode=retrieval_mode.value,
        )
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        error = None
    except Exception as exc:  # noqa: BLE001
        artifact_path = None
        payload = None
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        error = str(exc)

    if error:
        mo.callout(
            mo.md(
                f"""
            **Workflow run failed:** `{error}`

            If you selected `azure_search_live`, confirm:
            - `AZURE_SEARCH_ENDPOINT` is set
            - `AZURE_SEARCH_DAY3_INDEX` is set
            - the calling identity has `Search Index Data Reader`
            """
            ),
            kind="danger",
        )
    else:
        decision = payload["workflow_state"]["agent_findings"]["decision"]
        mo.vstack(
            [
                mo.hstack(
                    [
                        mo.stat(label="Latency", value=f"{elapsed_ms} ms"),
                        mo.stat(label="Recommendation", value=decision["recommendation"]),
                        mo.stat(label="Next step", value=decision["next_step"]),
                    ]
                ),
                mo.callout(
                    mo.md(
                        f"Artifact written to `{artifact_path.relative_to(artifact_path.parents[2])}`"
                    ),
                    kind="success",
                ),
            ]
        )
    return (payload,)


@app.cell
def _evidence_view(mo, payload):
    from aegisap.day3.export import evidence_to_table

    mo.stop(payload is None, mo.md("No workflow payload to display."))

    all_items = []
    retrieval_context = payload["workflow_state"]["retrieval_context"]
    for bucket_name in ("vendor", "policy", "po"):
        all_items.extend(retrieval_context.get(bucket_name, []))

    rows = evidence_to_table(all_items)
    mo.vstack(
        [
            mo.md("### Ranked Evidence"),
            mo.ui.table(rows, selection=None),
        ]
    )
    return


@app.cell
def _findings_view(mo, payload):
    mo.stop(payload is None, mo.md("No workflow payload to display."))

    workflow_state = payload["workflow_state"]
    mo.vstack(
        [
            mo.md("### Typed Specialist Findings"),
            mo.tree(workflow_state["agent_findings"]),
            mo.md("### Evaluation Scores"),
            mo.tree(workflow_state["eval_scores"]),
        ]
    )
    return


@app.cell
def _handoff_header(mo):
    mo.md("""
    ## 7. Why Citations Matter
    """)
    return


@app.cell
def _handoff_body(mo, payload):
    mo.stop(payload is None, mo.md("Run the workflow first to inspect handoff evidence."))

    decision = payload["workflow_state"]["agent_findings"]["decision"]
    evidence_ids = decision.get("evidence_ids", [])
    notes = decision.get("policy_notes", [])

    mo.callout(
        mo.md(
            f"""
        **Decision evidence IDs:** `{evidence_ids}`

        **Policy notes:**
        {chr(10).join(f"- {note}" for note in notes)}

        In this repo, a recommendation is only defensible if we can trace it back to specific
        evidence IDs and their source metadata. That is the difference between a plausible answer
        and an auditable one.
        """
        ),
        kind="info",
    )
    return


@app.cell
def _code_contract_header(mo):
    mo.md("""
    ## 8. Code-Level Day 3 Contract
    """)
    return


@app.cell
def _code_contract_body(mo):
    mo.md("""
    The repo's implementation boundary is intentionally explicit:

    - [graph.py](/workspaces/agentic-accounts-payable-orchestrator/src/aegisap/day3/graph.py) runs retrieval, specialist verification, synthesis, and scoring.
    - [ranker.py](/workspaces/agentic-accounts-payable-orchestrator/src/aegisap/day3/retrieval/ranker.py) applies authority weights, recency decay, and exact-match bonus.
    - [authority_policy.py](/workspaces/agentic-accounts-payable-orchestrator/src/aegisap/day3/retrieval/authority_policy.py) defines the policy knobs.
    - [run_day3_case.py](/workspaces/agentic-accounts-payable-orchestrator/scripts/run_day3_case.py) is the canonical script path.
    - [DAY_03_TRAINEE.md](/workspaces/agentic-accounts-payable-orchestrator/docs/curriculum/trainee/DAY_03_TRAINEE.md) defines the learning contract and pass criteria.

    The notebook should explain this contract, not replace it with a separate mini-curriculum.
    """)
    return


@app.cell
def _ms_learn_notes(mo):
    mo.md("""
    ## 9. Microsoft Learn Notes Applied Here

    | Microsoft Learn guidance | How this notebook applies it |
    |---|---|
    | Hybrid queries are a strong default for relevance | Day 3 uses Azure AI Search as a candidate generator for unstructured evidence |
    | Semantic ranker improves top-result quality but adds cost/latency | The notebook discusses semantic mode as optional, not mandatory |
    | Use Azure roles for query access | Examples use `DefaultAzureCredential` and least-privilege reader roles |
    | Semantic ranking reranks existing results, it does not define truth | Day 3 keeps authority ranking in local workflow code |
    """)
    return


@app.cell
def _exercises_header(mo):
    mo.md("""
    ## Exercises
    """)
    return


@app.cell
def _exercise_1(mo):
    mo.accordion(
        {
            "Exercise 1 — Highest score vs highest authority": mo.vstack(
                [
                    mo.md(
                        """
                **Task:** The stale onboarding email retrieves with a higher raw search score than the
                current vendor master. Which source should the workflow trust, and why?
                """
                    ),
                    mo.accordion(
                        {
                            "Show solution": mo.md(
                                """
                Trust the vendor master. Retrieval score only tells us which text looked relevant to the query.
                The vendor master is Tier 1 system-of-record evidence, is more recent, and matches the approved
                bank account. The email remains useful historical context but must not override the current truth.
                """
                            )
                        }
                    ),
                ]
            )
        }
    )
    return


@app.cell
def _exercise_2(mo):
    mo.accordion(
        {
            "Exercise 2 — Azure AI Search RBAC": mo.vstack(
                [
                    mo.md(
                        """
                **Task:** Write the least-privilege Python code to query Azure AI Search for Day 3.
                Include the correct auth pattern and the RBAC role required.
                """
                    ),
                    mo.accordion(
                        {
                            "Show solution": mo.md(
                                """
                ```python
                from azure.identity import DefaultAzureCredential
                from azure.search.documents import SearchClient
                import os

                client = SearchClient(
                    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
                    index_name=os.environ["AZURE_SEARCH_DAY3_INDEX"],
                    credential=DefaultAzureCredential(),
                )

                results = client.search(
                    search_text="Acme bank change",
                    top=5,
                )
                ```

                Required role: `Search Index Data Reader`.
                Do not use admin keys in application code for this path.
                """
                            )
                        }
                    ),
                ]
            )
        }
    )
    return


@app.cell
def _exercise_3(mo):
    mo.accordion(
        {
            "Exercise 3 — Canonical rerun command": mo.vstack(
                [
                    mo.md(
                        """
                **Task:** What exact command should you run to rebuild the Day 3 artifact in fixture mode,
                and which citation would you inspect first if a reviewer said the wrong bank-change evidence won?
                """
                    ),
                    mo.accordion(
                        {
                            "Show solution": mo.md(
                                """
                ```bash
                uv run python scripts/run_day3_case.py --retrieval-mode fixture
                ```

                First inspect the stale onboarding citation, `doc-onboarding-old-bank`, because the Day 3 adversarial
                case is specifically about proving that the stale Tier 3 email does **not** outrank the current
                authoritative vendor record.
                """
                            )
                        }
                    ),
                ]
            )
        }
    )
    return


@app.cell
def _exercise_4(mo):
    mo.accordion(
        {
            "Exercise 4 — Explain the boundary": mo.vstack(
                [
                    mo.md(
                        """
                **Task:** In one paragraph, explain the boundary between Azure AI Search and the local
                Day 3 authority policy.
                """
                    ),
                    mo.accordion(
                        {
                            "Show solution": mo.md(
                                """
                Azure AI Search is responsible for candidate retrieval: it finds documents that look relevant
                using keyword, vector, and optional semantic reranking signals. The Day 3 workflow is responsible
                for deciding whether those documents are trustworthy enough to influence a payment decision. That
                second step depends on source tier, recency, and exact-match policy, not just search relevance.
                                """
                            )
                        }
                    ),
                ]
            )
        }
    )
    return


@app.cell
def _summary(mo):
    mo.md("""
    ## Day 3 Summary Checklist

    - [ ] Explain the difference between retrieval and authority
    - [ ] Describe at least two common RAG failure modes
    - [ ] Explain why Azure AI Search hybrid retrieval helps but does not define truth
    - [ ] Configure a `SearchClient` with `DefaultAzureCredential`
    - [ ] Name the least-privilege query role: `Search Index Data Reader`
    - [ ] Show why the current vendor master outranks the stale onboarding email
    - [ ] Inspect typed specialist findings and decision evidence IDs
    - [ ] Write `build/day3/golden_thread_day3.json`
    - [ ] State the canonical rerun command for fixture mode
    """)
    return


@app.cell
def _forward(mo):
    mo.callout(
        mo.md(
            """
    **Tomorrow — Day 4: Single-Agent Planning on Top of Trusted Evidence**

    Day 4 assumes Day 3 already separated candidate retrieval from authority. The planner should only
    reason over evidence that Day 3 allowed into the decision path.
    """
        ),
        kind="success",
    )
    return


if __name__ == "__main__":
    app.run()
