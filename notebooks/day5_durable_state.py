# Day 5 — Durable State, Pause & Resume
# =======================================
# Run the Day 4 workflow to an approval checkpoint, persist it to PostgreSQL,
# simulate an approval decision, and resume — then verify idempotency via the
# side-effect ledger.
# 
# Run:
#     marimo edit notebooks/day5_durable_state.py

import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _mo_imports():
    import sys as _sys
    from pathlib import Path as _Path
    _root = _Path(__file__).resolve().parents[1]
    for _p in [str(_root / "src"), str(_root / "notebooks")]:
        if _p not in _sys.path:
            _sys.path.insert(0, _p)
    import marimo as mo

    return (mo,)


@app.cell
def _intro(mo):
    mo.md("""
    # Day 5 — Durable State, Pause & Resume

    **What you will learn**:
    - Why long-running workflows need *durable* checkpoints — not in-memory state
    - How `DurableStateStore` persists `workflow_threads`, `workflow_checkpoints`, `approval_tasks`, and `side_effect_ledger`
    - How the approval gate pauses execution and waits for a human decision
    - How resume tokens and the side-effect ledger prevent replay and duplication
    - What the `side_effect_ledger` looks like in the database

    > Prerequisite: `build/day4/golden_thread_day4.json` + PostgreSQL settings loaded for `AEGISAP_POSTGRES_DSN` or Entra-based connection variables.
    """)
    return


@app.cell
def _lab_contract(mo):
    from _shared.lab_guide import render_lab_overview

    render_lab_overview(
        mo,
        prerequisites=[
            "Run `uv run python scripts/run_day4_case.py --planner-mode fixture` if your Day 4 notebook artifact does not contain `workflow_state`.",
            "Apply migrations before opening the notebook.",
        ],
        required_inputs=[
            "`build/day4/golden_thread_day4.json` with a `workflow_state` payload.",
            "PostgreSQL connectivity through `AEGISAP_POSTGRES_DSN` or Entra auth variables.",
        ],
        required_env_vars=[
            "AEGISAP_POSTGRES_DSN or AZURE_POSTGRES_HOST/AZURE_POSTGRES_PORT/AZURE_POSTGRES_DB/AZURE_POSTGRES_USER",
            "AEGISAP_RESUME_TOKEN_SECRET or Azure Key Vault access for the resume token secret",
        ],
        expected_artifact="build/day5/golden_thread_day5_resumed.json",
        pass_criteria=[
            "A Day 5 pause artifact and resumed artifact are written to `build/day5/`.",
            "The checkpoint and approval task tables show the parked thread.",
            "The side-effect ledger shows no duplicate effect keys after resume.",
        ],
        implementation_exercise=(
            "Prove the pause/resume path is safe by identifying the exact recovery command "
            "for a broken resume and the artifact that shows `duplicate_side_effects = 0`."
        ),
    )
    return


@app.cell
def _load_day4(mo):
    import json as _j
    from pathlib import Path as _P
    from aegisap.day4.state.workflow_state import WorkflowState as _Day4WorkflowState

    artifact_path = _P(__file__).resolve(
    ).parents[1] / "build" / "day4" / "golden_thread_day4.json"
    mo.stop(
        not artifact_path.exists(),
        mo.callout(mo.md(
            "Run Day 4 first — `build/day4/golden_thread_day4.json` not found.\n\n"
            "Recovery command:\n\n```bash\nuv run python scripts/run_day4_case.py --planner-mode fixture\n```"), kind="danger"),
    )
    data = _j.loads(artifact_path.read_text())
    workflow_state = data.get("workflow_state")
    mo.stop(
        workflow_state is None,
        mo.callout(
            mo.md(
                "This Day 4 artifact does not contain `workflow_state`, which Day 5 needs.\n\n"
                "Recovery command:\n\n```bash\nuv run python scripts/run_day4_case.py --planner-mode fixture\n```"
            ),
            kind="danger",
        ),
    )
    state = _Day4WorkflowState.model_validate(workflow_state)
    mo.vstack([mo.md("## Day 4 Artifact Loaded"), mo.tree(data)])
    return (state,)


@app.cell
def _db_config(mo):
    import os as _os

    dsn_display = _os.environ.get("AEGISAP_POSTGRES_DSN", "")
    if dsn_display:
        _out = mo.callout(
            mo.md("PostgreSQL DSN configured (`AEGISAP_POSTGRES_DSN` is set)."),
            kind="success",
        )
    elif all(
        _os.environ.get(name, "").strip()
        for name in ["AZURE_POSTGRES_HOST", "AZURE_POSTGRES_PORT", "AZURE_POSTGRES_DB", "AZURE_POSTGRES_USER"]
    ):
        _out = mo.callout(
            mo.md("PostgreSQL Entra-auth settings detected. The notebook will connect without a stored DSN."),
            kind="success",
        )
    else:
        _out = mo.callout(
            mo.md(
                "PostgreSQL settings are incomplete.\n\n"
                "Recovery command:\n\n```bash\nuv run python scripts/verify_env.py --track full --env\n```"
            ),
            kind="warn",
        )
    _out
    return


@app.cell
def _():
    import os
    os.environ["AEGISAP_RESUME_TOKEN_SECRET"] = "dev-only-resume-secret"

    return


@app.cell
def _run_to_pause(mo, state):
    from aegisap.day5.workflow.training_runtime import create_day5_pause
    from aegisap.security.key_vault import get_resume_token_secret
    from aegisap.training.postgres import build_store_from_env

    thread_id = f"thread-{state.case_facts.case_id}"
    pause_result = None
    pause_error = None
    try:
        pause_result = create_day5_pause(
            day4_state=state,
            thread_id=thread_id,
            assigned_to="controller@example.com",
            store=build_store_from_env(),
            token_secret=get_resume_token_secret(),
        )
    except Exception as exc:  # noqa: BLE001
        pause_error = str(exc)

    if pause_error:
        _out = mo.callout(mo.md(f"**Pause error**: `{pause_error}`"), kind="danger")
    else:
        _out = mo.vstack([
            mo.md("## 1 — Workflow Paused"),
            mo.stat(label="Thread ID", value=str(
                pause_result.get("thread_id", "—"))),
            mo.stat(label="Checkpoint ID", value=str(
                pause_result.get("checkpoint_id", "—"))),
            mo.stat(label="Approval Task ID", value=str(
                pause_result.get("approval_task_id", "—"))),
            mo.callout(
                mo.md("Workflow is waiting at approval gate."), kind="success"),
        ])
    _out
    return pause_error, pause_result, thread_id


@app.cell
def _view_checkpoint(mo, pause_error, pause_result, thread_id):
    mo.stop(pause_error is not None or pause_result is None)
    from aegisap.training.postgres import build_connection_factory_from_env

    checkpoint_row = None
    try:
        with build_connection_factory_from_env()() as _conn:
            with _conn.cursor() as _cur:
                _cur.execute(
                    "SELECT checkpoint_id, checkpoint_seq, node_name, state_json, created_at "
                    "FROM workflow_checkpoints WHERE thread_id = %s "
                    "ORDER BY checkpoint_seq DESC LIMIT 1",
                    (thread_id,),
                )
                _row = _cur.fetchone()
                if _row:
                    checkpoint_row = {
                        "checkpoint_id": str(_row[0]),
                        "checkpoint_seq": _row[1],
                        "node_name": _row[2],
                        "state_json": _row[3],
                        "created_at": str(_row[4]),
                    }
    except Exception as exc:  # noqa: BLE001
        checkpoint_row = {"error": str(exc)}

    mo.vstack([
        mo.md("## 2 — Checkpoint in PostgreSQL"),
        mo.tree(checkpoint_row) if checkpoint_row else mo.md(
            "*(no checkpoint found)*"),
    ])
    return


@app.cell
def _pending_approvals(mo, pause_error, thread_id):
    def _():
        mo.stop(pause_error is not None or not thread_id)
        from aegisap.training.postgres import build_connection_factory_from_env

        rows = []
        try:
            with build_connection_factory_from_env()() as _conn:
                with _conn.cursor() as _cur:
                    _cur.execute(
                        "SELECT approval_task_id, status, assigned_to, created_at "
                        "FROM approval_tasks WHERE thread_id = %s",
                        (thread_id,),
                    )
                    for _row in _cur.fetchall():
                        rows.append({
                            "approval_task_id": str(_row[0]),
                            "status": _row[1],
                            "assigned_to": _row[2] or "—",
                            "created_at": str(_row[3]),
                        })
        except Exception as exc:  # noqa: BLE001
            rows = [{"error": str(exc)}]
        return mo.vstack([
            mo.md(f"## 3 — Pending Approvals ({len(rows)})"),
            mo.ui.table(rows, selection=None) if rows else mo.md("*(none)*"),
        ])


    _()
    return


@app.cell
def _approval_decision(mo, pause_error, thread_id):
    def _():
        mo.stop(pause_error is not None or not thread_id)
        from aegisap.training.postgres import build_connection_factory_from_env

        rows = []
        try:
            with build_connection_factory_from_env()() as _conn:
                with _conn.cursor() as _cur:
                    _cur.execute(
                        "SELECT approval_task_id, status, assigned_to, created_at "
                        "FROM approval_tasks WHERE thread_id = %s",
                        (thread_id,),
                    )
                    for _row in _cur.fetchall():
                        rows.append({
                            "approval_task_id": str(_row[0]),
                            "status": _row[1],
                            "assigned_to": _row[2] or "—",
                            "created_at": str(_row[3]),
                        })
        except Exception as exc:  # noqa: BLE001
            rows = [{"error": str(exc)}]

        mo.stop(pause_error is not None or not rows or "error" in (
            rows[0] if rows else {}))
        decision = mo.ui.radio(
            options={"Approve": "approved", "Reject": "rejected"},
            value="Approve",
            label="Approval Decision",
        )
        return mo.vstack([mo.md("## 4 — Simulate Approval Decision"), decision])


    _()
    return


@app.cell
def _resume(decision, mo, pause_error, pause_result):
    def _():
        return mo.stop(pause_error is not None or pause_result is None)
        from aegisap.day5.workflow.training_runtime import resume_day5_case
        from aegisap.security.key_vault import get_resume_token_secret
        from aegisap.training.postgres import build_store_from_env

        resume_result = None
        resume_error = None
        try:
            resume_result = resume_day5_case(
                store=build_store_from_env(),
                token_secret=get_resume_token_secret(),
                resume_token=pause_result["resume_token"],
                decision_payload={"status": decision.value, "comment": "Training decision"},
                resumed_by="controller@example.com",
            )
        except Exception as exc:  # noqa: BLE001
            resume_error = str(exc)

        if resume_error:
            _out = mo.callout(mo.md(f"**Resume error**: `{resume_error}`"), kind="danger")
        else:
            _out = mo.vstack([
                mo.md("## 5 — Workflow Resumed"),
                mo.callout(mo.md(
                    f"Decision: **{decision.value}** applied. Workflow completed."), kind="success"),
                mo.tree(resume_result.model_dump(mode="json") if hasattr(
                    resume_result, "model_dump") else vars(resume_result)),
            ])


    _()
    return


@app.cell
def _idempotency_check(mo, pause_error, pause_result):
    def _():
        mo.stop(pause_error is not None or pause_result is None)
        from aegisap.training.postgres import build_connection_factory_from_env

        _thread_id = pause_result.get("thread_id")
        ledger_rows = []
        try:
            with build_connection_factory_from_env()() as _conn:
                with _conn.cursor() as _cur:
                    _cur.execute(
                        "SELECT effect_key, effect_type, status, created_at "
                        "FROM side_effect_ledger WHERE thread_id = %s",
                        (_thread_id,),
                    )
                    for _row in _cur.fetchall():
                        ledger_rows.append({
                            "effect_key": _row[0],
                            "effect_type": _row[1],
                            "status": _row[2],
                            "created_at": str(_row[3]),
                        })
        except Exception as exc:  # noqa: BLE001
            ledger_rows = [{"error": str(exc)}]

        duplicates = len(ledger_rows) != len(
            {r.get("effect_key") for r in ledger_rows})
        return mo.vstack([
            mo.md("## 6 — Side-Effect Ledger (Idempotency Check)"),
            mo.table(ledger_rows, selection=None) if ledger_rows else mo.md(
                "*(empty)*"),
            mo.callout(
                mo.md("**No duplicates detected — idempotency verified.**"), kind="success")
            if not duplicates
            else mo.callout(mo.md("**DUPLICATE side effects detected!**"), kind="danger"),
        ])


    _()
    return


@app.cell
def _persist(mo, pause_result, resume_error, resume_result):
    mo.stop(resume_error is not None or resume_result is None)
    import json as _j
    from pathlib import Path as _P

    out_dir = _P(__file__).resolve().parents[1] / "build" / "day5"
    out_dir.mkdir(parents=True, exist_ok=True)

    def _to_dict(obj):
        if hasattr(obj, "model_dump"):
            return obj.model_dump(mode="json")
        if isinstance(obj, dict):
            return obj
        if hasattr(obj, "__dict__"):
            return vars(obj)
        return str(obj)

    pause_payload = _to_dict(pause_result)
    resumed_payload = _to_dict(resume_result)
    duplicate_side_effects = 0
    if hasattr(resume_result, "side_effect_records"):
        effect_keys = [record.effect_key for record in resume_result.side_effect_records]
        duplicate_side_effects = len(effect_keys) - len(set(effect_keys))
    resumed_payload["duplicate_side_effects"] = duplicate_side_effects

    for fname, obj in [
        ("golden_thread_day5_pause.json", pause_payload),
        ("golden_thread_day5_resumed.json", resumed_payload),
    ]:
        (out_dir / fname).write_text(_j.dumps(obj, indent=2, default=str))

    mo.callout(mo.md("Artifacts written to `build/day5/`."), kind="success")
    return


@app.cell
def _ready_for_next_day(mo):
    from _shared.lab_guide import render_readiness_check

    render_readiness_check(
        mo,
        artifact_relpath="build/day5/golden_thread_day5_resumed.json",
        next_day="Day 6 or the hosted resume API walkthrough",
        recovery_command="uv run python scripts/run_day5_pause_resume.py && uv run python scripts/resume_day5_case.py",
    )
    return


if __name__ == "__main__":
    app.run()
