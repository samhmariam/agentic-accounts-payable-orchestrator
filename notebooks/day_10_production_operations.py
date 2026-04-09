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

    from aegisap.deploy.gates import GateResult, build_release_envelope

    return GateResult, build_release_envelope, json, mo, repo_root


@app.cell
def _title(mo):
    mo.md(
        """
        # Day 10 - Production Acceptance, Release Evidence, and Change Board Readiness

        Primary learner entrypoint: `modules/day_10_production_acceptance/README.md`. Read the customer context and file manifest there before you start the incident.

        Day 10 starts with a go/no-go failure: the release envelope can show green
        even when a critical gate is still red. Your job is to prove the false-green
        path, repair the release aggregation logic, and defend why operator pressure
        cannot override missing evidence.
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
    render_daily_rubric_callout(mo, day="10", repo_root=repo_root)
    return


@app.cell
def _incident(mo):
    mo.md(
        """
        ## Incident

        Change management escalated a release where one gate passed and another failed,
        but the aggregated envelope still looked releasable.

        **What success looks like**

        - any failing gate forces a non-green release envelope
        - the release packet still preserves every gate's evidence and detail
        - the Day 10 CAB material explains why executive pressure does not erase gate failures
        """
    )
    return


@app.cell
def _portal_investigation(mo):
    mo.md(
        """
        ## Portal Investigation

        Start from the live release state before changing the aggregator:

        1. Open Container Apps revisions and confirm whether the candidate revision is actually healthy.
        2. Compare the live runtime state to the gate evidence the release packet claims to summarize.
        3. Identify which gate is failing in Azure or CI, and whether the envelope still reads as releasable.
        4. Capture the exact inconsistency between operator evidence and the generated decision.
        """
    )
    return


@app.cell
def _lab_intro(mo):
    mo.md(
        """
        ## Lab Repair

        Use the notebook to exercise the release-envelope logic with controlled gate
        inputs. The real repair still belongs in the production release code.
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
def _release_preview(GateResult, build_release_envelope, json, mo):
    results = [
        GateResult(name="security_posture", passed=False, detail="forbidden runtime secret detected"),
        GateResult(name="resume_safety", passed=True, detail="No duplicate side effects."),
    ]
    envelope = build_release_envelope(results)
    mo.callout(
        mo.md(
            f"""
            Release-envelope preview:

            ```json
            {json.dumps(envelope, indent=2)}
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

        Save `build/day10/kql_evidence.json` before you patch production code.

        Capture at least one literal Log Analytics query with:

        - capture order
        - captured_before_patch=true
        - workspace
        - first_signal_or_followup
        - correlation or trace reference when available
        - purpose
        - observed excerpt
        - operator interpretation

        The Day 10 CAB board also statically validates the full Days 05-09 native
        and KQL evidence chain before it accepts the release packet.
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

        Treat the live release state and notebook envelope preview as one go or no-go contract.

        - Portal state: the candidate revision or upstream gate is unhealthy even though the envelope looks releasable.
        - Notebook proof: the release-envelope preview shows the false-green aggregation path.
        - Durable repo boundary: the release-decision owner in the gate aggregation or checkpoint packaging boundary that prevents false-green promotion.

        Rosetta Stone: `notebooks/bridges/day10_release_evidence.md`
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

        Move into the real release boundary and identify the durable owner of:

        - gate aggregation for the failing release path
        - release-envelope proof that keeps failed evidence visible
        - checkpoint packaging only if the upstream evidence chain is wrong

        Then update the written Day 10 evidence:

        - `docs/curriculum/artifacts/day10/CAB_PACKET.md`
        - `docs/curriculum/artifacts/day10/EXECUTIVE_RELEASE_BRIEF.md`
        - `docs/curriculum/artifacts/day10/GATE_EXCEPTION_POLICY.md`

        ### Export to Production

        - Which exact gate combination produced the false-green result?
        - Which file now enforces the durable non-green release outcome?
        - Which verification proves failed-gate evidence survives into the rebuilt envelope?
        """
    )
    return


@app.cell
def _verification(repo_root, mo):
    artifact_path = repo_root / "build" / "day10" / "release_envelope.json"
    rollback_path = repo_root / "build" / "day10" / "rollback_rehearsal.json"
    artifact_note = (
        f"Current artifact present: `{artifact_path.relative_to(repo_root)}`"
        if artifact_path.exists()
        else "Artifact missing: rebuild the Day 10 artifact after the repair."
    )
    rollback_note = (
        f"Rollback rehearsal path: `{rollback_path.relative_to(repo_root)}`"
        if rollback_path.exists()
        else f"Rollback rehearsal still required later: `{rollback_path.relative_to(repo_root)}`"
    )
    mo.md(
        f"""
        ## Verification

        Run these commands in the terminal:

        ```bash
        uv run python -m pytest tests/day10/test_deployment_contract.py tests/day10/test_release_security.py tests/day10/test_release_envelope.py tests/training/test_checkpoints.py tests/api/test_app.py -q
        uv run aegisap-lab artifact rebuild --day 10
        ```

        {artifact_note}

        {rollback_note}
        """
    )
    return


@app.cell
def _native_tooling_gate(mo):
    mo.md(
        """
        ## Native Tooling Gate

        Policy source: `docs/curriculum/NATIVE_TOOLING_POLICY.md`

        Save your raw operator proof in `build/day10/native_operator_evidence.json`.
        Append `-o json` to Azure CLI diagnostics so the CAB packet preserves
        machine-readable evidence.

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
def _rollback_rehearsal(mo):
    mo.md(
        """
        ## Rollback Rehearsal

        Save `build/day10/rollback_rehearsal.json` after you exercise the live rollback path.

        Required sequence:

        1. Shift 100% of traffic back to the last-known-good ACA revision with
           `az containerapp ingress traffic set ... -o json`.
        2. Verify the routed revision identity before you discuss any Git revert.
        3. Wait for replica readiness with retry/backoff so a control-plane traffic change is
           not mistaken for a data-plane outage.
        4. Capture `/health/ready` and `/version` proof from the restored revision.

        A Git-only revert does not satisfy this gate.
        """
    )
    return


@app.cell
def _chaos_gate(mo):
    mo.md(
        """
        ## Chaos Gate

        Failure signal: A release gate or evidence packet is incomplete, leaving production acceptance without defensible proof.

        Starting signal: Release evidence looks green even though at least one upstream gate or revision is unhealthy.

        Expected recovery artifact: `build/day10/release_envelope.json`

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
        - CAB evidence artifact: <name the packet, checkpoint, or native Day 9 proof the board will inspect>
        ```

        Open or update a PR targeting `cohort/<your-name>/<day-slug>`, paste the markdown block below into the PR body, and push to trigger `.github/workflows/principal-review.yml` on `opened`, `synchronize`, or `ready_for_review`.

        The Day 10 CAB board will also replay the Day 9 native operator evidence if finance or infra challenges your routing proof, and it now blocks on missing or weak Days 05-09 native and KQL evidence.
        """
    )
    return


if __name__ == "__main__":
    app.run()
