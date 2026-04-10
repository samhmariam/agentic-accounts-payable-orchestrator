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
    return json, mo, repo_root


@app.cell
def _title(mo):
    mo.md("""
    # Day 00 - Bootstrap Incident, Portal Evidence, and Environment Contract Recovery

    Primary learner entrypoint: `modules/day_00_bootstrap/README.md`. Start the incident first, then use this notebook and the bootstrap doc to recover the Day 0 contract safely.
    """)
    return


@app.cell
def _incident(mo):
    mo.md("""
    ## Incident

    The Day 0 state file no longer matches the selected bootstrap track, so the cohort cannot trust the environment reload path.

    **What success looks like**

    - `setup-env.sh` can reload the chosen track from `.day0/<track>.json`
    - `verify_env.py` proves the Day 0 contract again
    - you can explain which Azure identity and environment facts the state file must carry forward
    """)
    return


@app.cell
def _portal_investigation(mo):
    mo.md("""
    ## Portal Investigation

    Use the portal as evidence, not as the fix:

    1. Confirm the intended subscription, resource group, and region.
    2. Check the Foundry or Azure OpenAI deployment name the track should load.
    3. Confirm the Search endpoint, Blob container, and full-track extras if relevant.
    4. Compare those Azure facts against the state file and the shell-export contract.
    """)
    return


@app.cell
def _lab_intro(mo):
    mo.md("""
    ## Lab Repair

    Treat the notebook as a contract reader. The durable repair belongs in the Day 0 state file and bootstrap scripts, not in Marimo state.
    """)
    return


@app.cell
def _track_input(mo):
    track = mo.ui.dropdown(options=["core", "full"], value="core", label="Bootstrap track")
    track
    return (track,)


@app.cell
def _state_preview(json, mo, repo_root, track):
    state_path = repo_root / ".day0" / f"{track.value}.json"
    if state_path.exists():
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        body = json.dumps(payload, indent=2)
        panel = mo.callout(
            mo.md(
                f"""
                Current Day 0 state preview from `{state_path}`:

                ```json
                {body}
                ```
                """
            ),
            kind="info",
        )
    else:
        panel = mo.callout(
            mo.md(
                f"""
                Day 0 state file is missing:

                ```text
                {state_path}
                ```
                """
            ),
            kind="danger",
        )
    panel
    return


@app.cell
def _codification_bridge(mo):
    mo.md("""
    ## Why This Fails In Prod

    The Day 0 shell contract is still production code. If the state file lies about deployment names, endpoints, or identity scope, every later day inherits a broken foundation.

    ## Codification Bridge

    - Portal state: Azure tells you which deployment names, endpoints, and roles are real.
    - Notebook proof: the state preview shows whether `.day0/<track>.json` still matches the intended track.
    - Durable repo boundary: `scripts/setup-env.sh`, `scripts/verify_env.py`, the Day 0 state file, and the provisioning scripts.

    Rosetta Stone: `notebooks/bridges/day00_bootstrap_contract.md`
    """)
    return


@app.cell
def _production_patch(mo):
    mo.md("""
    ## Production Patch

    This section is **markdown-only**.

    Do not edit repo files from this notebook.

    Use your editor and terminal to repair the Day 0 contract in the real repo surfaces:

    - `.day0/core.json` or `.day0/full.json`
    - `scripts/setup-env.sh`
    - `scripts/provision-core.ps1`
    - `scripts/provision-full.ps1`

    ### Export to Production

    - Which Day 0 value was wrong or missing?
    - Which repo surface makes the bootstrap contract durable again?
    - Which shell command proves the environment can be reloaded repeatably?
    """)
    return


@app.cell
def _verification(mo):
    mo.md("""
    ## Verification

    Run one of these commands after the repair:

    ```bash
    bash -lc "source ./scripts/setup-env.sh core && uv run python scripts/verify_env.py --track core"
    bash -lc "source ./scripts/setup-env.sh full && uv run python scripts/verify_env.py --track full"
    uv run aegisap-lab mastery --day 00 --track core
    uv run aegisap-lab mastery --day 00 --track full
    ```
    """)
    return


@app.cell
def _chaos_gate(mo):
    mo.md("""
    ## Chaos Gate

    Recover the bootstrap contract without skipping the portal evidence chain:

    - first signal: environment reload or verification fails
    - second signal: the Day 0 state file disagrees with Azure truth
    - durable fix: restore the track-specific state and rerun the exact verification path
    """)
    return


@app.cell
def _map_gap(mo):
    mo.md("""
    ## Map the Gap

    - What did the broken state file claim?
    - What did Azure truth say instead?
    - Which script or provisioning path now keeps those two views aligned?
    """)
    return


@app.cell
def _pr_defense(mo):
    mo.md("""
    ## PR Defense

    Be ready to defend:

    - why the bootstrap repair belongs in repo-tracked automation rather than a shell one-liner
    - how the identity model stays keyless
    - what would break first if the state file drifted again
    """)
    return


if __name__ == "__main__":
    app.run()
