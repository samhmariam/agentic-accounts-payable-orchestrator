import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _bootstrap():
    import json
    from pathlib import Path

    import marimo as mo

    repo_root = Path(__file__).resolve().parents[1]
    return json, mo, repo_root


@app.cell
def _title(mo):
    mo.md(
        """
        # Day 14 - Chaos Command Rescue Mission

        Day 14 starts in the war room: the trace gate can show green even when
        the private-network deployment is missing the second sink required for
        executive-grade incident evidence. Your job is to prove the false-green
        path, repair the elite-operations gate, and then produce the chaos and
        executive artifacts that would let a CTO trust the response.
        """
    )
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
def _codification_bridge(mo):
    mo.md(
        """
        ## Codification Bridge

        Treat the war-room evidence and notebook gate logic as one executive-control path.

        - Portal state: canary, rollback, or second-sink evidence disagrees with the Day 14 gate.
        - Notebook proof: the gate preview shows the false-green condition for private-network deployments.
        - Permanent repo change: `src/aegisap/deploy/gates_v2.py`, `src/aegisap/traceability/correlation.py` or `scripts/verify_trace_correlation.py`, and, if needed, `scripts/run_chaos_capstone.py`.

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

        Move into the real elite-operations boundary and implement the repair in:

        - `src/aegisap/deploy/gates_v2.py`
        - `src/aegisap/traceability/correlation.py` or `scripts/verify_trace_correlation.py` if the trace evidence path is wrong
        - `scripts/run_chaos_capstone.py` only if the Day 14 operational outputs are incomplete

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
    notes = []
    for path in (drill_path, cto_path):
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
def _pr_defense(mo):
    mo.md(
        """
        ## PR Defense

        Your pull request must include:

        - the exact false-green condition in the Day 14 gate and why it is operationally dangerous
        - why private-network deployments require stronger trace evidence than the public fallback path
        - proof that the chaos drill and CTO artifacts still tell a coherent rollback and incident story
        - one sentence on the blast radius of continuing service without trustworthy cross-sink evidence
        """
    )
    return


if __name__ == "__main__":
    app.run()
