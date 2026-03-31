# Day 9 — Cost, Model Routing & Caching
# ========================================
# Explore the ModelGateway's routing decisions in real time, query the cost
# ledger, tune the semantic cache TTL, and verify the budget gate.
# 
# Run:
#     marimo edit notebooks/day9_cost_routing.py

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
        # Day 9 — Cost, Model Routing & Caching

        **What you will learn**:
        - How `ModelGateway` routes a `TaskClass` to the *light* or *strong* deployment tier
        - Why routing reduces cost without sacrificing quality on low-risk tasks
        - How the semantic cache avoids redundant LLM calls for identical inputs
        - How the `CostLedger` gives per-call attribution for chargebacks and budgets
        - How an APIM throttle policy protects against burst spend

        > Prerequisite: Days 1–8 completed.
        """
    )


@app.cell
def _lab_contract(mo):
    from _shared.lab_guide import render_lab_overview

    render_lab_overview(
        mo,
        prerequisites=[
            "Day 8 produced `build/day8/regression_baseline.json`.",
            "Routing policy and optional APIM policy files are available in the repo.",
        ],
        required_inputs=[
            "A fixture package for the golden-thread execution.",
            "A daily budget value for the budget gate.",
        ],
        required_env_vars=[],
        expected_artifact="build/day9/routing_report.json",
        pass_criteria=[
            "The routing policy shows a deployment decision and reason.",
            "The notebook computes a sample ledger and budget status.",
            "The routing report is written for Day 10 budget gating.",
        ],
        implementation_exercise=(
            "Change one routing decision or cache-bypass case, regenerate the report, "
            "and defend the cost-quality tradeoff."
        ),
    )


@app.cell
def _routing_policy_lab(mo):
    from aegisap.routing.routing_policy import route_task, TaskClass

    task_options: list[str] = [
        "extract", "classify", "retrieve_summarise",
        "plan", "compliance_review", "reflection", "final_render",
    ]
    task_picker = mo.ui.dropdown(
        options=task_options,
        value="extract",
        label="Task Class",
    )
    mo.vstack([mo.md("## 1 — Routing Policy Lab"), task_picker])
    return task_picker, route_task


@app.cell
def _show_routing(mo, task_picker, route_task):
    decision = route_task(task_class=task_picker.value)
    tier_kind = "success" if decision.deployment_tier == "light" else "warn"
    mo.vstack([
        mo.hstack([
            mo.stat(label="Deployment", value=decision.deployment_name),
            mo.stat(label="Tier", value=decision.deployment_tier),
            mo.stat(label="Cache allowed", value=str(decision.cache_allowed)),
        ]),
        mo.callout(mo.md(f"**Reason**: {decision.reason}"), kind=tier_kind),
    ])


@app.cell
def _session_config(mo):
    daily_budget = mo.ui.number(
        start=0.01, stop=100.0, step=0.01, value=5.0,
        label="Daily budget (USD)",
    )
    ttl_slider = mo.ui.slider(
        start=0, stop=3600, value=300, step=60,
        label="Semantic cache TTL (seconds)",
    )
    mo.vstack([
        mo.md("## 2 — Session Configuration"),
        daily_budget,
        ttl_slider,
    ])
    return daily_budget, ttl_slider


@app.cell
def _run_golden_thread(mo, ttl_slider):
    import time as _t
    from aegisap.day_01.fixture_loader import load_fixture_package, list_fixture_cases
    from aegisap.day_01.agent import extract_candidate
    from aegisap.day_01.service import canonicalize_invoice
    from aegisap.routing.model_router import ModelGateway, ModelInvocationRequest

    cases = list_fixture_cases()
    mo.stop(not cases, mo.md("No fixture cases found."))

    package = load_fixture_package(cases[0])
    session_ledger: list[dict] = []

    t_start = _t.monotonic()
    candidate = extract_candidate(package)
    elapsed_ms = int((_t.monotonic() - t_start) * 1000)

    # Pull ledger from ModelGateway — approximate by reading cost metrics
    # (full ledger capture requires a session_id hook; we read the in-memory store)
    mo.vstack([
        mo.md("## 3 — Golden Thread Execution"),
        mo.stat(label="Extraction latency", value=f"{elapsed_ms} ms"),
        mo.callout(
            mo.md("Extraction complete. Ledger will populate below."), kind="success"),
    ])
    return candidate, elapsed_ms, session_ledger


@app.cell
def _cost_ledger_display(mo, elapsed_ms):
    # Build a representative ledger display from the last run
    # (full per-session ledger requires ModelGateway.session_id plumbing — Day 9 extension)
    sample_ledger = [
        {
            "node_name": "invoice_extraction",
            "deployment_name": "gpt-4.1-mini",
            "deployment_tier": "light",
            "prompt_tokens": 420,
            "completion_tokens": 180,
            "total_tokens": 600,
            "cached_hit": False,
            "latency_ms": elapsed_ms,
            "estimated_cost": round(420 / 1000 * 0.00015 + 180 / 1000 * 0.0006, 6),
        }
    ]
    total_cost = sum(r["estimated_cost"] for r in sample_ledger)

    mo.vstack([
        mo.md("## 4 — Cost Ledger"),
        mo.table(sample_ledger, selection=None),
        mo.stat(label="Total cost (session)", value=f"${total_cost:.6f}"),
        mo.stat(label="Cache hit rate", value="0%"),
    ])
    return (sample_ledger,)


@app.cell
def _budget_gate(mo, sample_ledger, daily_budget):
    from aegisap.cost.budget_gate import check_budget

    status = check_budget(sample_ledger, daily_budget_usd=daily_budget.value)

    kind = "success" if status.within_budget else "danger"
    mo.vstack([
        mo.md("## 5 — Budget Gate"),
        mo.hstack([
            mo.stat(label="Total cost", value=f"${status.total_cost_usd:.6f}"),
            mo.stat(label="Daily limit", value=f"${status.daily_limit_usd:.2f}"),
            mo.stat(label="Projected daily",
                    value=f"${status.projected_daily_usd:.4f}"),
            mo.stat(label="Headroom", value=f"${status.headroom_usd:.4f}"),
        ]),
        mo.callout(
            mo.md("**Within budget.**" if status.within_budget else "**OVER BUDGET.**"),
            kind=kind,
        ),
    ])
    return (status,)


@app.cell
def _apim_policy_viewer(mo):
    from pathlib import Path as _Path
    _repo_root = _Path(__file__).resolve().parents[1]
    apim_dir = _repo_root / "infra" / "apim" / "policies"
    apim_files = sorted(apim_dir.glob("*.xml")) if apim_dir.exists() else []

    if not apim_files:
        _out = mo.callout(
            mo.md("No APIM policy files found in `infra/apim/policies/`."), kind="warn")
    else:
        _out = mo.vstack([
            mo.md("## 6 — APIM Throttle Policy"),
            mo.tabs({f.stem: mo.code(f.read_text(), language="xml")
                    for f in apim_files}),
        ])
    _out


@app.cell
def _persist(mo, status, sample_ledger):
    import json as _j
    from pathlib import Path as _P

    out_dir = _P(__file__).resolve().parents[1] / "build" / "day9"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "budget_gate": status.as_dict(),
        "sample_ledger": sample_ledger,
    }
    out_path = out_dir / "routing_report.json"
    out_path.write_text(_j.dumps(report, indent=2))

    mo.vstack([
        mo.callout(
            mo.md("Artifact written to `build/day9/routing_report.json`"), kind="success"),
        mo.download(
            data=_j.dumps(report, indent=2).encode(),
            filename="routing_report.json",
            mimetype="application/json",
            label="Download routing_report.json",
        ),
    ])


@app.cell
def _ready_for_next_day(mo):
    from _shared.lab_guide import render_readiness_check

    render_readiness_check(
        mo,
        artifact_relpath="build/day9/routing_report.json",
        next_day="Day 10",
        recovery_command="marimo edit notebooks/day9_cost_routing.py",
    )


if __name__ == "__main__":
    app.run()
