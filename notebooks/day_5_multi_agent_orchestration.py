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

    from _shared.curriculum_scaffolds import deep_reload_modules

    deep_reload_modules("aegisap")

    from aegisap.day5.workflow.resume_service import ResumeTokenCodec, ResumeTokenPayload

    return ResumeTokenCodec, ResumeTokenPayload, mo, repo_root


@app.cell
def _title(mo):
    mo.md(
        """
        # Day 5 - Multi-Agent Orchestration, Durable State, and Resume Safety

        Primary learner entrypoint: `modules/day_05_durable_state/README.md`. Read the customer context and file manifest there before you start the incident.

        Day 5 is now about a broken resume boundary. A paused approval thread can no
        longer trust that the resume token and checkpoint are still bound together, and
        that is how duplicate or misrouted side effects are born.
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
    render_daily_rubric_callout(mo, day="05", repo_root=repo_root)
    return


@app.cell
def _incident(mo):
    mo.md(
        """
        ## Incident

        Runtime safety found a stale resume token path that no longer proves the approval
        task is bound to the original checkpoint.

        **What success looks like**

        - resume tokens stay checkpoint-bound
        - stale or drifted approval tasks are rejected before side effects run
        - the pause/resume governance docs explain the boundary clearly
        """
    )
    return


@app.cell
def _portal_investigation(mo):
    mo.md(
        """
        ## Portal Investigation

        Investigate the state boundary before you patch the resume code:

        1. Inspect the approval task record and capture its checkpoint ID.
        2. Compare it with the checkpoint ID encoded in the resume token or workflow metadata.
        3. Review DLQ or failed-resume traces to see whether the mismatch was detected before execution.
        4. Confirm no duplicate side effect was emitted while the boundary was broken.
        """
    )
    return


@app.cell
def _lab_repair_intro(mo):
    mo.md(
        """
        ## Lab Repair

        Use this notebook to reason about the resume-token contract, not to patch the
        workflow implementation directly. Reduced-scaffold mode is active here:
        inspect the fixed seed values below and then build the terminal or SDK probe
        you actually need in the repo.

        Do not use the shared lab wrapper helpers in this phase.
        Build your own probes with `azure-identity`, the relevant `azure-mgmt-*`
        SDK clients, `az rest`, or raw KQL, then return here only to record evidence.
        """
    )
    return


@app.cell
def _binding_seed():
    approval_checkpoint = "cp-2"
    token_checkpoint = "cp-1"
    return approval_checkpoint, token_checkpoint


@app.cell
def _binding_preview(ResumeTokenCodec, ResumeTokenPayload, approval_checkpoint, mo, token_checkpoint):
    codec = ResumeTokenCodec("lab-secret")
    token = codec.encode(
        ResumeTokenPayload(
            thread_id="thread-golden-001",
            checkpoint_id=token_checkpoint,
            checkpoint_seq=7,
            approval_task_id="approval-task-1",
        )
    )
    decoded = codec.decode(token)
    checkpoint_match = decoded.checkpoint_id == approval_checkpoint
    panel_kind = "success" if checkpoint_match else "danger"
    mo.callout(
        mo.md(
            f"""
            Resume-token prototype:

            - `encoded_token={token}`
            - `decoded_checkpoint_id={decoded.checkpoint_id}`
            - `approval_task_checkpoint_id={approval_checkpoint}`
            - `resume_allowed={checkpoint_match}`
            """
        ),
        kind=panel_kind,
    )
    return


@app.cell
def _codification_bridge(mo):
    mo.md(
        """
        ## Why This Fails In Prod

        List three specific ways this notebook logic fails in an Azure Container App. You must reference at least one Azure limit (memory, timeout, or ephemeral storage) and one concurrency issue.

        ## Codification Bridge

        Treat the task record, token payload, and notebook comparison as one invariant.

        - Portal state: approval-task state and checkpoint state no longer agree.
        - Notebook proof: the resume-token prototype shows whether stale material is being accepted.
        - Permanent repo change: `src/aegisap/day5/workflow/resume_service.py` and, if needed, `src/aegisap/day5/workflow/checkpoint_manager.py`.

        Rosetta Stone: `notebooks/bridges/day05_durable_state.md`
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

        Implement the repair in the production runtime:

        - `src/aegisap/day5/workflow/resume_service.py`
        - `src/aegisap/day5/workflow/checkpoint_manager.py` if the checkpoint contract also needs tightening

        Then update the governance evidence:

        - `docs/curriculum/artifacts/day05/HUMAN_APPROVAL_CONTRACT.md`
        - `docs/curriculum/artifacts/day05/PAUSE_RESUME_GOVERNANCE.md`

        ### Export to Production

        - Which identifier proved the checkpoint-binding mismatch?
        - Which invariant must become permanent in `resume_service.py` or `checkpoint_manager.py`?
        - What verification proves stale resume material is rejected before side effects run?
        """
    )
    return


@app.cell
def _verification(repo_root, mo):
    artifact_path = repo_root / "build" / "day5" / "golden_thread_day5_resumed.json"
    artifact_note = (
        f"Current artifact present: `{artifact_path.relative_to(repo_root)}`"
        if artifact_path.exists()
        else "Artifact missing: rebuild the Day 5 pause and resume artifacts after the repair."
    )
    mo.md(
        f"""
        ## Verification

        Run these commands in the terminal:

        ```bash
        uv run python -m pytest tests/day5/integration/test_resume_service.py tests/day5/integration/test_idempotent_recommendation_resume.py -q
        uv run aegisap-lab artifact rebuild --day 05
        ```

        {artifact_note}
        """
    )
    return


@app.cell
def _kql_evidence(mo):
    mo.md(
        """
        ## KQL Evidence

        Save `build/day5/kql_evidence.json` before you patch production code.

        Capture at least one literal Log Analytics query with:

        - workspace
        - purpose
        - observed excerpt
        - operator interpretation
        """
    )
    return


@app.cell
def _native_tooling_gate(mo):
    mo.md(
        """
        ## Native Tooling Gate

        Policy source: `docs/curriculum/NATIVE_TOOLING_POLICY.md`

        Save your raw operator proof in `build/day5/native_operator_evidence.json`.

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

        Failure signal: The durable workflow stalls or resumes unsafely after interruption, risking duplicate state transitions.

        Diagnostic surface: Cosmos-style thread state, notebook resume prototype, and the resume/checkpoint services.

        Expected recovery artifact: `build/day5/golden_thread_day5_resumed.json`

        Time box: 25 minutes. If you miss it, stop and rerun the four pillars in `docs/curriculum/FDE_DEBUGGING_FRAMEWORK.md`.
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
