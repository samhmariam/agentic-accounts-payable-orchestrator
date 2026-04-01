# Day 10 — Deployment Gates & Production Release
# ================================================
# All prior day gates surface in a single tabbed dashboard.
# A green envelope JSON is the artefact that unlocks the Container App
# traffic shift to 100 %.
# 
# Run:
#     marimo edit notebooks/day10_deployment_gates.py

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
    mo.md(
        """
        # Day 10 — Deployment Gates & Production Release

        **What you will learn**:
        - How to compose the implemented Day 10 gates into a single release envelope
        - How the shared `aegisap.deploy.gates` module and `scripts/check_all_gates.py` stay aligned
        - How to perform a controlled Azure Container Apps traffic shift
        - How to capture the final immutable release artifact

        > All Days 0–9 must have produced their build artifacts before running this notebook.
        """
    )


@app.cell
def _lab_contract(mo):
    from _shared.lab_guide import render_lab_overview

    render_lab_overview(
        mo,
        prerequisites=[
            "Days 0-9 artifacts are present under `build/`.",
            "Container App deployment environment variables are loaded if you want live ACA health checks.",
        ],
        required_inputs=[
            "`build/day6/golden_thread_day6.json`",
            "`build/day8/regression_baseline.json`",
            "`build/day9/routing_report.json`",
        ],
        required_env_vars=[
            "AZURE_SUBSCRIPTION_ID",
            "AZURE_RESOURCE_GROUP",
            "AZURE_CONTAINER_APP_NAME",
        ],
        expected_artifact="build/day10/release_envelope.json",
        pass_criteria=[
            "The notebook shows PASS/FAIL for `security_posture`, `eval_regression`, `budget`, `refusal_safety`, `resume_safety`, and `aca_health`.",
            "A release envelope is written to `build/day10/release_envelope.json`.",
            "If traffic shifting is attempted, the notebook reports the latest revision or an exact recovery action.",
        ],
        implementation_exercise=(
            "Mandatory checkpoint: extend the training release rehearsal with a checkpoint gate, "
            "recover a failing release path, and prepare the capstone review packet."
        ),
    )


@app.cell
def _run_trigger(mo):
    run_btn = mo.ui.run_button(label="Run all gates")
    mo.vstack([mo.md("## Click to run all gates"), run_btn])
    return (run_btn,)


@app.cell
def _gate_results(mo, run_btn):
    from aegisap.deploy.gates import GateResult, run_all_gates

    mo.stop(not run_btn.value, mo.md(
        "Press **Run all gates** above to start."))

    results: list[GateResult] = run_all_gates(skip_deploy=True)
    return (results,)


@app.cell
def _summary_tiles(mo, results):
    passed = [r for r in results if r.passed]
    failed = [r for r in results if not r.passed]
    all_ok = len(failed) == 0
    kind = "success" if all_ok else "danger"
    mo.vstack([
        mo.md("## Gate Summary"),
        mo.hstack([
            mo.stat(label="Gates passed", value=str(len(passed))),
            mo.stat(label="Gates failed", value=str(len(failed))),
            mo.stat(label="Overall", value="PASS" if all_ok else "FAIL"),
        ]),
        mo.callout(
            mo.md("All gates passed — ready to deploy." if all_ok
                  else f"**{len(failed)} gate(s) failed.** Review tabs below."),
            kind=kind,
        ),
    ])
    return (all_ok,)


@app.cell
def _gate_tabs(mo, results):
    def _row(r) -> dict:
        return {
            "gate": r.name,
            "status": "PASS" if r.passed else "FAIL",
            "detail": r.detail,
        }

    all_rows = [_row(r) for r in results]
    security_r = next(
        (r for r in results if r.name == "security_posture"), None)
    eval_r = next((r for r in results if r.name == "eval_regression"), None)
    budget_r = next((r for r in results if r.name == "budget"), None)
    refusal_r = next((r for r in results if r.name == "refusal_safety"), None)
    resume_r = next((r for r in results if r.name == "resume_safety"), None)
    aca_r = next((r for r in results if r.name == "aca_health"), None)

    def _detail_cell(r) -> mo.Html:
        if r is None:
            return mo.md("Not available.")
        kind = "success" if r.passed else "danger"
        return mo.callout(mo.md(r.detail), kind=kind)

    mo.tabs({
        "All Gates": mo.table(all_rows, selection=None),
        "Security": _detail_cell(security_r),
        "Eval Regression": _detail_cell(eval_r),
        "Budget": _detail_cell(budget_r),
        "Refusal Safety": _detail_cell(refusal_r),
        "Resume Safety": _detail_cell(resume_r),
        "ACA Health": _detail_cell(aca_r),
    })


@app.cell
def _traffic_shift(mo, all_ok):
    shift_btn = mo.ui.run_button(label="Shift 100% traffic to latest revision")
    mo.vstack([
        mo.md("## Traffic Shift"),
        mo.callout(
            mo.md("All gates must pass before shifting traffic."),
            kind="warn" if not all_ok else "neutral",
        ) if not all_ok else mo.md("Gates are green. Ready to shift."),
        shift_btn if all_ok else mo.md(
            "_Traffic shift disabled — fix failing gates first._"),
    ])
    return (shift_btn,)


@app.cell
def _do_traffic_shift(mo, shift_btn, all_ok):
    mo.stop(not (all_ok and shift_btn.value))

    try:
        from aegisap.deploy.aca_client import AcaClient

        client = AcaClient.from_env()
        health = client.health_check()
        response = client.set_traffic(
            active_revision=health.latest_revision, weight=100)
        _out = mo.callout(
            mo.md(
                f"Traffic shifted to **{health.latest_revision}** (100%).\n\n"
                f"Provision state: {health.provision_state}"
            ),
            kind="success",
        )
    except KeyError as exc:
        _out = mo.callout(
            mo.md(
                f"Missing environment variable: `{exc}`.\n\n"
                "Set `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, and "
                "`AZURE_CONTAINER_APP_NAME` to enable live traffic shifting."
            ),
            kind="warn",
        )
    except Exception as exc:
        _out = mo.callout(mo.md(f"Traffic shift failed: {exc}"), kind="danger")
    _out


@app.cell
def _persist(mo, results, all_ok):
    import json as _j
    from pathlib import Path as _Path
    from aegisap.deploy.gates import build_release_envelope
    _repo_root = _Path(__file__).resolve().parents[1]

    out_dir = _repo_root / "build" / "day10"
    out_dir.mkdir(parents=True, exist_ok=True)

    envelope = build_release_envelope(results)
    out_path = out_dir / "release_envelope.json"
    out_path.write_text(_j.dumps(envelope, indent=2))

    mo.vstack([
        mo.callout(mo.md(
            "Artifact written to `build/day10/release_envelope.json`"), kind="success"),
        mo.download(
            data=_j.dumps(envelope, indent=2).encode(),
            filename="release_envelope.json",
            mimetype="application/json",
            label="Download release_envelope.json",
        ),
    ])


@app.cell
def _checkpoint_prompt(mo):
    run_btn = mo.ui.button(label="Generate Day 10 checkpoint artifact", kind="warn")
    mo.vstack([
        mo.md("## 4 — Training Gate Extension"),
        mo.md(
            "This training-only checkpoint verifies that the Day 4 and Day 8 checkpoint artifacts "
            "are wired into the release rehearsal before capstone review."
        ),
        run_btn,
    ])
    return (run_btn,)


@app.cell
def _checkpoint_artifact(mo, run_btn, results):
    mo.stop(not run_btn.value)
    from aegisap.training.checkpoints import run_day10_gate_extension_checkpoint

    artifact_path, payload, release_path, _release_envelope = run_day10_gate_extension_checkpoint(
        base_results=results,
    )
    mo.vstack([
        mo.callout(
            mo.md(
                f"Checkpoint artifact written to `{artifact_path.relative_to(artifact_path.parents[2])}`.\n\n"
                f"Release envelope refreshed at `{release_path.relative_to(release_path.parents[2])}`."
            ),
            kind="success",
        ),
        mo.tree(payload),
    ])


@app.cell
def _capstone_prompt(mo):
    mo.vstack([
        mo.md("## 5 — Capstone Review Packet"),
        mo.callout(
            mo.md(
                "Build the release packet with:\n\n"
                "```bash\n"
                "uv run python scripts/build_capstone_release_packet.py \\\n"
                "  --trainee-id <your-id> \\\n"
                "  --enhancement-category observability_or_policy \\\n"
                "  --checkpoint-artifact build/day4/checkpoint_policy_overlay.json \\\n"
                "  --checkpoint-artifact build/day8/checkpoint_trace_extension.json \\\n"
                "  --checkpoint-artifact build/day10/checkpoint_gate_extension.json \\\n"
                "  --rollback-command \"uv run python scripts/check_all_gates.py --skip-deploy --out build/day10/release_envelope.json\" \\\n"
                "  --summary \"Describe the bounded enhancement, tests, and release evidence.\"\n"
                "```"
            ),
            kind="warn",
        ),
    ])


@app.cell
def _ready_for_next_day(mo):
    from _shared.lab_guide import render_readiness_check

    render_readiness_check(
        mo,
        artifact_relpath="build/day10/release_envelope.json",
        next_day="the production release rehearsal or capstone review",
        recovery_command="uv run python scripts/check_all_gates.py --skip-deploy --out build/day10/release_envelope.json",
    )


if __name__ == "__main__":
    app.run()
