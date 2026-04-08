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

    from aegisap.deploy.gates import GateResult, build_release_envelope

    return GateResult, build_release_envelope, json, mo, repo_root


@app.cell
def _title(mo):
    mo.md(
        """
        # Day 10 — Release Board Rescue Mission

        Day 10 starts with a go/no-go failure: the release envelope can show green
        even when a critical gate is still red. Your job is to prove the false-green
        path, repair the release aggregation logic, and defend why operator pressure
        cannot override missing evidence.
        """
    )
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
def _production_patch(mo):
    mo.md(
        """
        ## Production Patch

        This section is **markdown-only**.

        Do not edit repo files from this notebook.

        Move into the real release boundary and implement the repair in:

        - `src/aegisap/deploy/gates.py`
        - `scripts/check_all_gates.py`
        - `src/aegisap/training/checkpoints.py` only if the checkpoint packaging is wrong

        Then update the written Day 10 evidence:

        - `docs/curriculum/artifacts/day10/CAB_PACKET.md`
        - `docs/curriculum/artifacts/day10/EXECUTIVE_RELEASE_BRIEF.md`
        - `docs/curriculum/artifacts/day10/GATE_EXCEPTION_POLICY.md`
        """
    )
    return


@app.cell
def _verification(repo_root, mo):
    artifact_path = repo_root / "build" / "day10" / "release_envelope.json"
    artifact_note = (
        f"Current artifact present: `{artifact_path.relative_to(repo_root)}`"
        if artifact_path.exists()
        else "Artifact missing: rebuild the Day 10 artifact after the repair."
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
        """
    )
    return


@app.cell
def _pr_defense(mo):
    mo.md(
        """
        ## PR Defense

        Your pull request must include:

        - the exact gate combination that incorrectly produced a green release signal
        - why the aggregation bug is a release-authority failure, not just a display bug
        - proof that the repaired envelope still preserves failed-gate evidence for CAB review
        - one sentence on the blast radius of promoting a release because one gate was green
        """
    )
    return


if __name__ == "__main__":
    app.run()
