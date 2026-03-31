"""
Day 3 — Multi-Agent RAG & Authority Ranking
=============================================
Query Azure AI Search and the pgvector store in parallel, then watch the
authority-ranking policy score and reorder conflicting evidence in real time.

Run:
    marimo edit notebooks/day3_retrieval_authority.py
"""

import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _intro(mo):
    mo.md("""
    # Day 3 — Multi-Agent RAG & Authority Ranking

    **What you will learn**:
    - Why retrieval needs *multiple agents* — PO match, vendor risk, and decision synthesis
    - How Azure AI Search (hybrid BM25 + vector) surfaces evidence
    - How the 4-tier authority policy scores and reorders conflicting sources
    - How recency decay down-weights stale facts

    > Prerequisite: `build/day2/golden_thread_day2.json` must exist.
    """)
    return


@app.cell
def _lab_contract(mo):
    from _shared.lab_guide import render_lab_overview

    render_lab_overview(
        mo,
        prerequisites=[
            "Day 2 produced `build/day2/golden_thread_day2.json`.",
            "Azure AI Search is provisioned if you want live retrieval.",
        ],
        required_inputs=[
            "A Day 2 artifact with invoice and routing context.",
            "A retrieval backend selection.",
        ],
        required_env_vars=[
            "AZURE_SEARCH_ENDPOINT",
            "AZURE_SEARCH_DAY3_INDEX",
        ],
        expected_artifact="build/day3/golden_thread_day3.json",
        pass_criteria=[
            "Evidence is retrieved and ranked by authority.",
            "The notebook shows either a synthesis output or an actionable retrieval failure.",
            "The Day 3 artifact is written for Day 4 planning.",
        ],
        implementation_exercise=(
            "Use a seeded regression or custom evidence bundle to prove the authoritative source "
            "wins and the artifact cites the correct evidence."
        ),
    )
    return


@app.cell
def _load_day2(mo):
    import json as _j
    from pathlib import Path as _P

    artifact_path = _P(__file__).resolve(
    ).parents[1] / "build" / "day2" / "golden_thread_day2.json"
    mo.stop(
        not artifact_path.exists(),
        mo.callout(mo.md(
            "Run Day 2 first — `build/day2/golden_thread_day2.json` not found."), kind="danger"),
    )
    data = _j.loads(artifact_path.read_text())
    data.pop("_meta", None)
    workflow_state = data.get("workflow_state", data)
    canonical_invoice = workflow_state.get("invoice", {})

    vendor_master_path = _P(__file__).resolve(
    ).parents[1] / "data" / "day3" / "structured" / "vendor_master.json"
    vendor_rows = _j.loads(vendor_master_path.read_text()) if vendor_master_path.exists() else []
    supplier_name = canonical_invoice.get("supplier_name") or workflow_state.get("vendor", {}).get("vendor_name")
    vendor_row = next(
        (row for row in vendor_rows if row.get("vendor_name", "").lower() == str(supplier_name or "").lower()),
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
    po_number = invoice_data["po_number"]
    vendor_name = invoice_data["vendor_name"]

    mo.vstack([
        mo.md("## Day 2 Artifact Loaded"),
        mo.hstack([
            mo.stat(label="Invoice ID", value=invoice_data.get("invoice_id", "—")),
            mo.stat(label="PO Number", value=po_number),
            mo.stat(label="Vendor", value=vendor_name),
        ]),
    ])
    return (invoice_data,)


@app.cell
def _retrieval_config(mo):
    retrieval_mode = mo.ui.dropdown(
        options=["fixture", "azure_search_live", "pgvector_fixture"],
        value="fixture",
        label="Retrieval Backend",
    )
    mo.vstack([
        mo.md("## 1 — Retrieval Configuration"),
        retrieval_mode,
        mo.callout(
            mo.md(
                "Queries are derived from the Day 3 invoice fields and policy defaults in the current workflow code."
            ),
            kind="info",
        ),
    ])
    return (retrieval_mode,)


@app.cell
def _run_retrieval(invoice_data, mo, retrieval_mode):
    import time as _t
    from aegisap.day3.graph import run_day3_workflow
    from aegisap.day3.retrieval.interfaces import build_retrieval_config
    from aegisap.day3.export import evidence_to_table

    retrieval_cfg = build_retrieval_config(retrieval_mode.value)

    t_start = _t.monotonic()
    try:
        state = run_day3_workflow(
            invoice=invoice_data,
            retrieval_mode=retrieval_mode.value,
            retrieval_config=retrieval_cfg,
        )
        elapsed_ms = int((_t.monotonic() - t_start) * 1000)
        evidence_rows = evidence_to_table(state.bucket("vendor", "policy", "po"))
        error = None
    except Exception as exc:  # noqa: BLE001
        elapsed_ms = int((_t.monotonic() - t_start) * 1000)
        evidence_rows = []
        error = str(exc)
        state = None

    mo.stat(label="Retrieval latency", value=f"{elapsed_ms} ms")
    return elapsed_ms, error, evidence_rows, state


@app.cell
def _display_evidence(error, evidence_rows, mo):
    if error:
        _out = mo.callout(
            mo.md(f"**Retrieval error**: `{error}`"), kind="danger")
    elif not evidence_rows:
        _out = mo.callout(mo.md("No evidence items returned."), kind="warn")
    else:
        _out = mo.vstack([
            mo.md(
                f"## 2 — Evidence ({len(evidence_rows)} items) — ranked by authority-adjusted score"),
            mo.ui.table(
                evidence_rows,
                selection=None,
            ),
        ])
    _out
    return


@app.cell
def _authority_detail(evidence_rows, mo):
    mo.stop(not evidence_rows, mo.md("No evidence to display."))
    mo.vstack([
        mo.md("## 3 — Authority Tier Legend"),
        mo.ui.table([
            {"Tier": 1, "Label": "System of Record",
                "Example": "ERP vendor master"},
            {"Tier": 2, "Label": "Controlled Policy Artifact",
                "Example": "Approved bank change form"},
            {"Tier": 3, "Label": "Business Communication",
                "Example": "Email from AP manager"},
            {"Tier": 4, "Label": "Derived / Model Summary",
                "Example": "LLM-generated summary"},
        ], selection=None),
        mo.md(
            "> The authority-adjusted score = `retrieval_score × tier_weight × recency_decay`. "
            "Compare the returned evidence ordering across retrieval backends to see the policy reorder conflicting sources."
        ),
    ])
    return


@app.cell
def _display_synthesis(mo, state):
    mo.stop(state is None, mo.md("Retrieval failed; no synthesis to show."))
    synthesis = state.agent_findings.get("decision")
    if synthesis:
        _out = mo.vstack([
            mo.md("## 4 — Decision Synthesis"),
            mo.tree(synthesis if isinstance(synthesis, dict) else vars(synthesis)),
        ])
    else:
        _out = mo.callout(
            mo.md("Synthesis not available in this retrieval mode."), kind="warn")
    _out
    return


@app.cell
def _persist(elapsed_ms, evidence_rows, mo, state):
    mo.stop(state is None, mo.md("Retrieval failed — skipping artifact write."))
    import json as _j
    from pathlib import Path as _P
    from dataclasses import asdict, is_dataclass

    def _serialize(obj):
        if is_dataclass(obj):
            return asdict(obj)
        if hasattr(obj, "model_dump"):
            return obj.model_dump(mode="json")
        return str(obj)

    out_dir = _P(__file__).resolve().parents[1] / "build" / "day3"
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact = {
        "evidence": evidence_rows,
        "_meta": {"elapsed_ms": elapsed_ms},
    }
    if is_dataclass(state):
        artifact.update(asdict(state))
    elif hasattr(state, "model_dump"):
        artifact.update(state.model_dump(mode="json"))
    elif hasattr(state, "__dict__"):
        artifact.update({k: _serialize(v) for k, v in vars(state).items()})

    out_path = out_dir / "golden_thread_day3.json"
    out_path.write_text(_j.dumps(artifact, indent=2, default=str))

    mo.vstack([
        mo.callout(mo.md(
            "Artifact written to `build/day3/golden_thread_day3.json`"), kind="success"),
        mo.download(
            data=_j.dumps(artifact, indent=2, default=str).encode(),
            filename="golden_thread_day3.json",
            mimetype="application/json",
            label="Download golden_thread_day3.json",
        ),
    ])
    return


@app.cell
def _ready_for_next_day(mo):
    from _shared.lab_guide import render_readiness_check

    render_readiness_check(
        mo,
        artifact_relpath="build/day3/golden_thread_day3.json",
        next_day="Day 4",
        recovery_command="marimo edit notebooks/day3_retrieval_authority.py",
    )
    return


if __name__ == "__main__":
    app.run()
