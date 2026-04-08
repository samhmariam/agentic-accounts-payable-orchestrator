import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _bootstrap():
    import json
    import sys
    from pathlib import Path

    import marimo as mo

    repo_root = Path(__file__).resolve().parents[1]
    for candidate in [repo_root / "src", repo_root / "notebooks"]:
        text = str(candidate)
        if text not in sys.path:
            sys.path.insert(0, text)

    from aegisap.day3.graph import run_day3_workflow
    from aegisap.day3.retrieval.authority_policy import load_authority_policy
    from aegisap.day3.retrieval.azure_ai_search_adapter import AzureAISearchFixtureAdapter
    from aegisap.day3.retrieval.ranker import apply_authority_ranking
    from aegisap.day3.retrieval.structured_vendor_lookup import StructuredVendorLookup

    return (
        AzureAISearchFixtureAdapter,
        Path,
        StructuredVendorLookup,
        apply_authority_ranking,
        json,
        load_authority_policy,
        mo,
        repo_root,
        run_day3_workflow,
    )


@app.cell
def _title(mo):
    mo.md(
        """
        # Day 3 - Retrieval Authority, Search Evidence, and Boundary Repair

        Primary learner entrypoint: `modules/day_03_retrieval_authority/README.md`. Read the customer context and file manifest there before you start the incident.

        Day 3 begins with a poisoned evidence ranking problem: stale email context is
        being treated like authority. Your job is to prove where the ranking broke,
        prototype the repair, and then move the real fix into the production retrieval
        boundary.
        """
    )
    return


@app.cell
def _incident(mo):
    mo.md(
        """
        ## Incident

        Finance and Security caught a case where stale onboarding email evidence was
        ranking above the structured vendor master for bank details.

        **What success looks like**

        - structured vendor master evidence outranks stale email evidence again
        - stale evidence is preserved as history, not deleted or ignored
        - the ranking repair is defended with tests and Day 3 boundary evidence
        """
    )
    return


@app.cell
def _portal_investigation(mo):
    mo.md(
        """
        ## Portal Investigation

        Investigate the live surfaces before you touch the ranker:

        1. Open Azure AI Search and inspect the index entries for the vendor and bank-change evidence.
        2. Confirm the stale email document is still present and timestamped correctly.
        3. Compare the portal evidence with the structured system-of-record vendor data.
        4. Capture the exact reason the wrong source won: weight, recency, or exact-match policy.
        """
    )
    return


@app.cell
def _lab_repair_intro(mo):
    mo.md(
        """
        ## Lab Repair

        Use this notebook as a ranking scratchpad only. Prove the authority order here,
        then move the real repair into the repo.
        """
    )
    return


@app.cell
def _controls(mo):
    vendor_id = mo.ui.text(value="VEND-001", label="Vendor ID")
    bank_last4 = mo.ui.text(value="4421", label="Expected bank-account last four")
    mo.vstack([vendor_id, bank_last4])
    return bank_last4, vendor_id


@app.cell
def _ranking_preview(
    AzureAISearchFixtureAdapter,
    StructuredVendorLookup,
    apply_authority_ranking,
    bank_last4,
    json,
    load_authority_policy,
    mo,
    repo_root,
    vendor_id,
):
    policy = load_authority_policy(repo_root / "src" / "aegisap" / "day3" / "policies" / "source_authority_rules.yaml")
    structured = StructuredVendorLookup().search(vendor_id=vendor_id.value.strip(), vendor_name=None)
    unstructured = AzureAISearchFixtureAdapter().search(
        query=f"Acme Office Supplies bank change {bank_last4.value.strip()}"
    )
    ranked = apply_authority_ranking(
        structured + unstructured,
        policy=policy,
        query_terms={"bank_account_last4": bank_last4.value.strip()},
    )
    preview = [
        {
            "rank": index + 1,
            "evidence_id": item.evidence_id,
            "source_type": item.source_type,
            "authority_tier": item.authority_tier,
            "authority_adjusted_score": item.authority_adjusted_score,
            "bank_account_last4": item.metadata.get("bank_account_last4"),
        }
        for index, item in enumerate(ranked[:5])
    ]
    mo.callout(
        mo.md(
            f"""
            Top ranked evidence:

            ```json
            {json.dumps(preview, indent=2)}
            ```
            """
        ),
        kind="info",
    )
    return


@app.cell
def _workflow_preview(json, mo, repo_root, run_day3_workflow):
    invoice = json.loads((repo_root / "fixtures" / "golden_thread" / "day3_invoice.json").read_text(encoding="utf-8"))
    state = run_day3_workflow(invoice, retrieval_mode="fixture")
    decision = state.agent_findings["decision"]
    vendor_risk = state.agent_findings["vendor_risk"]
    mo.callout(
        mo.md(
            f"""
            Workflow preview:

            - `recommendation={decision.recommendation}`
            - `next_step={decision.next_step}`
            - `vendor_risk_status={vendor_risk.status}`
            - `evidence_ids={decision.evidence_ids}`
            """
        ),
        kind="success",
    )
    return


@app.cell
def _codification_bridge(mo):
    mo.md(
        """
        ## Codification Bridge

        Treat the search portal view and the notebook ranking output as the same problem statement.

        - Portal state: Azure AI Search still contains both the stale email and the authoritative vendor record.
        - Notebook proof: the ranking preview and workflow preview show which authority rule drifted.
        - Permanent repo change: `src/aegisap/day3/policies/source_authority_rules.yaml`, `src/aegisap/day3/retrieval/ranker.py`, and, if needed, `src/aegisap/day3/retrieval/authority_policy.py`.

        Rosetta Stone: `notebooks/bridges/day03_retrieval_authority.md`
        """
    )
    return


@app.cell
def _production_patch(mo):
    mo.md(
        """
        ## Production Patch

        This section is **markdown-only**.

        Do not edit repo files from this notebook.

        STOP. Close this notebook.

        Open the exact relative filepath listed below in your IDE. Write the durable patch there, not inside Marimo.

        Move into the real retrieval boundary and implement the repair in the codebase:

        - `src/aegisap/day3/policies/source_authority_rules.yaml`
        - `src/aegisap/day3/retrieval/ranker.py`
        - `src/aegisap/day3/retrieval/authority_policy.py` if the policy loader needs help

        Then update the written Day 3 evidence:

        - `docs/curriculum/artifacts/day03/RAG_BOUNDARY_DECISION.md`
        - `docs/curriculum/artifacts/day03/FRAMEWORK_DECISION_MATRIX.md`

        ### Export to Production

        - Which portal document was wrongly winning?
        - Which authority rule or score adjustment must change in `source_authority_rules.yaml` or `ranker.py`?
        - Which verification proves authoritative evidence still wins without deleting history?
        """
    )
    return


@app.cell
def _verification(repo_root, mo):
    artifact_path = repo_root / "build" / "day3" / "golden_thread_day3.json"
    artifact_note = (
        f"Current artifact present: `{artifact_path.relative_to(repo_root)}`"
        if artifact_path.exists()
        else "Artifact missing: rebuild the Day 3 artifact after the repair."
    )
    mo.md(
        f"""
        ## Verification

        Run these commands in the terminal:

        ```bash
        uv run python -m pytest tests/day3/test_vendor_authority_ranking.py tests/day3/test_day3_exit_check.py -q
        uv run aegisap-lab artifact rebuild --day 03
        ```

        {artifact_note}
        """
    )
    return


@app.cell
def _chaos_gate(mo):
    mo.md(
        """
        ## Chaos Gate

        Failure signal: Search evidence disagrees with the source-of-truth policy and the ranker surfaces the wrong authority.

        Diagnostic surface: Azure AI Search index state, notebook retrieval proof, and authority policy files under src/aegisap/day3/.

        Expected recovery artifact: `build/day3/golden_thread_day3.json`

        Time box: 25 minutes. If you miss it, stop and rerun the four pillars in `docs/curriculum/FDE_DEBUGGING_FRAMEWORK.md`.
        """
    )
    return


@app.cell
def _map_the_gap(mo):
    mo.md(
        """
        ## Map the Gap

        Capture these before you ask for review:

        - Portal action or observed state:
        - Exact API/SDK/Python call that matches it:
        - Exact relative production filepath that made the fix durable:
        """
    )
    return


@app.cell
def _pr_defense(mo):
    mo.md(
        """
        ## PR Defense

        Answer these three questions before you push:

        - What trade-off did I make today to satisfy the customer constraint?
        - What is the blast radius if my code fails?
        - How will I know it failed in production?

        Copy-ready PR body:

        ```md
        ## Principal Review Defense
        - Trade-off: <name the compromise and why it was worth it>
        - Blast radius: <name the affected systems, approvers, and rollback edge>
        - Production failure signal: <monitor, alert, trace, or dashboard link>
        - Constraint held: <which inherited customer rule stayed intact>
        ```

        Open or update a PR targeting `cohort/<your-name>/<day-slug>`, paste the markdown block below into the PR body, and push to trigger `.github/workflows/principal-review.yml` on `opened`, `synchronize`, or `ready_for_review`.
        """
    )
    return
