# Day 8 — Observability, Tracing & Regression
# =============================================
# Wire OpenTelemetry spans to Application Insights, explore the KQL dashboards,
# run the eval suite in-process, and verify that all scores are above threshold.
# 
# Run:
#     marimo edit notebooks/day8_observability.py

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
    # Day 8 — Observability, Tracing & Regression

    **What you will learn**:
    - How `azure-monitor-opentelemetry` exports spans to Application Insights
    - What a `node_span` looks like in the Distributed Tracing blade
    - How the three KQL queries in `infra/monitoring/kql/` expose failures, latency, and retries
    - How to capture a regression baseline and detect silent score degradations in CI

    > Prerequisite: Days 1–6 completed.  `APPLICATIONINSIGHTS_CONNECTION_STRING` set for live tracing.
    """)
    return


@app.cell
def _lab_contract(mo):
    from _shared.lab_guide import render_lab_overview

    render_lab_overview(
        mo,
        prerequisites=[
            "Days 1-6 artifacts are available so you can generate or inspect traces.",
            "Day 7 produced `build/day7/security_posture.json`.",
            "App Insights is configured if you want live Azure Monitor export.",
        ],
        required_inputs=[
            "A valid evaluation baseline path under `build/day8/` or a willingness to create one.",
        ],
        required_env_vars=[
            "APPLICATIONINSIGHTS_CONNECTION_STRING",
        ],
        expected_artifact="build/day8/regression_baseline.json",
        pass_criteria=[
            "The notebook runs the eval suite and compares it to the stored threshold/baseline.",
            "A regression baseline is saved to `build/day8/regression_baseline.json`.",
            "You can explain which metrics would block a Day 10 release.",
        ],
        implementation_exercise=(
            "Mandatory checkpoint: instrument a trace extension and emit "
            "`build/day8/checkpoint_trace_extension.json`."
        ),
    )
    return


@app.cell
def _ensure_observability_env(mo):
    import os as _os

    from _shared.lab_guide import load_day0_environment

    loaded_env, state_path = load_day0_environment(track="full")
    conn_str = _os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING", "").strip()

    if conn_str:
        message = (
            f"Loaded observability environment from `.day0/{state_path.stem}.json` for this Marimo session."
            if loaded_env and state_path is not None
            else "Application Insights connection string already present in this session."
        )
        mo.callout(mo.md(message), kind="success")
    else:
        state_hint = (
            f"Attempted to load `.day0/{state_path.stem}.json`, but `APPLICATIONINSIGHTS_CONNECTION_STRING` was still missing.\n\n"
            if state_path is not None
            else "No `.day0/full.json` state file was found for automatic bootstrap.\n\n"
        )
        mo.callout(
            mo.md(
                "Live Azure Monitor export is not configured for this session.\n\n"
                f"{state_hint}"
                "Recovery command:\n\n"
                "```bash\n"
                "source scripts/setup-env.sh full\n"
                "# or export APPLICATIONINSIGHTS_CONNECTION_STRING='<your-connection-string>'\n"
                "```"
            ),
            kind="warn",
        )
    return


@app.cell
def _otel_status(mo):
    def _():
        import os as _os
        conn_str = _os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING", "")
        if conn_str:
            try:
                from azure.monitor.opentelemetry import configure_azure_monitor  # type: ignore
                configure_azure_monitor(connection_string=conn_str)
                _out = mo.callout(
                    mo.md("Azure Monitor OTel exporter configured."), kind="success")
            except Exception as exc:  # noqa: BLE001
                _out = mo.callout(
                    mo.md(f"OTel config failed: `{str(exc)[:100]}`"), kind="warn")
        else:
            _out = mo.callout(
                mo.md(
                    "APPLICATIONINSIGHTS_CONNECTION_STRING not set — spans will go to console only."),
                kind="warn",
            )
        return _out


    _()
    return


@app.cell
def _kql_viewer(mo):
    from pathlib import Path as _Path
    _repo_root = _Path(__file__).resolve().parents[1]
    kql_dir = _repo_root / "infra" / "monitoring" / "kql"
    kql_files = sorted(kql_dir.glob("*.kql")) if kql_dir.exists() else []

    if not kql_files:
        _out = mo.callout(
            mo.md("No KQL files found in `infra/monitoring/kql/`."), kind="warn")
    else:
        tabs = {
            f.stem: mo.vstack([
                mo.md(f"### `{f.name}`"),
                mo.md(f"```sql\n{f.read_text()}\n```"),
                mo.callout(
                    mo.md(
                        "Run this query in **Azure Portal → Log Analytics → Logs** to see live results."),
                    kind="neutral" if hasattr(
                        mo.callout, "neutral") else "info",
                ),
            ])
            for f in kql_files
        }
        _out = mo.vstack([
            mo.md("## 2 — KQL Queries"),
            mo.tabs(tabs),
        ])
    _out
    return


@app.cell
def _run_evals(mo):
    run_evals = mo.ui.button(label="Run Eval Suite", kind="success")
    mo.vstack([
        mo.md("## 3 — Eval Suite"),
        mo.md("Click to run the full eval suite in-process against fixture cases."),
        run_evals,
    ])
    return (run_evals,)


@app.cell
def _eval_results(mo, run_evals):
    import subprocess as _sub
    import json as _j
    import sys as _sys
    from pathlib import Path as _Path

    eval_scores: dict[str, float] = {}

    if not run_evals.value:
        _out = mo.callout(
            mo.md("Click **Run Eval Suite** to execute the regression checks."),
            kind="info",
        )
    else:
        _repo_root = _Path(__file__).resolve().parents[1]
        result = _sub.run(
            [_sys.executable, "-m", "pytest", "evals/", "-q", "--tb=no", "--json-report",
             "--json-report-file=/tmp/eval_report.json"],
            capture_output=True,
            text=True,
            cwd=str(_repo_root),
        )

        report_path = _Path("/tmp/eval_report.json")
        if report_path.exists():
            report = _j.loads(report_path.read_text())
            total = report.get("summary", {}).get("total", 0)
            passed = report.get("summary", {}).get("passed", 0)
            eval_scores["test_pass_rate"] = round(passed / max(total, 1), 4)

        _out = mo.vstack([
            mo.md(f"```bash\n{result.stdout[-2000:] or '(no output)'}\n```"),
            mo.stat(label="Exit code", value=str(result.returncode)),
            mo.stat(label="Scores captured", value=str(len(eval_scores))),
        ])

    _out
    return (eval_scores,)


@app.cell
def _regression_check(eval_scores: dict[str, float], mo):
    from aegisap.observability.baseline import compare_to_baseline
    from pathlib import Path as _Path

    if not eval_scores:
        _out = mo.vstack([
            mo.md("## 4 — Regression Check"),
            mo.callout(
                mo.md("Run the eval suite above to compare current results against the baseline."),
                kind="info",
            ),
        ])
    else:
        _repo_root = _Path(__file__).resolve().parents[1]

        import yaml as _yaml
        thresholds_path = _repo_root / "evals" / "score_thresholds.yaml"
        thresholds = _yaml.safe_load(
            thresholds_path.read_text()) if thresholds_path.exists() else {}

        deltas = compare_to_baseline(eval_scores)

        if deltas:
            delta_rows = [
                {
                    "Metric": d.metric,
                    "Current": d.current_value,
                    "Threshold": d.threshold,
                    "Direction": d.direction,
                }
                for d in deltas
            ]
            _out = mo.vstack([
                mo.md("## 4 — Regression Check"),
                mo.callout(
                    mo.md(f"**{len(deltas)} metric(s) below threshold.**"), kind="danger"),
                mo.table(delta_rows, selection=None),
            ])
        else:
            _out = mo.vstack([
                mo.md("## 4 — Regression Check"),
                mo.callout(
                    mo.md("All metrics meet or exceed thresholds."), kind="success"),
                mo.tree(thresholds),
            ])

    _out
    return


@app.cell
def _capture_baseline_cell(eval_scores: dict[str, float], mo):
    save_btn = mo.ui.button(label="Save as New Baseline", kind="warn")
    guidance = (
        mo.md("Click to overwrite the stored baseline with current scores.")
        if eval_scores
        else mo.callout(
            mo.md("Run the eval suite first to enable baseline capture."),
            kind="info",
        )
    )
    mo.vstack([
        mo.md("## 5 — Baseline Management"),
        guidance,
        save_btn,
    ])
    return (save_btn,)


@app.cell
def _do_save_baseline(eval_scores: dict[str, float], mo, save_btn):
    if eval_scores and save_btn.value:
        from aegisap.observability.baseline import capture_baseline

        capture_baseline(eval_scores)
        _out = mo.callout(
            mo.md("Baseline saved to `build/day8/regression_baseline.json`."),
            kind="success",
        )
    else:
        _out = mo.md("")

    _out
    return


@app.cell
def _persist(eval_scores: dict[str, float], mo):
    import json as _j
    from pathlib import Path as _P

    out_dir = _P(__file__).resolve().parents[1] / "build" / "day8"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "regression_baseline.json"
    if eval_scores:
        out_path.write_text(_j.dumps(eval_scores, indent=2))
        _out = mo.callout(mo.md(
            "Artifact written to `build/day8/regression_baseline.json`"), kind="success")
    else:
        _out = mo.md("Run the eval suite above to generate an artifact.")
    _out
    return


@app.cell
def _checkpoint_prompt(mo):
    save_btn = mo.ui.button(label="Generate Day 8 checkpoint artifact", kind="warn")
    mo.vstack([
        mo.md("## 6 — Mandatory Checkpoint"),
        mo.md(
            "Record the training-only trace extension contract and the KQL query that proves "
            "the new span metadata is visible in Azure Monitor."
        ),
        save_btn,
    ])
    return (save_btn,)


@app.cell
def _checkpoint_artifact(mo, save_btn):
    if save_btn.value:
        from aegisap.training.checkpoints import run_day8_trace_extension_checkpoint

        artifact_path, payload = run_day8_trace_extension_checkpoint()
        _out = mo.vstack([
            mo.callout(
                mo.md(f"Checkpoint artifact written to `{artifact_path.relative_to(artifact_path.parents[2])}`"),
                kind="success",
            ),
            mo.tree(payload),
        ])
    else:
        _out = mo.md("")

    _out
    return


@app.cell
def _ready_for_next_day(mo):
    from _shared.lab_guide import render_readiness_check

    render_readiness_check(
        mo,
        artifact_relpath="build/day8/regression_baseline.json",
        next_day="Day 9 and Day 10",
        recovery_command="marimo edit notebooks/day8_observability.py",
    )
    return


if __name__ == "__main__":
    app.run()
