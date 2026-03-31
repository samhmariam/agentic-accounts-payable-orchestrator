"""
Day 1 — Invoice Intake & Canonicalization
==========================================
Pick a fixture (or paste raw invoice text), watch the LLM extract a
structured CanonicalInvoice, and inspect every field diff between the
raw agent output and the validated canonical form.

Run:
    marimo edit notebooks/day1_intake_canonicalization.py
"""

import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _intro(mo):
    mo.md("""
    # Day 1 — Invoice Intake & Canonicalization

    **Golden Thread**: INV-3001 · PO-9001 · Acme Office Supplies · GBP 12,500

    **What you will learn**:
    - How a single GPT-4o tool-call extracts a typed `CanonicalInvoice`
    - How Pydantic validation rejects malformed or ambiguous fields
    - How the `ModelGateway` routes this low-risk task to the *light* model tier
    - What a `TokenUsage` cost footprint looks like per extraction call

    > Prerequisite: Day 0 gate must have passed (`build/day0/env_report.json`).
    """)
    return


@app.cell
def _lab_contract(mo):
    from _shared.lab_guide import render_lab_overview

    render_lab_overview(
        mo,
        prerequisites=[
            "Day 0 gate passed or the Azure environment is already known-good.",
        ],
        required_inputs=[
            "A fixture case or a valid `InvoicePackageInput` JSON payload.",
        ],
        required_env_vars=[
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_VERSION",
            "AZURE_OPENAI_CHAT_DEPLOYMENT",
        ],
        expected_artifact="build/day1/golden_thread_day1.json",
        pass_criteria=[
            "The notebook produces a valid canonical invoice or an explicit rejection.",
            "The artifact `build/day1/golden_thread_day1.json` is written.",
            "You can explain the difference between extraction and validation using the displayed output.",
        ],
        implementation_exercise=(
            "Run a malformed invoice or missing-PO case and prove the notebook produces "
            "a deterministic rejection with the correct reason code."
        ),
    )
    return


@app.cell
def _check_day0(mo):
    import json as _j
    from pathlib import Path as _P
    _report_path = _P(__file__).resolve(
    ).parents[1] / "build" / "day0" / "env_report.json"
    if _report_path.exists():
        _report = _j.loads(_report_path.read_text())
        if not _report.get("gate_passed"):
            mo.stop(True, mo.callout(
                mo.md("Day 0 gate not passed. Run Day 0 first."), kind="danger"))
    else:
        mo.callout(mo.md(
            "Day 0 report not found — continuing anyway (env may be pre-configured)."), kind="warn")
    return


@app.cell
def _ensure_azure_env(mo):
    import os as _os

    from _shared.lab_guide import load_day0_environment

    required_env = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_CHAT_DEPLOYMENT",
    ]
    loaded_env, state_path = load_day0_environment(track="core")
    missing = [name for name in required_env if not _os.environ.get(name, "").strip()]

    if missing:
        state_hint = (
            f"Attempted to load `.day0/{state_path.stem}.json`, but the required values were still missing.\n\n"
            if state_path is not None
            else "No `.day0/core.json` state file was found for automatic bootstrap.\n\n"
        )
        mo.stop(
            True,
            mo.callout(
                mo.md(
                    "Azure OpenAI environment is incomplete for Day 1 extraction.\n\n"
                    f"{state_hint}"
                    f"Missing vars: {', '.join(f'`{name}`' for name in missing)}\n\n"
                    "Recovery command:\n\n"
                    "```bash\n"
                    "source scripts/setup-env.sh core\n"
                    "# PowerShell: . ./scripts/setup-env.ps1 -Track core\n"
                    "```"
                ),
                kind="danger",
            ),
        )

    if loaded_env:
        mo.callout(
            mo.md(
                f"Loaded Azure lab environment from `.day0/{state_path.stem}.json` for this Marimo session."
            ),
            kind="success",
        )
    else:
        mo.callout(
            mo.md("Azure OpenAI environment already present in this session."),
            kind="success",
        )
    return


@app.cell
def _fixture_picker(mo):
    from aegisap.day_01.fixture_loader import list_fixture_cases
    cases = list_fixture_cases()

    fixture_picker = mo.ui.dropdown(
        options=["-- paste below --"] + cases,
        value=cases[0] if cases else "-- paste below --",
        label="Fixture Case",
    )
    raw_text_input = mo.ui.text_area(
        placeholder='{"message_id": "...", "email_subject": "...", ...}',
        label="Or paste raw InvoicePackageInput JSON",
        rows=8,
    )
    mo.vstack([
        mo.md("## 1 — Select Input"),
        fixture_picker,
        mo.md("*— or —*"),
        raw_text_input,
    ])
    return fixture_picker, raw_text_input


@app.cell
def _load_package(fixture_picker, mo, raw_text_input):
    from aegisap.day_01.fixture_loader import load_fixture_package
    from aegisap.day_01.models import InvoicePackageInput

    package = None
    load_error = None
    if fixture_picker.value and fixture_picker.value != "-- paste below --":
        try:
            package = load_fixture_package(fixture_picker.value)
        except Exception as exc:  # noqa: BLE001
            load_error = str(exc)
    elif raw_text_input.value.strip():
        try:
            package = InvoicePackageInput.model_validate_json(
                raw_text_input.value)
        except Exception as exc:  # noqa: BLE001
            load_error = str(exc)

    mo.stop(package is None and not load_error, mo.md(
        "Select a fixture or paste JSON to continue."))
    if load_error:
        mo.stop(True, mo.callout(
            mo.md(f"**Load error**: `{load_error}`"), kind="danger"))

    mo.vstack([
        mo.md("## 2 — Raw Package"),
        mo.tree(package.model_dump(mode="json")),
    ])
    return (package,)


@app.cell
def _extract(mo, package):
    import time as _time
    from aegisap.day_01.agent import extract_candidate

    mo.md("### Extracting... (calling Azure OpenAI)")
    t_start = _time.monotonic()

    # extract_candidate calls ModelGateway internally and returns candidate + ledger entry
    candidate = extract_candidate(package)

    elapsed_ms = int((_time.monotonic() - t_start) * 1000)

    mo.vstack([
        mo.md("## 3 — Raw LLM Output (ExtractedInvoiceCandidate)"),
        mo.tree(candidate.model_dump(mode="json")),
        mo.stat(label="Extraction latency", value=f"{elapsed_ms} ms"),
    ])
    return candidate, elapsed_ms


@app.cell
def _canonicalize(candidate, mo, package):
    from aegisap.day_01.service import  canonicalize_with_candidate
    canon_result = None
    canon_error = None
    try:
        canon_result =  canonicalize_with_candidate(package, candidate)
    except Exception as exc:  # noqa: BLE001
        canon_error = str(exc)

    if canon_error:
        _out = mo.vstack([
            mo.md("## 4 — Canonicalization"),
            mo.callout(
                mo.md(f"**Validation failed**: `{canon_error}`"), kind="danger"),
        ])
    else:
        _out = mo.vstack([
            mo.md("## 4 — CanonicalInvoice"),
            mo.tree(canon_result.model_dump(mode="json")),
            mo.callout(mo.md("Canonicalization **succeeded**."),
                       kind="success"),
        ])
    _out
    return (canon_result,)


@app.cell
def _persist(canon_result, elapsed_ms, mo):
    mo.stop(canon_result is None, mo.md(
        "Canonicalization failed; skipping artifact write."))
    import json as _j
    from pathlib import Path as _P

    out_dir = _P(__file__).resolve().parents[1] / "build" / "day1"
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact = canon_result.model_dump(mode="json")
    artifact["_meta"] = {"extraction_latency_ms": elapsed_ms}
    out_path = out_dir / "golden_thread_day1.json"
    out_path.write_text(_j.dumps(artifact, indent=2))

    mo.vstack([
        mo.md("## 5 — Persist"),
        mo.callout(mo.md(
            "Artifact written to `build/day1/golden_thread_day1.json`"), kind="success"),
        mo.download(
            data=_j.dumps(artifact, indent=2).encode(),
            filename="golden_thread_day1.json",
            mimetype="application/json",
            label="Download golden_thread_day1.json",
        ),
    ])
    return


@app.cell
def _ready_for_next_day(mo):
    from _shared.lab_guide import render_readiness_check

    render_readiness_check(
        mo,
        artifact_relpath="build/day1/golden_thread_day1.json",
        next_day="Day 2",
        recovery_command="marimo edit notebooks/day1_intake_canonicalization.py",
    )
    return


if __name__ == "__main__":
    app.run()
