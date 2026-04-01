# Day 2 — Stateful Routing with LangGraph
# =========================================
# Load the Day 1 CanonicalInvoice, choose a routing scenario, and watch the
# LangGraph WorkflowState mutate node-by-node in real time.
# 
# Run:
#     marimo edit notebooks/day2_stateful_workflow.py

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
    # Day 2 — Stateful Routing with LangGraph

    **What you will learn**:
    - Why a single LLM call is insufficient — workflows need explicit *state*
    - How LangGraph models state as a typed `WorkflowState` Pydantic object
    - How the route decision (`high_value / new_vendor / clean_path`) gates
      which review node runs
    - How `NodeMetric` + OTel spans expose per-node latency

    > Prerequisite: `build/day1/golden_thread_day1.json` must exist.
    """)
    return


@app.cell
def _lab_contract(mo):
    from _shared.lab_guide import render_lab_overview

    render_lab_overview(
        mo,
        prerequisites=[
            "Day 1 produced `build/day1/golden_thread_day1.json`.",
        ],
        required_inputs=[
            "A valid Day 1 canonical invoice artifact.",
            "One routing scenario: `known_vendor`, `new_vendor`, or `high_value`.",
        ],
        required_env_vars=[],
        expected_artifact="build/day2/golden_thread_day2.json",
        pass_criteria=[
            "The workflow executes end-to-end and shows a route and final status.",
            "The state diff explains how the workflow mutated the invoice context.",
            "The Day 2 artifact is written for downstream retrieval work.",
        ],
        implementation_exercise=(
            "Modify or re-run the routing scenario so a seeded escalation case lands on the "
            "correct state path without breaking the golden-thread artifact."
        ),
    )
    return


@app.cell
def _load_day1(mo):
    import json as _j
    from pathlib import Path as _P
    from aegisap.day_01.models import CanonicalInvoice

    artifact_path = _P(__file__).resolve(
    ).parents[1] / "build" / "day1" / "golden_thread_day1.json"
    mo.stop(
        not artifact_path.exists(),
        mo.callout(mo.md(
            "Run Day 1 first — `build/day1/golden_thread_day1.json` not found."), kind="danger"),
    )
    data = _j.loads(artifact_path.read_text())
    invoice_payload = data.get("canonical_invoice", data)
    if isinstance(invoice_payload, dict):
        invoice_payload = dict(invoice_payload)
        invoice_payload.pop("_meta", None)
    invoice = CanonicalInvoice.model_validate_json(_j.dumps(invoice_payload))

    mo.vstack([
        mo.md("## Day 1 Artifact Loaded"),
        mo.tree(invoice.model_dump(mode="json")),
    ])
    return (invoice,)


@app.cell
def _graph_viz(mo):
    from aegisap.day2.mermaid import generate_mermaid
    mo.vstack([
        mo.md("## Day 2 Workflow Graph"),
        mo.mermaid(generate_mermaid()),
    ])
    return


@app.cell
def _scenario_picker(mo):
    scenario = mo.ui.radio(
        options={
            "known_vendor (clean path)": "known_vendor",
            "new_vendor (extra review)": "new_vendor",
            "high_value (controller review)": "high_value",
        },
        value="known_vendor (clean path)",
        label="Routing Scenario",
    )
    mo.vstack([mo.md("## Choose Routing Scenario"), scenario])
    return (scenario,)


@app.cell
def _run_workflow(invoice, mo, scenario):
    import time as _t
    import uuid as _uuid
    from decimal import Decimal

    from aegisap.day2.config import HIGH_VALUE_THRESHOLD, ROUTE_PRECEDENCE
    from aegisap.day2.graph import build_graph
    from aegisap.day2.state import WorkflowState, make_initial_state

    _scenario = scenario.value

    scenario_invoice = invoice
    if _scenario in {"known_vendor", "new_vendor"}:
        scenario_invoice = invoice.model_copy(
            update={
                "net_amount": Decimal("7600.00"),
                "vat_amount": Decimal("1900.00"),
                "gross_amount": Decimal("9500.00"),
            }
        )
    elif _scenario == "high_value":
        scenario_invoice = invoice.model_copy(
            update={
                "net_amount": Decimal("12000.00"),
                "vat_amount": Decimal("3000.00"),
                "gross_amount": Decimal("15000.00"),
            }
        )

    initial_state = make_initial_state(
        scenario_invoice,
        package_id=f"notebook-{scenario_invoice.invoice_number}-{_scenario}-{_uuid.uuid4().hex[:8]}",
        known_vendor=(_scenario != "new_vendor"),
        high_value_threshold=HIGH_VALUE_THRESHOLD,
        route_precedence=ROUTE_PRECEDENCE,
        thread_id=str(_uuid.uuid4()),
    )

    graph = build_graph()
    t_start = _t.monotonic()
    final_state = graph.invoke(initial_state)
    if not isinstance(final_state, WorkflowState):
        final_state = WorkflowState.model_validate(final_state)
    elapsed_ms = int((_t.monotonic() - t_start) * 1000)

    mo.vstack([
        mo.md("## Workflow Executed"),
        mo.stat(label="Route taken", value=str(final_state.route)),
        mo.stat(label="Final status", value=str(final_state.status)),
        mo.stat(label="Wall-clock", value=f"{elapsed_ms} ms"),
    ])
    return elapsed_ms, final_state, initial_state


@app.cell
def _state_diff(final_state, initial_state, mo):
    mo.vstack([
        mo.md("## WorkflowState — Before vs After"),
        mo.hstack(
            [
                mo.vstack([mo.md("**Initial state**"),
                          mo.tree(initial_state.model_dump(mode="json"))]),
                mo.vstack([mo.md("**Final state**"),
                          mo.tree(final_state.model_dump(mode="json"))]),
            ],
            gap=3,
        ),
    ])
    return


@app.cell
def _evidence_panel(final_state, mo):
    items = final_state.evidence or []
    recs = final_state.recommendations or []
    mo.vstack([
        mo.md("## Evidence & Recommendations"),
        mo.accordion({
            "Evidence items": mo.tree([e.model_dump(mode="json") for e in items]) if items else mo.md("*(none)*"),
            "Recommendations": mo.tree([r.model_dump(mode="json") for r in recs]) if recs else mo.md("*(none)*"),
            "Warnings": mo.md("\n".join(f"- {w}" for w in final_state.warnings) or "*(none)*"),
        }),
    ])
    return


@app.cell
def _persist(elapsed_ms, final_state, mo):
    import json as _j
    from pathlib import Path as _P

    out_dir = _P(__file__).resolve().parents[1] / "build" / "day2"
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact = final_state.model_dump(mode="json")
    artifact["_meta"] = {"elapsed_ms": elapsed_ms}
    out_path = out_dir / "golden_thread_day2.json"
    out_path.write_text(_j.dumps(artifact, indent=2))

    mo.vstack([
        mo.callout(mo.md(
            "Artifact written to `build/day2/golden_thread_day2.json`"), kind="success"),
        mo.download(
            data=_j.dumps(artifact, indent=2).encode(),
            filename="golden_thread_day2.json",
            mimetype="application/json",
            label="Download golden_thread_day2.json",
        ),
    ])
    return


@app.cell
def _ready_for_next_day(mo):
    from _shared.lab_guide import render_readiness_check

    render_readiness_check(
        mo,
        artifact_relpath="build/day2/golden_thread_day2.json",
        next_day="Day 3",
        recovery_command="marimo edit notebooks/day2_stateful_workflow.py",
    )
    return


if __name__ == "__main__":
    app.run()
