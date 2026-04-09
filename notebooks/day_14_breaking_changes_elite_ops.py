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
        # Day 14 - Elite Operations, Breaking Changes, and Executive Incident Leadership

        Primary learner entrypoint: `modules/day_14_elite_ops/README.md`. Read the customer context and file manifest there before you start the incident.

        Day 14 starts in the war room: the trace gate can show green even when
        the private-network deployment is missing the second sink required for
        executive-grade incident evidence. Your job is to prove the false-green
        path, repair the elite-operations gate, and then produce the chaos and
        executive artifacts that would let a CTO trust the response.
        """
    )
    return


@app.cell
def _rubric_helper(repo_root):
    import sys

    notebooks_root = repo_root / "notebooks"
    text = str(notebooks_root)
    if text not in sys.path:
        sys.path.insert(0, text)

    from _shared.curriculum_scaffolds import render_daily_rubric_callout

    return (render_daily_rubric_callout,)


@app.cell
def _rubric_surface(mo, render_daily_rubric_callout, repo_root):
    render_daily_rubric_callout(mo, day="14", repo_root=repo_root)
    return


@app.cell
def _incident(mo):
    mo.md(
        """
        ## Incident

        The candidate release is under pressure, but the trace gate is no longer
        enforcing the dual-sink requirement that Day 12 private networking made
        mandatory.

        **What success looks like**

        - missing dual-sink evidence forces the Day 14 gate red again
        - the rollback and canary evidence still survive the repair
        - the chaos capstone records MTTR and the executive packet tells a coherent incident story
        """
    )
    return


@app.cell
def _portal_investigation(mo):
    mo.md(
        """
        ## Portal Investigation

        Start from live operations evidence before touching the gate:

        1. Inspect the candidate revision, rollout status, and any canary or rollback markers in Azure.
        2. Compare Application Insights evidence to the expected second sink or workspace evidence.
        3. Verify whether the environment is on the private-network path that should require dual-sink trace proof.
        4. Capture the exact mismatch between real operator evidence and the Day 14 gate decision.
        """
    )
    return


@app.cell
def _lab_intro(mo):
    mo.md(
        """
        ## Lab Repair

        Use the notebook to reason about the trace gate with controlled inputs.
        The real repair still belongs in the production release and trace code.
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
        "private_network_all_passed": True,
        "dual_sink_ok": False,
        "uncorrelated": 0,
    }
    preview["should_pass"] = (
        preview["uncorrelated"] == 0 and not preview["private_network_all_passed"] or preview["dual_sink_ok"]
    )
    mo.callout(
        mo.md(
            f"""
            Day 14 gate preview:

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

        Save `build/day14/kql_evidence.json` before you patch production code.

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

        Treat the war-room evidence and notebook gate logic as one executive-control path.

        - Portal state: canary, rollback, or second-sink evidence disagrees with the Day 14 gate.
        - Notebook proof: the gate preview shows the false-green condition for private-network deployments.
        - Durable repo boundary: the staged incident owner for network recovery first, identity recovery second, and correlation or canary truth third.

        Rosetta Stone: `notebooks/bridges/day14_elite_operations.md`
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

        Move into the real elite-operations boundary and identify the durable owner of:

        - stage 1 network recovery that restores private connectivity
        - stage 2 identity recovery that restores actor-bound approvals
        - stage 3 canary and correlation truth before rollback or release decisions

        Then update the Day 14 evidence:

        - `docs/curriculum/artifacts/day14/INCIDENT_COMMAND_PLAYBOOK.md`
        - `docs/curriculum/artifacts/day14/EXECUTIVE_INCIDENT_BRIEF.md`
        - `docs/curriculum/artifacts/day14/ELITE_READINESS_SCORECARD.md`

        ### Export to Production

        - Which operator signal contradicted the gate?
        - Which file permanently blocks the false-green elite-ops decision?
        - Which verification proves the chaos and executive artifacts still tell the same story?
        """
    )
    return


@app.cell
def _verification(repo_root, mo):
    cto_path = repo_root / "build" / "day14" / "cto_trace_report.json"
    drill_path = repo_root / "build" / "day14" / "breaking_changes_drills.json"
    native_path = repo_root / "build" / "day14" / "native_operator_evidence.json"
    notes = []
    for path in (drill_path, cto_path, native_path):
        if path.exists():
            notes.append(f"Current artifact present: `{path.relative_to(repo_root)}`")
        else:
            notes.append(f"Artifact missing: `{path.relative_to(repo_root)}`")
    mo.md(
        f"""
        ## Verification

        Run these commands in the terminal:

        ```bash
        uv run python -m pytest tests/day14/test_breaking_changes.py -q
        uv run python scripts/run_chaos_capstone.py
        uv run aegisap-lab artifact rebuild --day 14
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

        Save your raw canary, rollback, and correlation proof in `build/day14/native_operator_evidence.json`.

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

        The capstone CAB chair may randomly select one saved proof and require a live rerun before final approval.
        """
    )
    return


@app.cell
def _chaos_gate(mo):
    mo.md(
        """
        ## Chaos Gate

        Failure signal: A breaking change brings down the orchestration path and the team must restore service without losing correlation or rollback readiness.

        Starting signal: Customers report that nothing is processing; clear the network fault first, then the identity fault, then the canary and correlation fault.

        Expected recovery artifact: `build/day14/cto_trace_report.json`

        Time box: 35 minutes. If you miss it, stop and rerun the four pillars in `docs/curriculum/FDE_DEBUGGING_FRAMEWORK.md`.
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
