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

    from aegisap.network.bicep_policy_checker import BicepPolicyChecker

    return BicepPolicyChecker, json, mo, repo_root


@app.cell
def _title(mo):
    mo.md(
        """
        # Day 12 - Private Networking, Egress Control, and Security Dependency Management

        Primary learner entrypoint: `modules/day_12_private_networking/README.md`. Read the customer context and file manifest there before you start the incident.

        Day 12 starts with a network-isolation incident: the static policy check
        stopped seeing a public endpoint, which means a deployment can look safe
        while the Azure network boundary is drifting. Your job is to prove the
        blind spot, repair the checker, and defend why private access must be
        demonstrated with both static and live evidence.
        """
    )
    return


@app.cell
def _incident(mo):
    mo.md(
        """
        ## Incident

        Security escalated a deployment where a public endpoint reappeared, but
        the Day 12 gate package did not catch it.

        **What success looks like**

        - the static checker inspects the right ARM property path again
        - live posture evidence still proves DNS is private and public ingress is unavailable
        - the Day 12 policy and exception artifacts explain why public access is never acceptable in production
        """
    )
    return


@app.cell
def _portal_investigation(mo):
    mo.md(
        """
        ## Portal Investigation

        Start in the Azure networking surfaces before changing the checker:

        1. Open the Azure OpenAI and Search resources and inspect whether public network access is disabled.
        2. Review Private Endpoint connections and confirm they still map to the expected subnet and private DNS zone.
        3. Use Network Watcher or the portal networking view to see whether the endpoint can still be reached publicly.
        4. Compare the live Azure answer to what the Day 12 static artifact currently claims.
        """
    )
    return


@app.cell
def _lab_intro(mo):
    mo.md(
        """
        ## Lab Repair

        Use the notebook to exercise the static-policy checker with a minimal ARM
        template. The real repair still belongs in the production network code.
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
def _lab_preview(BicepPolicyChecker, json, mo):
    checker = BicepPolicyChecker(infra_root=__import__("pathlib").Path("."))
    checked, violations = checker._check_arm_template(  # noqa: SLF001 - training preview only
        {
            "resources": [
                {
                    "type": "Microsoft.CognitiveServices/accounts",
                    "name": "incident-openai",
                    "properties": {"publicNetworkAccess": "Enabled"},
                }
            ]
        },
        "incident_preview.bicep",
    )
    preview = {
        "resources_checked": checked,
        "violations": [
            {
                "resource": violation.resource,
                "type": violation.resource_type,
                "violation": violation.violation,
            }
            for violation in violations
        ],
    }
    mo.callout(
        mo.md(
            f"""
            Static network-policy preview:

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

        Save `build/day12/kql_evidence.json` before you patch production code.

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

        Treat the network portal evidence and notebook checker output as one private-only contract.

        - Portal state: private endpoint, DNS, or public-network posture evidence disagrees with the gate package.
        - Notebook proof: the static policy checker preview shows whether the bug lives in property inspection or live posture proof.
        - Permanent repo change: `src/aegisap/network/bicep_policy_checker.py`, `src/aegisap/network/private_endpoint_probe.py`, and, if needed, the Day 12 verification scripts.

        Rosetta Stone: `notebooks/bridges/day12_private_networking.md`
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

        Move into the real network boundary and implement the repair in:

        - `src/aegisap/network/bicep_policy_checker.py`
        - `src/aegisap/network/private_endpoint_probe.py` if the live posture path is also wrong
        - `scripts/check_private_network_static.py` or `scripts/verify_private_network_posture.py` only if the artifact contract is wrong

        Then update the Day 12 evidence:

        - `docs/curriculum/artifacts/day12/NETWORK_DEPENDENCY_REGISTER.md`
        - `docs/curriculum/artifacts/day12/SECURITY_EXCEPTION_REQUEST.md`
        - `docs/curriculum/artifacts/day12/EGRESS_CONTROL_POLICY.md`

        ### Export to Production

        - Which portal or Network Watcher signal proved the drift?
        - Which checker or probe file makes the private-only rule permanent?
        - Which verification proves static and live posture agree again?
        """
    )
    return


@app.cell
def _verification(repo_root, mo):
    posture_path = repo_root / "build" / "day12" / "private_network_posture.json"
    static_path = repo_root / "build" / "day12" / "static_bicep_analysis.json"
    native_path = repo_root / "build" / "day12" / "native_operator_evidence.json"
    notes = []
    for path in (static_path, posture_path, native_path):
        if path.exists():
            notes.append(f"Current artifact present: `{path.relative_to(repo_root)}`")
        else:
            notes.append(f"Artifact missing: `{path.relative_to(repo_root)}`")
    mo.md(
        f"""
        ## Verification

        Run these commands in the terminal:

        ```bash
        uv run python -m pytest tests/day12/test_network_posture.py tests/day12/test_bicep_policy_checker.py -q
        uv run aegisap-lab artifact rebuild --day 12
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

        Save your raw private-network proof in `build/day12/native_operator_evidence.json`.

        Allowed tools during this gate:

        - Azure Portal
        - `az`
        - `az rest`
        - `nslookup` or `Resolve-DnsName`
        - `curl`
        - raw KQL when you need to prove the request path
        - `git`

        Tools banned during this gate:

        - `aegisap-lab`
        - helper verification wrappers
        - canned answer keys

        Day 12 does not pass until the facilitator selects one saved proof and you rerun it live on screen.
        """
    )
    return


@app.cell
def _chaos_gate(mo):
    mo.md(
        """
        ## Chaos Gate

        Failure signal: Private endpoint DNS or routing drift makes a production-bound service resolve publicly or appear publicly reachable.

        Diagnostic surface: Network Watcher evidence, private endpoint probe cells, and live audit-production DNS posture checks.

        Expected recovery artifact: `build/day12/private_network_posture.json`

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
