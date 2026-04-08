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
        # Day 13 - Integration Boundary Rescue Mission

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
def _production_patch(mo):
    mo.md(
        """
        ## Production Patch

        This section is **markdown-only**.

        Do not edit repo files from this notebook.

        Move into the real integration boundary and implement the repair in:

        - `src/aegisap/mcp/server.py`
        - `src/aegisap/mcp/schemas.py` only if the contract object itself drifted
        - `src/aegisap/integration/dlq_consumer.py` or `src/aegisap/integration/compensating_action.py` if the reliability path is also broken

        Then update the Day 13 evidence:

        - `docs/curriculum/artifacts/day13/EXTERNAL_CONTRACT_POLICY.md`
        - `docs/curriculum/artifacts/day13/COMPENSATING_ACTION_CATALOG.md`
        - `docs/curriculum/artifacts/day13/API_CHANGE_COMMUNICATION_PLAN.md`
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
def _pr_defense(mo):
    mo.md(
        """
        ## PR Defense

        Your pull request must include:

        - the exact MCP contract drift and the partner-visible symptom it caused
        - why the governed boundary must advertise the write path instead of letting callers guess
        - proof that the Day 13 contract and DLQ artifacts now tell the same reliability story
        - one sentence on the blast radius of publishing a stale or incomplete external contract
        """
    )
    return


if __name__ == "__main__":
    app.run()
