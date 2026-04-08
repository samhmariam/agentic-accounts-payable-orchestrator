import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _bootstrap():
    import sys
    from pathlib import Path

    import marimo as mo

    repo_root = Path(__file__).resolve().parents[1]
    for candidate in [repo_root / "src", repo_root / "notebooks"]:
        text = str(candidate)
        if text not in sys.path:
            sys.path.insert(0, text)

    return Path, mo, repo_root


@app.cell
def _title(mo):
    mo.md(
        """
        # Day 8 - IaC, Identity Planes, and Secure Release Ownership

        Primary learner entrypoint: `modules/day_08_iac_identity/README.md`. Read the customer context and file manifest there before you start the incident.

        Day 8 begins with an IaC drift failure: the runtime identity is asking for
        more Azure AI Search authority than the production contract allows. Your job
        is to trace the over-privileged assignment, repair it in infrastructure code,
        and prove the release boundary is back to least privilege.
        """
    )
    return


@app.cell
def _incident(mo):
    mo.md(
        """
        ## Incident

        The platform team caught a staging deployment where the runtime principal was
        granted Search contributor-style access instead of reader-only access.

        **What success looks like**

        - the runtime identity returns to read-only search access
        - the admin identity keeps the contributor privileges it actually needs
        - the Day 8 release packet explains the blast radius of over-privileged search access
        """
    )
    return


@app.cell
def _portal_investigation(mo):
    mo.md(
        """
        ## Portal Investigation

        Investigate the live Azure shape first:

        1. Open Azure AI Search IAM and identify which principal owns Search Index Data Reader vs Contributor.
        2. Open the Container App managed identity and confirm which principal the runtime path actually uses.
        3. Compare the portal role assignments to the Bicep role-assignment module.
        4. Capture whether the drift is isolated to runtime search access or part of a wider release-role problem.
        """
    )
    return


@app.cell
def _lab_intro(mo):
    mo.md(
        """
        ## Lab Repair

        Use the notebook to inspect the infrastructure contract and prove what the
        runtime assignment should be. The actual fix still belongs in the repo.
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
def _assignment_preview(Path, mo, repo_root):
    template = (repo_root / "infra" / "modules" / "role_assignments.bicep").read_text(encoding="utf-8")
    marker = "resource runtimeSearchAssignment"
    start = template.index(marker)
    snippet = template[start:start + 420]
    severity = "danger" if "searchIndexDataContributorRoleDefinitionId" in snippet else "info"
    mo.callout(
        mo.md(
            f"""
            Runtime search-assignment snippet:

            ```bicep
            {snippet}
            ```
            """
        ),
        kind=severity,
    )
    return


@app.cell
def _contract_check(Path, mo, repo_root):
    search_template = (repo_root / "infra" / "foundations" / "search_service.bicep").read_text(encoding="utf-8")
    local_auth_disabled = "disableLocalAuth: true" in search_template
    mo.callout(
        mo.md(
            f"""
            Deployment contract preview:

            - `disableLocalAuth` locked: `{local_auth_disabled}`
            - runtime role should be `Search Index Data Reader`
            - admin role should remain `Search Index Data Contributor`
            """
        ),
        kind="success" if local_auth_disabled else "warn",
    )
    return


@app.cell
def _kql_evidence(mo):
    mo.md(
        """
        ## KQL Evidence

        Save `build/day8/kql_evidence.json` before you patch production code.

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

        Treat the Azure IAM view and the notebook snippet as one least-privilege contract.

        - Portal state: the runtime principal is over-privileged or the identity wiring no longer matches the expected release boundary.
        - Notebook proof: the assignment preview and contract check show the runtime must stay reader-only.
        - Permanent repo change: `infra/modules/role_assignments.bicep`, `infra/foundations/search_service.bicep`, and, if needed, `infra/modules/container_app.bicep`.

        Rosetta Stone: `notebooks/bridges/day08_identity_iac.md`
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

        Move into the real infrastructure boundary and implement the repair in:

        - `infra/modules/role_assignments.bicep`
        - `infra/foundations/search_service.bicep` if local-auth posture drifted too
        - `infra/modules/container_app.bicep` only if the runtime identity wiring is wrong

        Then update the written Day 8 evidence:

        - `docs/curriculum/artifacts/day08/SECURITY_REVIEW_PACKET.md`
        - `docs/curriculum/artifacts/day08/DRIFT_RESPONSE_PLAYBOOK.md`
        - `docs/curriculum/artifacts/day08/RELEASE_OWNERSHIP_MAP.md`

        ### Export to Production

        - Which principal and role were wrong in the portal?
        - Which Bicep resource or property makes the least-privilege fix permanent?
        - Which verification and rebuilt artifact prove runtime access is back inside the contract?
        """
    )
    return


@app.cell
def _verification(repo_root, mo):
    artifact_path = repo_root / "build" / "day8" / "deployment_design.json"
    artifact_note = (
        f"Current artifact present: `{artifact_path.relative_to(repo_root)}`"
        if artifact_path.exists()
        else "Artifact missing: rebuild the Day 8 artifact after the repair."
    )
    mo.md(
        f"""
        ## Verification

        Run these commands in the terminal:

        ```bash
        uv run python -m pytest tests/day7/security/test_search_token_auth_only.py tests/day8/test_security_and_context.py tests/day8/test_observability_contract.py -q
        uv run aegisap-lab artifact rebuild --day 08
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

        Failure signal: Role assignments or service posture drifted, and the runtime principal can mutate resources it should only read.

        Diagnostic surface: Portal role assignments, Marimo Bicep bridge, and live audit-production probes.

        Expected recovery artifact: `build/day8/deployment_design.json`

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
