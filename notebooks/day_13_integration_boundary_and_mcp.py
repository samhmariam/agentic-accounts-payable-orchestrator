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

    from aegisap.mcp.schemas import McpCapabilities

    return McpCapabilities, json, mo, repo_root


@app.cell
def _title(mo):
    mo.md(
        """
        # Day 13 - Integration Boundaries, Async Reliability, and Contract Management

        Primary learner entrypoint: `modules/day_13_integration_boundary/README.md`. Read the customer context and file manifest there before you start the incident.

        Day 13 starts with an MCP contract incident: the governed write-path
        tool vanished from the live capabilities contract, which means external
        callers can no longer see the safe boundary they are supposed to use.
        Your job is to prove the drift, restore the contract, and defend why
        async compensating actions still belong behind the boundary.
        """
    )
    return


@app.cell
def _incident(mo):
    mo.md(
        """
        ## Incident

        A partner integration escalated that the MCP server no longer advertises
        the payment-hold write path, even though the reliability path still
        depends on compensating actions behind that boundary.

        **What success looks like**

        - `/capabilities` exposes the governed write-path tool again
        - the write path still registers compensating-action safety in stub or live mode
        - the Day 13 artifact packet explains contract ownership, partner impact, and rollback posture
        """
    )
    return


@app.cell
def _portal_investigation(mo):
    mo.md(
        """
        ## Portal Investigation

        Start from the hosted integration surface before editing code:

        1. Inspect the Container App or Function App revision serving the MCP boundary.
        2. Check application logs for capability requests, write-path calls, and DLQ or retry symptoms.
        3. Confirm whether the partner is missing a contract element or whether the write path is actually unavailable.
        4. Capture the exact difference between the intended MCP contract and the boundary the runtime is currently publishing.
        """
    )
    return


@app.cell
def _lab_intro(mo):
    mo.md(
        """
        ## Lab Repair

        Use the notebook to inspect the MCP capability advertisement in-memory.
        The real repair still belongs in the production integration boundary.
        """
    )
    return


@app.cell
def _starter_investigation(mo):
    mo.md(
        """
        ## Starter Investigation

        Starter-only mode is active from this day onward.

        Do not use the shared lab wrapper helpers in this phase.
        Build your own probes with `azure-identity` and the relevant `azure-mgmt-*` SDK clients, then carry only the proof back into the notebook.
        """
    )
    return


@app.cell
def _lab_preview(McpCapabilities, json, mo):
    preview = McpCapabilities().model_dump(mode="json")
    mo.callout(
        mo.md(
            f"""
            MCP capability preview:

            ```json
            {json.dumps(preview, indent=2)}
            ```
            """
        ),
        kind="info",
    )
    return


@app.cell
def _kql_evidence(mo):
    mo.md(
        """
        ## KQL Evidence

        Save `build/day13/kql_evidence.json` before you patch production code.

        Capture at least one literal Log Analytics query with:

        - workspace
        - purpose
        - observed excerpt
        - operator interpretation
        """
    )
    return


@app.cell
def _codification_bridge(mo):
    mo.md(
        """
        ## Why This Fails In Prod

        List three specific ways this notebook logic fails in an Azure Container App. You must reference at least one Azure limit (memory, timeout, or ephemeral storage) and one concurrency issue.

        ## Codification Bridge

        Treat the hosted contract view and notebook capability preview as one boundary statement.

        - Portal state: the published MCP contract no longer matches the intended governed write path.
        - Notebook proof: the capability preview shows which contract element should exist.
        - Permanent repo change: `src/aegisap/mcp/server.py`, `src/aegisap/mcp/schemas.py`, and, if needed, the DLQ or compensating-action code.

        Rosetta Stone: `notebooks/bridges/day13_integration_boundary.md`
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

        Move into the real integration boundary and implement the repair in:

        - `src/aegisap/mcp/server.py`
        - `src/aegisap/mcp/schemas.py` only if the contract object itself drifted
        - `src/aegisap/integration/dlq_consumer.py` or `src/aegisap/integration/compensating_action.py` if the reliability path is also broken

        Then update the Day 13 evidence:

        - `docs/curriculum/artifacts/day13/EXTERNAL_CONTRACT_POLICY.md`
        - `docs/curriculum/artifacts/day13/COMPENSATING_ACTION_CATALOG.md`
        - `docs/curriculum/artifacts/day13/API_CHANGE_COMMUNICATION_PLAN.md`

        ### Export to Production

        - Which capability was missing for partners?
        - Which file republishes the durable boundary contract?
        - Which verification proves the contract and reliability artifacts agree again?
        """
    )
    return


@app.cell
def _verification(repo_root, mo):
    contract_path = repo_root / "build" / "day13" / "mcp_contract_report.json"
    dlq_path = repo_root / "build" / "day13" / "dlq_drain_report.json"
    notes = []
    for path in (contract_path, dlq_path):
        if path.exists():
            notes.append(f"Current artifact present: `{path.relative_to(repo_root)}`")
        else:
            notes.append(f"Artifact missing: `{path.relative_to(repo_root)}`")
    mo.md(
        f"""
        ## Verification

        Run these commands in the terminal:

        ```bash
        uv run python -m pytest tests/day13/test_dlq_consumer.py tests/day13/test_mcp_server.py tests/day13/test_payment_hold.py -q
        uv run aegisap-lab artifact rebuild --day 13
        ```

        {'\n\n'.join(notes)}
        """
    )
    return


@app.cell
def _native_tooling_gate(mo):
    mo.md(
        """
        ## Native Tooling Gate

        Policy source: `docs/curriculum/NATIVE_TOOLING_POLICY.md`

        Save your raw operator proof in `build/day13/native_operator_evidence.json`.

        Allowed tools during this gate:

        - Azure Portal
        - `az`
        - `az rest`
        - raw KQL
        - `git`
        - `curl`
        - `nslookup` or `Resolve-DnsName`

        Tools banned during this gate:

        - `aegisap-lab`
        - helper verification wrappers
        - canned answer keys

        Wrappers stay banned until both raw evidence files are complete. After that,
        they may be used only for artifact rebuild, mastery, or reset flows.
        """
    )
    return


@app.cell
def _chaos_gate(mo):
    mo.md(
        """
        ## Chaos Gate

        Failure signal: Boundary drift leaves partner traffic in the DLQ or exposes an incomplete MCP contract to the client.

        Diagnostic surface: MCP client notebook flow, DLQ evidence, compensating-action code, and cloud-truth posture checks.

        Expected recovery artifact: `build/day13/mcp_contract_report.json`

        Time box: 30 minutes. If you miss it, stop and rerun the four pillars in `docs/curriculum/FDE_DEBUGGING_FRAMEWORK.md`.
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


if __name__ == "__main__":
    app.run()
