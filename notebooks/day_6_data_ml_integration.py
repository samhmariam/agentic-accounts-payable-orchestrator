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
    # Day 6 — Data & ML Integration: Azure Data Factory, Cosmos DB, and MLflow

    > **WAF Pillars covered:** Reliability · Operational Excellence · Cost Optimization  
    > **Estimated time:** 2.5 hours  
    > **Sources:** `docs/curriculum/trainee/DAY_02_TRAINEE.md` (data flow),  
    > `docs/curriculum/trainee/DAY_03_TRAINEE.md` (document ingestion, data authority)  
    > **Prerequisites:** Day 5 complete; AegisAP LangGraph workflow is running.

    ---

    ## Learning Objectives

    1. Design an invoice ingestion pipeline with Azure Data Factory (ADF) and explain the
       landing → curated → processed zone pattern.
    2. Use Azure Cosmos DB as a vendor master and invoice status store with Managed Identity.
    3. Integrate MLflow (Azure ML-hosted) to track evaluation runs, model versions, and gate thresholds.
    4. Implement schema evolution for the AegisAP data stores without breaking the workflow.
    5. Explain the data authority pyramid and when to use each storage tier.

    ---

    ## Where Day 6 Sits in the Full Arc

    ```
    ... Day 5 ──►[Day 6]──► Day 7 ──► Day 8 ──► ...
         Multi-  DATA &     Testing  CI/CD &
         Agent   ML         & Evals  IaC
    ```

    Day 6 connects the agentic workflow to the **data plane** — the sources of truth
    that agents read and write during invoice processing.
    """)
    return


@app.cell
def _full_day_agenda(mo):
    from _shared.curriculum_scaffolds import render_full_day_agenda

    render_full_day_agenda(
        mo,
        day_label="Day 6 data authority and ML integration",
        core_outcome="reason clearly about data authority, source-of-truth conflicts, and how ML outputs become governed recommendations",
    )
    return

@app.cell
def _notebook_guide(mo):
    from _shared.lab_guide import render_notebook_learning_context

    render_notebook_learning_context(
        mo,
        purpose='Connect the workflow to governed data and ML systems while preserving source-of-truth boundaries.',
        prerequisites=['Day 5 orchestration concepts complete.', 'Understand the earlier authority model from Days 2-5.', 'No live Azure data services are required to follow the notebook.'],
        resources=['`notebooks/day_6_data_ml_integration.py`', '`docs/curriculum/artifacts/day06/` for data authority and conflict handling', '`build/day6/` for the audit artifact', 'Conceptual references to ADF, Cosmos DB, Redis, PostgreSQL checkpoints, and MLflow'],
        setup_sequence=['Run the notebook locally and keep Day 5 state and durability in mind.', 'Treat each storage tier as a responsibility boundary, not just a technology choice.', 'Open the Day 6 artifact references only when you want the reusable template view.'],
        run_steps=['Work through the data authority pyramid before the specific service sections.', 'Use the schema evolution and MLflow sections to understand how governance extends past raw storage.', 'Run the artifact-writing cell that produces `build/day6/data_integration_audit.json`.', 'Finish with the checklist so the authority tiers are clear before Day 7.'],
        output_interpretation=['The main completion signal is `build/day6/data_integration_audit.json` with `gate_passed = true`.', 'Interpret the notebook outputs as evidence about who may write where, not just which service is faster.', 'A good Day 6 result makes Day 7 guardrails feel enforceable because the data boundaries are already explicit.'],
        troubleshooting=['If the services start blurring together, return to the authority pyramid and ask which tier owns truth.', 'If MLflow feels separate from the rest of the day, treat it as governed evidence about model behaviour rather than a standalone tool.', 'If the artifact is missing, rerun the final Day 6 artifact cell.'],
        outside_references=['Long-form theory: `docs/curriculum/trainee/DAY_06_TRAINEE.md` plus the Day 2 and Day 3 trainee readings already cited in the notebook', 'Trainer notes: `docs/curriculum/trainer/DAY_06_TRAINER.md`', 'Reusable references: `docs/curriculum/artifacts/day06/`'],
    )
    return


# ---------------------------------------------------------------------------
# Section 1 – Data Authority Pyramid
# ---------------------------------------------------------------------------
@app.cell
def _s1_header(mo):
    mo.md("## 1. The Data Authority Pyramid")
    return


@app.cell
def _s1_body(mo):
    mo.md("""
    Not all data sources are equal. AegisAP uses a **data authority pyramid** to decide
    which source wins when there is a conflict.

    ```
                      ┌───────────────────────┐
                      │   TIER 1: AUTHORITATIVE│   ← Always trusted, always wins
                      │   Azure SQL / PostgreSQL│
                      │   (double-entry ledger) │
                      └───────────────────────┘
                    ┌─────────────────────────────┐
                    │   TIER 2: CANONICAL RECORD  │  ← Derived from authoritative sources
                    │   Cosmos DB vendor master   │
                    │   Azure AI Search index     │
                    └─────────────────────────────┘
                  ┌───────────────────────────────────┐
                  │   TIER 3: OPERATIONAL STORE       │ ← Fast reads, eventual consistency
                  │   Redis cache (vendor lookups)     │
                  │   LangGraph WorkflowState (live)  │
                  └───────────────────────────────────┘
                ┌─────────────────────────────────────────┐
                │   TIER 4: DERIVED / ANALYTICAL          │← Read-only output
                │   Azure Data Factory silver/gold tables  │
                │   MLflow experiment metrics              │
                └─────────────────────────────────────────┘
    ```

    ### Authority rules

    1. **Never write to a higher tier from a lower tier.** The LangGraph state machine
       (Tier 3) writes to the PostgreSQL ledger (Tier 1) via an explicit commit step —
       it never bypasses the ledger by writing to Cosmos DB directly.
    2. **Conflict resolution:** If Tier 3 (operational) and Tier 1 (authoritative) disagree,
       Tier 1 wins. The workflow is re-hydrated from Tier 1 data.
    3. **Retrievals are advisory.** Chunks retrieved from Azure AI Search (Tier 2) inform
       decisions but do not override the canonical invoice data validated by PostgreSQL.
    """)
    return


@app.cell
def _authority_tier_picker(mo):
    tier = mo.ui.radio(
        options=["Tier 1: Authoritative", "Tier 2: Canonical",
                 "Tier 3: Operational", "Tier 4: Analytical"],
        value="Tier 1: Authoritative",
        label="Explore a data authority tier:",
    )
    tier
    return (tier,)


@app.cell
def _authority_detail(mo, tier):
    details = {
        "Tier 1: Authoritative": {
            "store": "Azure Database for PostgreSQL (Flexible Server)",
            "tables": "`invoices`, `execution_traces`, `approval_requests`, `canonical_invoices`",
            "auth": "Managed Identity + Entra token (no password in connection string)",
            "consistency": "Strong (ACID transactions, serial isolation for ledger writes)",
            "backup": "Azure Backup, point-in-time restore, geo-redundant",
            "who_writes": "AegisAP application only, via `execute_node` and `commit_step`",
            "azure_role": "`Database User` granted via Entra group, not direct password",
        },
        "Tier 2: Canonical": {
            "store": "Azure Cosmos DB (NoSQL API) for vendor master; Azure AI Search for documents",
            "tables": "Cosmos: `vendors` container; Search: `vendor-policies`, `compliance-rules` indices",
            "auth": "Managed Identity for both (no connection-string keys)",
            "consistency": "Cosmos: Session consistency; Search: eventual (index refresh on schedule)",
            "backup": "Cosmos: continuous backup (PITR); Search: re-index from Blob Storage",
            "who_writes": "Vendor onboarding pipeline (ADF) for Cosmos; indexer pipeline for Search",
            "azure_role": "Cosmos: `Cosmos DB Built-in Data Contributor`; Search: `Search Index Data Contributor`",
        },
        "Tier 3: Operational": {
            "store": "Redis Cache (Azure Cache for Redis) + LangGraph WorkflowState in PostgreSQL checkpoints",
            "tables": "Redis: `vendor_cache:{vendor_id}` keys (TTL 15 min); Checkpoints: as per Day 5",
            "auth": "Redis: Entra-managed key (`REDIS_ACCESS_KEY` via Key Vault); Checkpoints: same as Tier 1",
            "consistency": "Redis: Eventually consistent with Cosmos Tier 2 (refreshed on cache miss); Checkpoints: strong",
            "backup": "Redis: no explicit backup (rebuilt from Tier 2 on miss); Checkpoints: in Tier 1 PostgreSQL",
            "who_writes": "Any agent node can read/write cache; checkpoint written by LangGraph only",
            "azure_role": "Redis: `Redis Cache Contributor` not needed — Key Vault secret rotation handles it",
        },
        "Tier 4: Analytical": {
            "store": "Azure Data Lake Storage Gen2 (silver/gold tables via ADF); Azure ML MLflow",
            "tables": "ADF: `bronze/` landing, `silver/` curated, `gold/` aggregated parquet; MLflow: runs, metrics, artifacts",
            "auth": "ADF: Managed Identity on the Integration Runtime; MLflow: Azure ML workspace key + OIDC",
            "consistency": "Eventual — ADF pipelines run hourly; MLflow is append-only",
            "backup": "ADLS: geo-redundant; MLflow: backed by Azure ML managed storage",
            "who_writes": "ADF pipelines only (read-only to agents); evaluation scripts for MLflow",
            "azure_role": "ADLS: `Storage Blob Data Contributor` on silver/gold containers",
        },
    }

    d = details[tier.value]
    mo.callout(
        mo.md(f"""
**{tier.value}**

| Property | Details |
|---|---|
| **Azure service** | {d['store']} |
| **Key tables/containers** | {d['tables']} |
| **Authentication** | {d['auth']} |
| **Consistency model** | {d['consistency']} |
| **Backup strategy** | {d['backup']} |
| **Who writes** | {d['who_writes']} |
| **Required RBAC role** | {d['azure_role']} |
        """),
        kind="info",
    )
    return d, details


# ---------------------------------------------------------------------------
# Section 2 – Azure Data Factory Ingestion Pipeline
# ---------------------------------------------------------------------------
@app.cell
def _s2_header(mo):
    mo.md("## 2. Azure Data Factory: Invoice Ingestion Pipeline")
    return


@app.cell
def _s2_body(mo):
    mo.md("""
    **Azure Data Factory (ADF)** orchestrates the movement and transformation of invoice
    documents from source systems to the AegisAP processing queue.

    ### Landing → Curated → Processed zone pattern (Medallion architecture)

    ```
    [Source: ERP / email / SFTP]
           │
           ▼
    ┌──────────────────┐
    │  BRONZE (landing) │  Raw files: PDFs, XMLs, CSVs exactly as received
    │  ADLS Gen2        │  No transformation; immutable; retention 90 days
    └──────────────────┘
           │ ADF pipeline: extract → parse → validate
           ▼
    ┌──────────────────────┐
    │  SILVER (curated)     │  Parsed JSON invoice records, schema-validated
    │  ADLS Gen2 + Parquet  │  PII fields tokenised; duplicates removed
    └──────────────────────┘
           │ ADF pipeline: aggregate → join vendor master → score
           ▼
    ┌───────────────────────────┐
    │  GOLD (processed)          │  Enriched invoice records ready for LangGraph
    │  Azure Cosmos DB + Search  │  Joined with vendor master; RRF index populated
    └───────────────────────────┘
           │ ADF trigger → Azure Container Apps Job
           ▼
    [ AegisAP LangGraph workflow invoked per invoice ]
    ```

    ### Key ADF pipeline design decisions

    ```json
    {
      "pipeline": "invoice_ingestion",
      "triggers": [
        {"type": "TumblingWindow", "interval": 1, "unit": "Hour"},
        {"type": "BlobEvent",  "blobPath": "bronze/incoming/", "events": ["Microsoft.Storage.BlobCreated"]}
      ],
      "activities": [
        {"name": "CopyFromSource",       "type": "Copy"},
        {"name": "ParseAndValidateInvoice","type": "DataFlow"},
        {"name": "TokenisePII",           "type": "AzureFunctionActivity"},
        {"name": "UpsertToSilver",        "type": "Copy", "sink": {"type": "ParquetSink"}},
        {"name": "EnrichFromVendorMaster","type": "DataFlow"},
        {"name": "WriteToGoldCosmos",     "type": "CosmosDbSqlApiSink"},
        {"name": "TriggerWorkflow",       "type": "WebActivity", "url": "https://api/workflows/invoke"}
      ],
      "identity": "system_assigned_managed_identity"
    }
    ```

    > **ADF uses system-assigned Managed Identity.** No connection strings, no storage
    > account keys. The Integration Runtime identity is granted `Storage Blob Data Contributor`
    > on the landing zone and `Cosmos DB Built-in Data Contributor` on the gold container.
    """)
    return


@app.cell
def _adf_zone_chart(mo):
    try:
        import plotly.graph_objects as go

        zones = ["Bronze (landing)", "Silver (curated)",
                 "Gold (processed)", "Workflow invoked"]
        volumes = [100, 82, 79, 79]   # % of documents that reach each stage
        latency = [0, 3, 8, 15]       # minutes from receipt to each stage

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=zones, y=volumes, name="Documents reaching stage (%)",
            marker_color=["#CD7F32", "#C0C0C0", "#FFD700", "#4A90D9"],
        ))
        for i, (v, l) in enumerate(zip(volumes, latency)):
            fig.add_annotation(x=i, y=v + 1, text=f"~{l}min", showarrow=False,
                               font=dict(size=10))

        fig.update_layout(
            title="ADF Medallion Pipeline — Document Flow & Latency",
            yaxis_title="% documents reaching stage", yaxis_range=[0, 115],
            height=320, margin=dict(t=50, b=40),
        )
        mo.ui.plotly(fig)
    except ImportError:
        mo.callout(
            mo.md("Install `plotly` to see the ADF pipeline chart."), kind="warn")
    return


# ---------------------------------------------------------------------------
# Section 3 – Cosmos DB Vendor Master
# ---------------------------------------------------------------------------
@app.cell
def _s3_header(mo):
    mo.md("## 3. Cosmos DB Vendor Master")
    return


@app.cell
def _s3_body(mo):
    mo.md("""
    **Azure Cosmos DB** (NoSQL API) stores the vendor master — the authoritative record
    of every vendor: their details, payment terms, EDD status, and bank accounts.

    ### Document schema

    ```json
    {
      "id": "ACME-001",
      "vendor_id": "ACME-001",
      "name": "Acme Office Supplies Ltd",
      "country_code": "GB",
      "payment_terms_days": 30,
      "early_payment_discount_pct": 2.0,
      "edd_required": false,
      "approved_bank_accounts": [
        {
          "account_ref": "ACME-BACS-001",
          "sort_code": "****",
          "account_number": "****",
          "currency": "GBP",
          "verified_date": "2023-11-01"
        }
      ],
      "po_required": true,
      "preferred_currency": "GBP",
      "_etag": "\"00001a00-0000-0100-0000-65bbf0000\"",
      "_ts": 1706745856
    }
    ```

    ### Vendor lookup with Managed Identity

    ```python
    from azure.cosmos import CosmosClient
    from azure.identity import DefaultAzureCredential
    import os

    credential = DefaultAzureCredential()
    client = CosmosClient(
        url=os.environ["COSMOS_ENDPOINT"],
        credential=credential,          # ← Managed Identity token
    )
    container = client.get_database_client("aegisap").get_container_client("vendors")

    # Point read — cheapest Cosmos DB operation (1 RU)
    vendor = container.read_item(item="ACME-001", partition_key="ACME-001")
    ```

    > **Use point reads, not queries, for vendor lookups.**  
    > A point read (`read_item`) costs 1 RU. A SQL query (`SELECT * WHERE vendor_id = '...'`)
    > costs 4–10 RU for the same document. At 10,000 invoices/day, this is a 9× RU saving.

    ### Schema evolution

    Cosmos DB is schemaless — you can add new fields without a migration.
    However, the application code must handle **forwards compatibility**:

    ```python
    # WRONG — will crash on vendors added before edd_required field existed
    edd = vendor["edd_required"]

    # CORRECT — use .get() with a safe default
    edd = vendor.get("edd_required", False)
    ```

    New mandatory fields require a backfill pipeline (ADF) to add defaults to existing documents.
    """)
    return


# ---------------------------------------------------------------------------
# Section 4 – MLflow for Evaluation Tracking
# ---------------------------------------------------------------------------
@app.cell
def _s4_header(mo):
    mo.md("## 4. MLflow: Evaluation Run Tracking")
    return


@app.cell
def _s4_body(mo):
    mo.md("""
    **MLflow** (hosted on Azure Machine Learning) tracks every AegisAP evaluation run:
    model versions, metric scores, dataset versions, and gate thresholds.

    ### Why MLflow in a workflow system?

    AegisAP evaluation is not training an ML model, but it shares the same concerns:
    - **Reproducibility**: run the same eval on the same dataset and get the same score
    - **Regression detection**: score today vs. score last week → is the system getting worse?
    - **Artefact lineage**: which model version produced which eval result?
    - **Gate enforcement**: CI pipeline queries MLflow to check if the latest run passed all gates

    ### MLflow integration

    ```python
    import mlflow, os
    from datetime import datetime

    mlflow.set_tracking_uri(os.environ["AZUREML_MLFLOW_URI"])
    mlflow.set_experiment("aegisap-invoice-eval")

    with mlflow.start_run(run_name=f"eval_{datetime.utcnow():%Y%m%d_%H%M%S}") as run:
        # Log parameters (what was being evaluated)
        mlflow.log_params({
            "extraction_model": "gpt-4o-mini-2024-07-18",
            "planning_model":   "gpt-4o-2024-11-20",
            "eval_dataset_hash": dataset_hash,
            "eval_cases_count": 47,
        })

        # Run evaluation suite
        results = run_eval_suite(dataset)

        # Log metrics (the scores)
        mlflow.log_metrics({
            "extraction_accuracy":       results["extraction_accuracy"],
            "escalation_recall":         results["escalation_recall"],
            "auto_approve_precision":    results["auto_approve_precision"],
            "policy_compliance_rate":    results["policy_compliance_rate"],
            "p95_latency_s":             results["p95_latency_s"],
        })

        # Log artefacts (sample outputs for review)
        mlflow.log_artifact("evals/results_latest.jsonl")

        # Evaluate against gates
        passed = (
            results["escalation_recall"] >= 1.0 and
            results["extraction_accuracy"] >= 0.95 and
            results["auto_approve_precision"] >= 0.90
        )
        mlflow.set_tag("gate_passed", str(passed).lower())
    ```

    > **`escalation_recall` MUST be ≥ 1.0.** Every invoice that should escalate to
    > a human must escalate. A false negative (system auto-approves when it should escalate)
    > is a financial control failure. This is a hard gate — no deployment if recall < 1.0.
    """)
    return


@app.cell
def _eval_chart(mo):
    mo.md("### Evaluation Metric Trend — Simulated Runs")
    return


@app.cell
def _eval_trend(mo):
    try:
        import plotly.graph_objects as go

        runs = [f"Run {i}" for i in range(1, 9)]
        escalation_recall = [0.92, 0.95, 0.97, 1.0, 1.0, 0.98, 1.0, 1.0]
        extraction_acc = [0.88, 0.91, 0.93, 0.95, 0.96, 0.95, 0.97, 0.97]
        precision = [0.85, 0.87, 0.90, 0.91, 0.92, 0.93, 0.93, 0.94]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=runs, y=escalation_recall, name="Escalation recall (gate: 1.0)",
                                 mode="lines+markers", line=dict(color="#E74C3C", width=2)))
        fig.add_trace(go.Scatter(x=runs, y=extraction_acc, name="Extraction accuracy (gate: 0.95)",
                                 mode="lines+markers", line=dict(color="#4A90D9", width=2)))
        fig.add_trace(go.Scatter(x=runs, y=precision, name="Auto-approve precision (gate: 0.90)",
                                 mode="lines+markers", line=dict(color="#27AE60", width=2)))
        # Gate threshold lines
        fig.add_hline(y=1.0,  line_dash="dot", line_color="#E74C3C",
                      annotation_text="Escalation recall gate (1.0)", annotation_position="bottom right")
        fig.add_hline(y=0.95, line_dash="dot", line_color="#4A90D9",
                      annotation_text="Extraction gate (0.95)")
        fig.add_hline(y=0.90, line_dash="dot", line_color="#27AE60",
                      annotation_text="Precision gate (0.90)")
        # Mark failed runs
        for i, r in enumerate(escalation_recall):
            if r < 1.0:
                fig.add_vline(x=runs[i], line_dash="dash",
                              line_color="#E74C3C", opacity=0.3)

        fig.update_layout(
            title="MLflow Evaluation Run History",
            yaxis_title="Score", yaxis_range=[0.8, 1.05],
            height=380, margin=dict(t=50, b=40),
        )
        mo.ui.plotly(fig)
    except ImportError:
        mo.callout(
            mo.md("Install `plotly` to see the evaluation trend chart."), kind="warn")
    return


# ---------------------------------------------------------------------------
# Section 5 – PII Tokenisation
# ---------------------------------------------------------------------------
@app.cell
def _s5_header(mo):
    mo.md("## 5. PII Tokenisation in the Ingestion Pipeline")
    return


@app.cell
def _s5_body(mo):
    mo.md("""
    Invoice documents contain **Personally Identifiable Information (PII)**:
    bank account numbers, sort codes, contact names, email addresses.
    AegisAP tokenises PII during the Silver zone transformation — before data reaches
    the search index or the LangGraph workflow.

    ### Tokenisation model

    ```python
    import hashlib, os

    def tokenise_pii(value: str, field_type: str) -> str:
        \"\"\"Replace a PII value with a stable, reversible token.\"\"\"
        # HMAC-based token — same value always produces same token
        # but cannot be reverse-engineered without the secret
        secret = os.environ["PII_TOKENISATION_KEY"]   # from Key Vault
        return "TOKEN_" + field_type + "_" + hashlib.sha256(
            (secret + value).encode()
        ).hexdigest()[:16]

    # Example:
    # sort_code "12-34-56"      → "TOKEN_SORT_a3b7c2d1e4f5a6b7"
    # account_number "12345678" → "TOKEN_ACCT_9f8e7d6c5b4a3210"
    ```

    The **de-tokenisation service** is a separate secured API that only:
    - The payment execution service can call (RBAC-controlled)
    - The auditor's review tool can call (with MFA step-up)

    No agent in the LangGraph workflow ever sees raw bank account numbers.

    > **Why HMAC, not random UUIDs?**  
    > A random UUID per PII occurrence breaks deduplication — two invoices from the same
    > vendor with the same bank account would appear to have different accounts.
    > HMAC produces the same token for the same value, enabling join operations on tokens
    > without exposing the underlying PII.

    > **OWASP Reference:** This pattern mitigates **A02: Cryptographic Failures** by
    > ensuring PII is not stored or processed in plaintext beyond the ingestion boundary.
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
        "Exercise 1 — Tier Assignment": mo.vstack([
            mo.md("""
**Task:** Assign each of the following data items to a tier in the authority pyramid (1–4)
and explain why:

1. The canonical amount for invoice INV-2024-001 (£1,250.00)
2. The vendor payment terms for ACME-001 (net-30)
3. The cached vendor name for a tooltip in the AP dashboard
4. The vendor policy chunks retrieved during invoice processing
5. The MLflow metric `escalation_recall = 1.0` for eval run `eval_20240301_143000`
6. The PostgreSQL checkpoint for the suspended workflow thread on INV-2024-042
            """),
            mo.accordion({
                "Show solution": mo.md("""
1. **Tier 1** — The canonical amount is the financial truth. It was validated by the canonicalisation function and committed to the PostgreSQL `invoices` table. This is the ledger record.

2. **Tier 2** — Vendor payment terms are in the Cosmos DB vendor master, which is canonical but derived from vendor contracts (Tier 1 source documents). Agents read from Tier 2; the payment terms can change when a new contract is signed (triggering an ADF pipeline update).

3. **Tier 3** — A dashboard tooltip can tolerate a short TTL cache miss (Redis). If the cache is stale by 15 minutes, no business harm results. Refreshed on cache miss from Cosmos DB (Tier 2).

4. **Tier 3** — Retrieved chunks are **operational context** for the current workflow run. They are stored in `WorkflowState` and the execution trace, but the authoritative source is the Azure AI Search index (Tier 2 rebuilt from document store).

5. **Tier 4** — MLflow metrics are analytical / derived data. They are produced by running the evaluation suite over a point-in-time dataset. They cannot be edited or corrected (append-only log). The gate check reads from Tier 4.

6. **Tier 1** — The LangGraph checkpoint IS the durable workflow state. It lives in the PostgreSQL checkpoints table (same Tier 1 database as the invoice ledger). Loss of this record = loss of the suspended workflow thread.
                """),
            }),
        ]),
    })
    return


@app.cell
def _exercise_2(mo):
    mo.accordion({
        "Exercise 2 — ADF Pipeline Failure Handling": mo.vstack([
            mo.md("""
**Scenario:** The ADF silver zone pipeline fails on 3 of 47 invoices in Tuesday's batch.
The remaining 44 are processed successfully and trigger the LangGraph workflow.
The 3 failed invoices are stuck in the bronze zone.

**Task:** Design the operational response:
1. How does ADF notify the operations team?
2. What data do you need to diagnose the 3 failures?
3. How do you reprocess ONLY the 3 failed invoices without re-running the 44?
4. How do you ensure the 3 invoices are not lost if the bronze zone storage blob is accidentally deleted?
            """),
            mo.accordion({
                "Show solution": mo.md("""
**1. Notification:**

Configure an ADF pipeline failure alert:
- Azure Monitor alert on `PipelineFailedRuns` metric → Action Group → email/Teams webhook
- ADF built-in Diagnostic Settings → Log Analytics workspace → KQL alert rule:
  ```kql
  ADFPipelineRun
  | where Status == "Failed"
  | where PipelineName == "invoice_silver_transform"
  | project PipelineName, RunId, Start, End, ErrorMessage
  ```

**2. Diagnostic data needed:**
- ADF pipeline run ID (to link to activity-level logs)
- Activity failure reason from `ADFActivityRun` log table
- The specific input invoice blob path(s) that caused failures
- Error message (schema parse error? PII tokenisation key vault timeout? Malformed PDF?)

**3. Reprocess only 3 failed invoices:**

ADF Tumbling Window triggers support **rerun of specific windows**.
For event-triggered pipelines, use the ADF Rerun capability:
- In Azure Portal → ADF Studio → Monitor → Pipeline Runs → select failed run → Rerun
- Or via ARM API: `POST /pipelines/{name}/createRun` with the specific blob paths as parameters

Set `dataflow.skipOnFirstFailure = false` in the pipeline configuration during rerun
to ensure errors are visible, not silently skipped.

**4. Prevent bronze zone loss:**

- Enable **Soft Delete** on the ADLS Gen2 storage account (30-day retention for blobs)
- Enable **Versioning** so accidental overwrites are recoverable
- ADF copies source files to bronze before transformation — ensure the copy activity uses `PreserveHierarchy` and does NOT delete source files on success
- For critical sources (ERP exports, SFTP): configure **Azure Backup for Storage** with a separate vault in a different resource group to prevent deletion by the same identity that runs ADF
                """),
            }),
        ]),
    })
    return


@app.cell
def _exercise_3(mo):
    mo.accordion({
        "Exercise 3 — Cosmos DB Schema Evolution": mo.vstack([
            mo.md("""
**New requirement:** The Finance team wants to add a `payment_hold` field to the vendor master.
When `payment_hold = true`, ALL invoices from that vendor should be rejected until the hold is lifted.

**Task:**
1. What does the new Cosmos DB document look like?
2. Sketch the code change required in AegisAP's vendor lookup function.
3. What backfill pipeline do you need to run for existing vendors?
4. Which team must approve this change before it reaches production and why?
            """),
            mo.accordion({
                "Show solution": mo.md("""
**1. New document schema:**
```json
{
  "id": "ACME-001",
  "vendor_id": "ACME-001",
  "name": "Acme Office Supplies Ltd",
  "payment_hold": false,           ← NEW FIELD
  "payment_hold_reason": null,     ← NEW FIELD (string when hold is active)
  "payment_hold_raised_by": null,  ← NEW FIELD (email of AP manager)
  "payment_hold_raised_at": null,  ← NEW FIELD (ISO 8601 timestamp)
  "payment_terms_days": 30,
  ...
}
```

**2. Code change in policy overlay:**
```python
def apply_policy_overlay(plan, canonical, vendor_record):
    violations = []

    # NEW: payment hold check — must be FIRST rule (highest priority)
    if vendor_record.get("payment_hold", False):
        violations.append(
            f"VENDOR_PAYMENT_HOLD: vendor {canonical['vendor_id']} has an active "
            f"payment hold (reason: {vendor_record.get('payment_hold_reason', 'not specified')}). "
            "All invoice processing suspended until hold is lifted."
        )
        # Return immediately — no need to check other rules
        return False, violations

    # ... existing rules continue ...
```

Use `.get("payment_hold", False)` — defaults to False for vendors without the field (forwards compatibility).

**3. Backfill pipeline:**

Simple ADF Data Flow activity or Python script:
```python
# Backfill: add payment_hold=False to all vendors that don't have the field
for item in container.read_all_items():
    if "payment_hold" not in item:
        container.upsert_item({
            **item,
            "payment_hold": False,
            "payment_hold_reason": None,
            "payment_hold_raised_by": None,
            "payment_hold_raised_at": None,
        })
```

Run with a Managed Identity that has `Cosmos DB Built-in Data Contributor` on the vendors container.

**4. Approval before production:**

The **Finance Controller** must approve this change because:
- `payment_hold = true` causes invoices to be rejected — it directly affects cash payments
- A configuration error (wrong default value, wrong vendor_id, case sensitivity bug) could
  accidentally block payments to ALL vendors
- This is a **financial control change** — it must be reviewed under the same change
  management process as changing the auto-approve threshold
- The change must be documented in the ADR register and included in the next security review
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
        "day": 6,
        "title": "Data & ML Integration",
        "completed_at": datetime.datetime.utcnow().isoformat() + "Z",
        "data_authority": {
            "tier1": "PostgreSQL (invoices, execution_traces, approval_requests)",
            "tier2": "Cosmos DB (vendor master) + Azure AI Search (policy docs)",
            "tier3": "Redis cache + LangGraph checkpoints",
            "tier4": "ADLS Gen2 (medallion) + MLflow (eval metrics)",
        },
        "pii_tokenisation": "HMAC-SHA256 with Key Vault secret",
        "adf_pipeline": "bronze → silver → gold → workflow trigger",
        "mlflow_gate": {
            "escalation_recall_threshold": 1.0,
            "extraction_accuracy_threshold": 0.95,
            "auto_approve_precision_threshold": 0.90,
        },
        "gate_passed": True,
    }

    out_dir = Path(__file__).resolve().parents[1] / "build" / "day6"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "data_integration_audit.json"
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

    1. **Bronze zone immutability:** The Operations team wants to delete old bronze zone files
       to save storage costs. The AP Manager says "we need to retain originals for 7 years
       for audit." Design a tiered retention policy that satisfies both constraints without
       changing the ADF pipeline.

    2. **MLflow gate bypass:** A release manager wants to bypass the `escalation_recall` gate
       for a hotfix release (there is a critical bug in production). Under what circumstances
       — if any — would you permit this, and what compensating controls are required?

    3. **Cosmos DB point read vs. query:** At 50,000 invoices/day, the difference between
       a 1 RU point read and a 5 RU query for vendor lookup is significant. Calculate the
       monthly RU cost difference and the equivalent cost in GBP (assume $0.00008 per RU
       in UK South region with provisioned throughput at 400 RU/s).
    """)
    return


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
@app.cell
def _summary(mo):
    mo.md("""
    ## Day 6 Summary Checklist

    - [ ] Explain the four data authority tiers and the conflict resolution rule
    - [ ] Describe the Bronze → Silver → Gold medallion pipeline and what happens at each stage
    - [ ] Configure a Cosmos DB client with `DefaultAzureCredential` (no connection-string key)
    - [ ] Explain why point reads are preferred over queries in Cosmos DB for vendor lookups
    - [ ] Implement HMAC-based PII tokenisation and explain why it is preferable to random UUIDs
    - [ ] Use MLflow to log an evaluation run with parameters, metrics, and gate tags
    - [ ] State the mandatory escalation recall threshold and why it cannot be lower than 1.0
    - [ ] Artifact `build/day6/data_integration_audit.json` exists and `gate_passed = true`
    """)
    return


@app.cell
def _forward(mo):
    mo.callout(
        mo.md("""
**Tomorrow — Day 7: Testing, Evaluation & Guardrails**

You have data flowing and ML results tracked. Tomorrow is about proving correctness
and safety: building the AegisAP eval suite, writing slice-based tests for high-risk
invoice classes, implementing PromptShield for prompt injection detection, and
wiring evaluation gates into the CI/CD pipeline so no regression reaches production.

Open `notebooks/day_7_testing_eval_guardrails.py` when ready.
        """),
        kind="success",
    )
    return



@app.cell
def _fde_learning_contract(mo):
    mo.md(r"""
    ---
    ## FDE Learning Contract — Day 06: Data Authority, System of Record, and Change Classification
    

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
    | Source Of Truth Hierarchy | 25 |
| Change Classification Rigor | 25 |
| Governance Realism | 20 |
| Incident Recovery Logic | 15 |
| Defense Quality | 15 |

    Pass bar: **80 / 100**   Elite bar: **90 / 100**

    ### Oral Defense Prompts

    1. Which data source did you demote in the authority hierarchy, and what scenario would cause a conflict between it and the authoritative source?
2. If you classify a threshold change as a policy change rather than a model change, what approval path changes and what is the blast radius of the wrong classification?
3. Who in the enterprise owns the data authority chart, and what evidence would an auditor require to prove it was followed during an incident?

    ### Artifact Scaffolds

    - `docs/curriculum/artifacts/day06/DATA_AUTHORITY_CHART.md`
- `docs/curriculum/artifacts/day06/CHANGE_CLASSIFICATION_MATRIX.md`
- `docs/curriculum/artifacts/day06/SOURCE_OF_TRUTH_CONFLICT_RUNBOOK.md`

    See `docs/curriculum/MENTAL_MODELS.md` for mental models reference.
    See `docs/curriculum/ASSESSOR_CALIBRATION.md` for scoring anchors.
    """)
    return


if __name__ == "__main__":
    app.run()
