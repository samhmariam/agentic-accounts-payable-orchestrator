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

    from aegisap.day5.workflow.resume_service import ResumeTokenCodec, ResumeTokenPayload

    return ResumeTokenCodec, ResumeTokenPayload, mo, repo_root


@app.cell
def _title(mo):
    mo.md(
        """
        # Day 5 — Durable State Rescue Mission

        Day 5 is now about a broken resume boundary. A paused approval thread can no
        longer trust that the resume token and checkpoint are still bound together, and
        that is how duplicate or misrouted side effects are born.
        """
    )
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
        workflow implementation directly.
        """
    )
    return


@app.cell
def _binding_controls(mo):
    token_checkpoint = mo.ui.text(value="cp-1", label="Checkpoint ID stored in the resume token")
    approval_checkpoint = mo.ui.text(value="cp-2", label="Checkpoint ID stored on the approval task")
    mo.vstack([token_checkpoint, approval_checkpoint])
    return approval_checkpoint, token_checkpoint


@app.cell
def _binding_preview(ResumeTokenCodec, ResumeTokenPayload, approval_checkpoint, mo, token_checkpoint):
    codec = ResumeTokenCodec("lab-secret")
    token = codec.encode(
        ResumeTokenPayload(
            thread_id="thread-golden-001",
            checkpoint_id=token_checkpoint.value.strip(),
            checkpoint_seq=7,
            approval_task_id="approval-task-1",
        )
    )
    decoded = codec.decode(token)
    checkpoint_match = decoded.checkpoint_id == approval_checkpoint.value.strip()
    panel_kind = "success" if checkpoint_match else "danger"
    mo.callout(
        mo.md(
            f"""
            Resume-token prototype:

            - `encoded_token={token}`
            - `decoded_checkpoint_id={decoded.checkpoint_id}`
            - `approval_task_checkpoint_id={approval_checkpoint.value.strip()}`
            - `resume_allowed={checkpoint_match}`
            """
        ),
        kind=panel_kind,
    )
    return


@app.cell
def _production_patch(mo):
    mo.md(
        """
        ## Production Patch

        This section is **markdown-only**.

        Do not edit repo files from this notebook.

        Implement the repair in the production runtime:

        - `src/aegisap/day5/workflow/resume_service.py`
        - `src/aegisap/day5/workflow/checkpoint_manager.py` if the checkpoint contract also needs tightening

        Then update the governance evidence:

        - `docs/curriculum/artifacts/day05/HUMAN_APPROVAL_CONTRACT.md`
        - `docs/curriculum/artifacts/day05/PAUSE_RESUME_GOVERNANCE.md`
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
def _pr_defense(mo):
    mo.md(
        """
        ## PR Defense

        Your pull request must include:

        - the exact checkpoint-binding invariant the runtime must preserve
        - proof that stale resume material is rejected before side effects execute
        - evidence that idempotent recommendation delivery still deduplicates correctly
        - one sentence on why durable-state bugs are infrastructure bugs, not prompt bugs
        """
    )
    return
