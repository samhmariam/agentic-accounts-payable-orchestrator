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

    from _shared.curriculum_scaffolds import deep_reload_modules

    deep_reload_modules("aegisap")

    return json, mo, repo_root


@app.cell
def _title(mo):
    mo.md(
        """
        # Day 11 - Delegated Identity, OBO, and Authority Confusion Defense

        Primary learner entrypoint: `modules/day_11_delegated_identity/README.md`. Read the customer context and file manifest there before you start the incident.

        Day 11 starts with an authority-confusion incident: the approval path no
        longer proves that the OBO actor still belongs to the finance approver
        group. Your job is to show the broken actor-binding assumption, repair
        it in the identity boundary, and defend why payload identity is never an
        acceptable substitute for token-backed group evidence.
        """
    )
    return


@app.cell
def _incident(mo):
    mo.md(
        """
        ## Incident

        Finance security escalated an approval event where the service could no
        longer prove the human approver was still in the required Entra group.

        **What success looks like**

        - actor binding uses the required group ID, not a payload field or the user OID
        - the Day 11 contract shows app identity, OBO exchange, and actor binding all passing
        - the written threat model explains why delegated authority cannot be bypassed for speed
        """
    )
    return


@app.cell
def _portal_investigation(mo):
    mo.md(
        """
        ## Portal Investigation

        Start in Entra before touching the code:

        1. Open the backend app registration and confirm the service principal that performs the OBO exchange.
        2. Open the approver group and verify which users actually hold payment authority right now.
        3. Compare the group object ID in Entra to the identity evidence the runtime artifact claims to trust.
        4. Capture exactly where the runtime could confuse the acting user with the required authority group.
        """
    )
    return


@app.cell
def _lab_intro(mo):
    mo.md(
        """
        ## Lab Repair

        Use the notebook to model the group-membership check with controlled
        payloads. The real repair still belongs in the production identity code.
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
def _lab_preview(json, mo):
    preview = {
        "actor_oid": "user-oid-123",
        "required_group_id": "finance-approvers-001",
        "graph_groups": [
            {"id": "finance-approvers-001", "displayName": "Finance Approvers"},
            {"id": "audit-readers-002", "displayName": "Audit Readers"},
        ],
    }
    preview["would_pass"] = any(
        group["id"] == preview["required_group_id"] for group in preview["graph_groups"]
    )
    mo.callout(
        mo.md(
            f"""
            Prototype actor-binding preview:

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

        Save `build/day11/kql_evidence.json` before you patch production code.

        Capture at least one literal Log Analytics query with:

        - capture order
        - captured_before_patch=true
        - workspace
        - first_signal_or_followup
        - correlation or trace reference when available
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

        Treat the Entra evidence and notebook actor-binding preview as one authority contract.

        - Portal state: the required approver group and the acting user are no longer being bound together safely.
        - Notebook proof: the actor-binding preview shows whether the runtime is trusting payload identity instead of group-backed evidence.
        - Durable repo boundary: the delegated-identity owner in the actor-binding or token-exchange boundary that restores human-bound approval.

        Rosetta Stone: `notebooks/bridges/day11_delegated_identity.md`
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

        Edit the repo target in your IDE first.

        Rerun this notebook bootstrap cell after every repo edit so `deep_reload_modules(...)`
        reloads the real package imports before you trust the notebook proof again.

        Write the durable patch in the repo target below, not inside Marimo.

        Move into the real identity boundary and identify the durable owner of:

        - actor binding for the real human approver
        - delegated token exchange and authority scoping
        - contract verification only if the evidence path is wrong

        Then update the Day 11 evidence:

        - `docs/curriculum/artifacts/day11/APPROVAL_AUTHORITY_MODEL.md`
        - `docs/curriculum/artifacts/day11/OBO_THREAT_MODEL.md`
        - `docs/curriculum/artifacts/day11/IDENTITY_EXCEPTION_REQUEST_RESPONSE.md`

        ### Export to Production

        - Which group or actor identifier proved the authority confusion?
        - Which file permanently blocks payload-only approval?
        - Which verification proves the delegated path is safe again?
        """
    )
    return


@app.cell
def _verification(repo_root, mo):
    artifact_path = repo_root / "build" / "day11" / "obo_contract.json"
    artifact_note = (
        f"Current artifact present: `{artifact_path.relative_to(repo_root)}`"
        if artifact_path.exists()
        else "Artifact missing: rebuild the Day 11 artifact after the repair."
    )
    mo.md(
        f"""
        ## Verification

        Run these commands in the terminal:

        ```bash
        uv run python -m pytest tests/day11/test_actor_verification.py tests/day11/test_obo_flow.py tests/day11/test_obo_simulation.py -q
        uv run aegisap-lab artifact rebuild --day 11
        ```

        {artifact_note}
        """
    )
    return


@app.cell
def _native_tooling_gate(mo):
    mo.md(
        """
        ## Native Tooling Gate

        Policy source: `docs/curriculum/NATIVE_TOOLING_POLICY.md`

        Save your raw operator proof in `build/day11/native_operator_evidence.json`.

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

        Failure signal: The OBO path loses actor fidelity, making approvals or downstream actions look like app-only activity.

        Starting signal: Delegated approval begins failing with actor-binding or OBO symptoms once real identity checks run.

        Expected recovery artifact: `build/day11/obo_contract.json`

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
