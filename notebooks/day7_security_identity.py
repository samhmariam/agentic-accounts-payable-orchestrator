# Day 7 — Security, Managed Identity & Audit
# ============================================
# Verify that the runtime uses `DefaultAzureCredential` only, that no
# API keys are in the environment, that AI Search local auth is disabled,
# and that the PostgreSQL audit log is populated.
# 
# Run:
#     marimo edit notebooks/day7_security_identity.py

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
    # Day 7 — Security, Managed Identity & Audit

    **What you will learn**:
    - Why "no API keys in the environment" is a hard runtime contract, not a guideline
    - How `DefaultAzureCredential` chains through Managed Identity → workload identity → dev CLI
    - How AI Search's `disableLocalAuth: true` makes Bicep your security control plane
    - How PII patterns are redacted *before* they reach OTel spans
    - How the PostgreSQL audit log provides an immutable, query-able decision trail

    > Prerequisite: Day 0 full-track environment provisioned.
    """)
    return


@app.cell
def _lab_contract(mo):
    from _shared.lab_guide import render_lab_overview

    render_lab_overview(
        mo,
        prerequisites=[
            "Day 0 full-track environment is provisioned.",
            "For the full golden thread, Day 6 produced `build/day6/golden_thread_day6.json`.",
            "A Day 5 or Day 6 workflow has emitted audit rows if you want to inspect the audit table.",
        ],
        required_inputs=[
            "A running environment that passes `uv run python scripts/verify_env.py --track full --env`.",
        ],
        required_env_vars=[
            "AZURE_KEY_VAULT_URI",
            "AZURE_SEARCH_ENDPOINT",
            "AZURE_SEARCH_INDEX",
        ],
        expected_artifact="build/day7/security_posture.json",
        pass_criteria=[
            "Security posture checks pass or produce actionable failures.",
            "PII redaction output is visible in the notebook.",
            "The posture report is written to `build/day7/security_posture.json`.",
        ],
        implementation_exercise=(
            "Repair one seeded identity or secret-posture failure and regenerate "
            "`build/day7/security_posture.json` with the corrected evidence."
        ),
    )
    return


@app.cell
def _identity_probe(mo):
    from aegisap.security.posture import run_posture_check

    posture = run_posture_check()
    _rows = [
        {
            "Check": c.name,
            "Status": "✅ PASS" if c.passed else "❌ FAIL",
            "Detail": c.detail[:80],
        }
        for c in posture.checks
    ]
    overall = mo.callout(
        mo.md("**All security checks passed.**"),
        kind="success",
    ) if posture.passed else mo.callout(
        mo.md(f"**{len(posture.failed_checks)} check(s) failed.**"),
        kind="danger",
    )
    mo.vstack([
        mo.md("## 1 — Security Posture Checks"),
        mo.ui.table(_rows, selection=None),
        overall,
    ])
    return (posture,)


@app.cell
def _forbidden_env_detail(mo):
    from aegisap.security.config import FORBIDDEN_ENV_VARS
    import os as _os

    env_rows = [
        {
            "Variable": v,
            "Present": "❌ YES" if _os.environ.get(v, "").strip() else "✅ No",
        }
        for v in sorted(FORBIDDEN_ENV_VARS)
    ]
    mo.vstack([
        mo.md("## 2 — Forbidden Environment Variable Scan"),
        mo.ui.table(env_rows, selection=None),
    ])
    return


@app.cell
def _pii_redaction_lab(mo):
    sample_input = mo.ui.text_area(
        value=(
            "Please process this invoice for John Smith, SSN 123-45-6789, "
            "bank IBAN GB29NWBK60161331926819, email john.smith@acme.com"
        ),
        label="Input text (PII will be redacted)",
        rows=4,
    )
    mo.vstack([mo.md("## 3 — PII Redaction Lab"), sample_input])
    return (sample_input,)


@app.cell
def _show_redaction(mo, sample_input):
    from aegisap.security.redaction import redact_pii as _redact_pii

    original = sample_input.value
    redacted = _redact_pii(original) if original else ""

    mo.vstack([
        mo.md("**Original**"),
        mo.callout(mo.md(f"`{original}`"), kind="warn"),
        mo.md("**Redacted**"),
        mo.callout(mo.md(f"`{redacted}`"), kind="success"),
    ])
    return


@app.cell
def _audit_log(mo):
    from aegisap.training.postgres import build_connection_factory_from_env

    try:
        connect = build_connection_factory_from_env()
    except Exception as exc:  # noqa: BLE001
        mo.stop(
            True,
            mo.callout(
                mo.md(
                    f"PostgreSQL connection settings are not ready: `{exc}`\n\n"
                    "Recovery command:\n\n```bash\nuv run python scripts/verify_env.py --track full --env\n```"
                ),
                kind="warn",
            ),
        )

    _rows = []
    try:
        with connect() as _conn:
            with _conn.cursor() as _cur:
                _cur.execute(
                    "SELECT audit_id, thread_id, action_type, decision_outcome, created_at "
                    "FROM audit_events ORDER BY created_at DESC LIMIT 20"
                )
                for _row in _cur.fetchall():
                    _rows.append({
                        "audit_id": str(_row[0])[:8] + "…",
                        "thread_id": str(_row[1])[:8] + "…",
                        "action_type": _row[2],
                        "decision_outcome": _row[3],
                        "created_at": str(_row[4]),
                    })
    except Exception as exc:  # noqa: BLE001
        _rows = [{"error": str(exc)[:120]}]

    mo.vstack([
        mo.md(f"## 4 — Audit Log (last {len(_rows)} rows)"),
        mo.ui.table(_rows, selection=None) if _rows else mo.md(
            "*(no audit events yet)*"),
    ])
    return


@app.cell
def _persist(mo, posture):
    import json as _j
    from pathlib import Path as _P

    out_dir = _P(__file__).resolve().parents[1] / "build" / "day7"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = posture.as_dict()
    out_path = out_dir / "security_posture.json"
    out_path.write_text(_j.dumps(report, indent=2))

    mo.vstack([
        mo.callout(
            mo.md("Artifact written to `build/day7/security_posture.json`"), kind="success"),
        mo.download(
            data=_j.dumps(report, indent=2).encode(),
            filename="security_posture.json",
            mimetype="application/json",
            label="Download security_posture.json",
        ),
    ])
    return


@app.cell
def _ready_for_next_day(mo):
    from _shared.lab_guide import render_readiness_check

    render_readiness_check(
        mo,
        artifact_relpath="build/day7/security_posture.json",
        next_day="Day 8",
        recovery_command="uv run python scripts/verify_env.py --track full --env",
    )
    return


if __name__ == "__main__":
    app.run()
