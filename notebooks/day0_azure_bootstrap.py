import marimo

__generated_with = "0.20.4"
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
    # Day 0 — Keyless Azure Substrate

    **Objective**: Verify that every required Azure service is reachable using
    `DefaultAzureCredential` only.  No API keys.  No connection strings (except
    Application Insights).

    > Change **Track** below and the probes update automatically.
    """)
    return


@app.cell
def _lab_contract(mo):
    from _shared.lab_guide import render_lab_overview

    render_lab_overview(
        mo,
        prerequisites=[
            "Azure CLI login is complete in the correct tenant and subscription.",
            "The target environment was provisioned from `infra/core.bicep` or `infra/full.bicep`.",
        ],
        required_inputs=[
            "Track selection: `core` or `full`.",
        ],
        required_env_vars=[
            "AZURE_SUBSCRIPTION_ID",
            "AZURE_RESOURCE_GROUP",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_SEARCH_ENDPOINT",
        ],
        expected_artifact="build/day0/env_report.json",
        pass_criteria=[
            "All required probes pass for the selected track.",
            "No forbidden environment variables are detected.",
            "The environment report is written to `build/day0/env_report.json`.",
        ],
        implementation_exercise=(
            "Break one environment probe, restore it with the exact recovery command, "
            "and regenerate `build/day0/env_report.json`."
        ),
    )
    return


@app.cell
def _track_picker(mo):
    track = mo.ui.dropdown(
        options=["core", "full"],
        value="core",
        label="Provisioning Track",
    )
    mo.md(f"**Track** → {track}")
    return (track,)


@app.cell
def _run_probes(track):
    from _shared.azure_probe import run_all_probes, probe_forbidden_env_vars

    results = run_all_probes(track.value)
    forbidden = probe_forbidden_env_vars()
    return forbidden, results


@app.cell
def _display_probes(forbidden, mo, results):
    rows = []
    all_ok = True
    for r in results:
        icon = "✅" if r.ok else "❌"
        rows.append(
            mo.hstack(
                [
                    mo.stat(label=f"{icon} {r.service}",
                            value=f"{r.latency_ms} ms" if r.ok else "FAIL"),
                    mo.md(f"`{r.detail[:80]}`"),
                ],
                justify="start",
                gap=2,
            )
        )
        if not r.ok:
            all_ok = False

    probe_display = mo.vstack(rows)

    if forbidden:
        sec_callout = mo.callout(
            mo.md(
                f"**SECURITY VIOLATION** — forbidden environment variables detected:\n\n"
                + "\n".join(f"- `{v}`" for v in forbidden)
            ),
            kind="danger",
        )
    else:
        sec_callout = mo.callout(
            mo.md("No forbidden environment variables detected."), kind="success")
    return all_ok, probe_display, sec_callout


@app.cell
def _show_probes(mo, probe_display, sec_callout):
    mo.vstack([
        mo.md("## Service Probes"),
        probe_display,
        mo.md("## Security Posture"),
        sec_callout,
    ])
    return


@app.cell
def _gate(all_ok, forbidden, mo):
    mo.stop(
        not all_ok or bool(forbidden),
        mo.callout(
            mo.md(
                "**Day 0 gate not passed.** Fix the issues above before continuing. "
                "Refer to [docs/DAY_00_AZURE_BOOTSTRAP.md](../docs/DAY_00_AZURE_BOOTSTRAP.md)."
            ),
            kind="danger",
        ),
    )
    mo.callout(
        mo.md("**All probes passed.** Ready to proceed to Day 1."), kind="success")
    return


@app.cell
def _persist(forbidden, mo, results, track):
    import json as _json
    from pathlib import Path as _P

    out_dir = _P(__file__).resolve().parents[1] / "build" / "day0"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "track": track.value,
        "probes": [
            {
                "service": r.service,
                "ok": r.ok,
                "latency_ms": r.latency_ms,
                "detail": r.detail,
                "principal": r.principal,
            }
            for r in results
        ],
        "forbidden_env_vars_found": forbidden,
        "gate_passed": all(r.ok for r in results) and not forbidden,
    }
    out_path = out_dir / "env_report.json"
    out_path.write_text(_json.dumps(report, indent=2))

    mo.vstack([
        mo.md(f"Artifact written to `build/day0/env_report.json`"),
        mo.download(
            data=_json.dumps(report, indent=2).encode(),
            filename="env_report.json",
            mimetype="application/json",
            label="Download env_report.json",
        ),
    ])
    return


@app.cell
def _ready_for_next_day(mo):
    from _shared.lab_guide import render_readiness_check

    render_readiness_check(
        mo,
        artifact_relpath="build/day0/env_report.json",
        next_day="Day 1",
        recovery_command="uv run python scripts/verify_env.py --track core",
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
