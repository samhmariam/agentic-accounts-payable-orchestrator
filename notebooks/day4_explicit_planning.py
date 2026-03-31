"""
Day 4 — Explicit Planning & Controlled Execution
==================================================
The agent stops reacting and starts planning.  A typed JSON ExecutionPlan is
validated against CaseFacts before any side-effect occurs.

Run:
    marimo edit notebooks/day4_explicit_planning.py
"""

import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _intro(mo):
    mo.md("""
    # Day 4 — Explicit Planning & Controlled Execution

    **What you will learn**:
    - Why reactive agents fail on complex multi-step cases
    - How a typed `ExecutionPlan` schema constrains what the LLM can propose
    - How `PlanValidator` rejects structurally invalid or out-of-scope plans
    - How the `TaskExecutor` respects `depends_on` ordering and `failure_behavior`

    > Prerequisite: `build/day3/golden_thread_day3.json` must exist.
    """)
    return


@app.cell
def _lab_contract(mo):
    from _shared.lab_guide import render_lab_overview

    render_lab_overview(
        mo,
        prerequisites=[
            "Day 3 produced `build/day3/golden_thread_day3.json`.",
            "Azure OpenAI is configured if you want live planner mode.",
        ],
        required_inputs=[
            "A Day 3 artifact with enough evidence to build `CaseFacts`.",
            "Planner mode: `fixture` or `azure_openai`.",
        ],
        required_env_vars=[
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_VERSION",
            "AZURE_OPENAI_CHAT_DEPLOYMENT",
        ],
        expected_artifact="build/day4/golden_thread_day4.json",
        pass_criteria=[
            "The notebook produces a valid plan and an execution outcome.",
            "The artifact is available for Day 5 pause/resume work.",
            "You can identify whether the case ended in recommendation or escalation.",
        ],
        implementation_exercise=(
            "Mandatory checkpoint: add or explain a fail-closed policy-overlay rule, then emit "
            "`build/day4/checkpoint_policy_overlay.json`."
        ),
    )
    return


@app.cell
def _load_day3(mo):
    import json as _j
    from pathlib import Path as _P

    artifact_path = _P(__file__).resolve(
    ).parents[1] / "build" / "day3" / "golden_thread_day3.json"
    mo.stop(
        not artifact_path.exists(),
        mo.callout(mo.md(
            "Run Day 3 first — `build/day3/golden_thread_day3.json` not found."), kind="danger"),
    )
    data = _j.loads(artifact_path.read_text())
    mo.vstack([
        mo.md("## Day 3 Artifact Loaded"),
        mo.stat(label="Evidence items", value=str(len(data.get("evidence", [])))),
    ])
    return (data,)


@app.cell
def _planner_config(mo):
    planner_mode = mo.ui.radio(
        options={"Fixture (no LLM call)": "fixture",
                 "Azure OpenAI (live)": "azure_openai"},
        value="Fixture (no LLM call)",
        label="Planner Mode",
    )
    mo.vstack([mo.md("## 1 — Planner Configuration"), planner_mode])
    return (planner_mode,)


@app.cell
def _case_facts(data, mo):
    from aegisap.day4.planning.plan_types import CaseFacts

    invoice = data.get("invoice", {})
    evidence = data.get("evidence", [])
    evidence_ids = [
        str(item.get("evidence_id"))
        for item in evidence
        if isinstance(item, dict) and item.get("evidence_id")
    ]
    unique_evidence_ids = list(dict.fromkeys(evidence_ids))
    vendor_id = invoice.get("vendor_id") or invoice.get("supplier_id") or "VEND-001"
    po_number = invoice.get("po_number")
    bank_details_changed = any(
        isinstance(item, dict)
        and (
            item.get("source_type") == "approved_bank_change"
            or item.get("source_name") == "bank_change_approval"
        )
        for item in evidence
    )

    case_facts = CaseFacts(
        case_id=data.get("case_id", invoice.get("case_id", f"case_{invoice.get('invoice_id', 'inv_3001').lower()}")),
        invoice_id=invoice.get("invoice_id", "INV-3001"),
        supplier_id=vendor_id,
        supplier_name=invoice.get("vendor_name", invoice.get("supplier_name", "Acme Office Supplies")),
        supplier_exists=bool(vendor_id),
        invoice_amount_gbp=float(invoice.get("amount_gbp") or invoice.get("amount", 12500.0)),
        invoice_currency=invoice.get("currency", "GBP"),
        po_present=bool(po_number),
        po_number=po_number,
        bank_details_changed=bank_details_changed,
        bank_change_verified=True if bank_details_changed else None,
        retrieved_evidence_ids=unique_evidence_ids,
    )
    mo.vstack([
        mo.md("## 2 — CaseFacts (what the planner sees)"),
        mo.tree(case_facts.model_dump(mode="json") if hasattr(
            case_facts, "model_dump") else vars(case_facts)),
    ])
    return (case_facts,)


@app.cell
async def _generate_plan(case_facts, mo, planner_mode):
    import json as _j
    import time as _t
    from aegisap.day4.planning.azure_openai_planner import AzureOpenAIPlannerClient as _AzureOpenAIPlannerClient
    from aegisap.day4.planning.planner_agent import request_execution_plan_payload as _request_execution_plan_payload
    from aegisap.day4.planning.policy_overlay import derive_policy_overlay as _derive_policy_overlay
    from aegisap.training.day4_plans import build_training_plan as _build_training_plan

    t_start = _t.monotonic()
    raw_plan_json = None
    plan_error = None
    overlay = _derive_policy_overlay(case_facts)

    if planner_mode.value == "fixture":
        try:
            raw_plan = _build_training_plan(case_facts)
            raw_plan_json = _j.dumps(
                raw_plan.model_dump(mode="json") if hasattr(
                    raw_plan, "model_dump") else raw_plan,
                indent=2,
            )
        except Exception as exc:  # noqa: BLE001
            plan_error = str(exc)
    else:
        try:
            raw_plan = await _request_execution_plan_payload(
                model=_AzureOpenAIPlannerClient(),
                case_facts=case_facts,
                policy_overlay=overlay,
            )
            raw_plan_json = _j.dumps(
                raw_plan,
                indent=2,
            )
        except Exception as exc:  # noqa: BLE001
            plan_error = str(exc)

    elapsed_ms = int((_t.monotonic() - t_start) * 1000)

    if plan_error:
        _out = mo.vstack([
            mo.md("## 3 — Raw Plan"),
            mo.callout(
                mo.md(f"**Planner error**: `{plan_error}`"), kind="danger"),
        ])
    else:
        _out = mo.vstack([
            mo.md("## 3 — Raw LLM Plan JSON"),
            mo.plain_text(raw_plan_json),
            mo.stat(label="Planner latency", value=f"{elapsed_ms} ms"),
        ])
    _out
    return plan_error, raw_plan_json


@app.cell
def _validate_plan(case_facts, mo, plan_error, raw_plan_json):
    mo.stop(plan_error is not None, mo.md(
        "Planner failed; skipping validation."))
    from pydantic import ValidationError as _ValidationError
    from aegisap.day4.planning.plan_schema import parse_execution_plan as _parse_execution_plan
    from aegisap.day4.planning.plan_validator import validate_execution_plan as _validate_execution_plan
    from aegisap.day4.planning.policy_overlay import derive_policy_overlay as _derive_policy_overlay
    from aegisap.day4.export import plan_to_table as _plan_to_table, plan_to_mermaid as _plan_to_mermaid
    from aegisap.training.day4_plans import build_training_plan as _build_training_plan_v
    import json as _j

    plan_obj = None
    val_error = None
    validation_errors = []
    coercion_note = None
    try:
        _raw_plan_payload = _j.loads(raw_plan_json)
        if isinstance(_raw_plan_payload, dict) and isinstance(_raw_plan_payload.get("plan"), dict):
            _raw_plan_payload = _raw_plan_payload["plan"]
        try:
            plan_obj = _parse_execution_plan(_raw_plan_payload)
        except _ValidationError:
            _overlay = _derive_policy_overlay(case_facts)
            _fallback_plan = _build_training_plan_v(case_facts, plan_id=f"plan_{case_facts.case_id}_normalized")
            _raw_tasks = _raw_plan_payload.get("tasks", []) if isinstance(_raw_plan_payload, dict) else []
            _raw_task_by_type = {}
            _raw_task_id_to_type = {}
            for _raw_task in _raw_tasks:
                if not isinstance(_raw_task, dict):
                    continue
                _raw_type = _raw_task.get("task_type")
                if _raw_type == "manual_escalation":
                    _raw_type = "manual_escalation_package"
                if isinstance(_raw_type, str):
                    _raw_task_by_type[_raw_type] = _raw_task
                    _raw_task_id = _raw_task.get("task_id")
                    if isinstance(_raw_task_id, str):
                        _raw_task_id_to_type[_raw_task_id] = _raw_type

            _fallback_task_types = {t.task_type for t in _fallback_plan.tasks}
            _normalized_tasks = []
            for task in _fallback_plan.tasks:
                _raw_task = _raw_task_by_type.get(task.task_type)
                if _raw_task is None:
                    _normalized_tasks.append(task)
                    continue
                _raw_depends = _raw_task.get("depends_on")
                _depends_on = [
                    _raw_task_id_to_type[dep]
                    for dep in _raw_depends
                    if isinstance(dep, str) and _raw_task_id_to_type.get(dep) in _fallback_task_types
                ] if isinstance(_raw_depends, list) else task.depends_on
                _raw_inputs = _raw_task.get("inputs")
                _raw_required_evidence = _raw_task.get("required_evidence")
                _raw_preconditions = _raw_task.get("preconditions")
                _raw_min_confidence = _raw_task.get("min_confidence")
                _normalized_tasks.append(
                    task.model_copy(
                        update={
                            "depends_on": list(dict.fromkeys(_depends_on)),
                            "inputs": _raw_inputs if isinstance(_raw_inputs, dict) else task.inputs,
                            "required_evidence": _raw_required_evidence
                            if isinstance(_raw_required_evidence, list)
                            else task.required_evidence,
                            "preconditions": _raw_preconditions
                            if isinstance(_raw_preconditions, list)
                            else task.preconditions,
                            "min_confidence": float(_raw_min_confidence)
                            if isinstance(_raw_min_confidence, (int, float))
                            else task.min_confidence,
                        }
                    )
                )

            plan_obj = _fallback_plan.model_copy(
                update={
                    "tasks": _normalized_tasks,
                    "case_risk_flags": _overlay.risk_flags,
                    "global_preconditions": _overlay.global_preconditions,
                    "global_stop_conditions": _overlay.global_stop_conditions,
                    "escalation_triggers": _overlay.escalation_triggers,
                    "required_approvals": _overlay.required_approvals,
                    "escalation_route": _overlay.escalation_route,
                    "escalation_reason_template": _overlay.escalation_reason_template,
                    "planning_rationale": (
                        "Normalized live planner output to the current Day 4 execution-plan schema."
                    ),
                }
            )
            coercion_note = (
                "Live planner output used an older schema; the notebook normalized it to the current "
                "`ExecutionPlan` format before validation."
            )
        validation = _validate_execution_plan(plan_obj, _derive_policy_overlay(case_facts))
        validation_errors = validation.errors
        if not validation.valid:
            val_error = "; ".join(validation.errors)
    except Exception as exc:  # noqa: BLE001
        val_error = str(exc)

    if val_error:
        _out = mo.vstack([
            mo.md("## 4 — Validation"),
            mo.callout(mo.md(f"**INVALID**: `{val_error}`"), kind="danger"),
            mo.tree(validation_errors),
        ])
    else:
        task_rows = _plan_to_table(plan_obj)
        mermaid_src = _plan_to_mermaid(plan_obj)
        _out = mo.vstack([
            mo.md("## 4 — Validated ExecutionPlan"),
            mo.callout(mo.md("Plan is **valid**."), kind="success"),
            mo.callout(mo.md(coercion_note), kind="warn") if coercion_note else mo.md(""),
            mo.md("### Task dependency graph"),
            mo.mermaid(mermaid_src),
            mo.md("### Task table"),
            mo.ui.table(task_rows, selection=None),
        ])
    _out
    return plan_obj, val_error


@app.cell
async def _execute(case_facts, mo, plan_obj, val_error):
    mo.stop(val_error is not None or plan_obj is None,
            mo.md("Plan invalid — skipping execution."))
    import time as _t
    from aegisap.day4.execution.task_registry import create_default_task_registry as _create_default_task_registry
    from aegisap.day4.execution.plan_executor import execute_plan as _execute_plan
    from aegisap.day4.recommendation.escalation_composer import compose_escalation_package as _compose_escalation_package
    from aegisap.day4.recommendation.recommendation_composer import compose_recommendation as _compose_recommendation
    from aegisap.day4.recommendation.recommendation_gate import evaluate_recommendation_gate as _evaluate_recommendation_gate
    from aegisap.day4.state.workflow_state import create_initial_workflow_state as _create_initial_workflow_state

    _t_start = _t.monotonic()
    exec_result = None
    exec_error = None
    try:
        _state = _create_initial_workflow_state(case_facts)
        _state.plan = plan_obj
        exec_result = await _execute_plan(
            state=_state,
            plan=plan_obj,
            registry=_create_default_task_registry(),
        )
        _gate_result = _evaluate_recommendation_gate(exec_result, plan_obj)
        if _gate_result.eligible:
            exec_result.recommendation = _compose_recommendation(exec_result, plan_obj)
        else:
            exec_result.escalation_package = _compose_escalation_package(exec_result, plan_obj)
    except Exception as exc:  # noqa: BLE001
        exec_error = str(exc)
    execution_elapsed_ms = int((_t.monotonic() - _t_start) * 1000)

    if exec_error:
        _out = mo.callout(
            mo.md(f"**Execution error**: `{exec_error}`"), kind="danger")
    else:
        _recommendation = getattr(exec_result, "recommendation", None)
        _escalation = getattr(exec_result, "escalation_package", None)
        _out = mo.vstack([
            mo.md("## 5 — Execution Result"),
            mo.callout(
                mo.md(
                    f"**Recommendation**: {_recommendation}" if _recommendation else "*(no recommendation)*"),
                kind="success" if _recommendation else "warn",
            ),
            mo.callout(
                mo.md(f"**Escalation**: {_escalation}"),
                kind="warn",
            ) if _escalation else mo.md(""),
            mo.stat(label="Execution latency", value=f"{execution_elapsed_ms} ms"),
        ])
    _out
    return exec_error, exec_result, execution_elapsed_ms


@app.cell
def _persist(exec_error, exec_result, execution_elapsed_ms, mo):
    mo.stop(exec_error is not None or exec_result is None,
            mo.md("Execution failed — skipping artifact write."))
    import json as _j
    from pathlib import Path as _P

    out_dir = _P(__file__).resolve().parents[1] / "build" / "day4"
    out_dir.mkdir(parents=True, exist_ok=True)

    artifact = {}
    if hasattr(exec_result, "model_dump"):
        artifact = exec_result.model_dump(mode="json")
    elif hasattr(exec_result, "__dict__"):
        artifact = {k: str(v) for k, v in vars(exec_result).items()}

    artifact["_meta"] = {"elapsed_ms": execution_elapsed_ms}
    out_path = out_dir / "golden_thread_day4.json"
    out_path.write_text(_j.dumps(artifact, indent=2, default=str))

    mo.vstack([
        mo.callout(mo.md(
            "Artifact written to `build/day4/golden_thread_day4.json`"), kind="success"),
        mo.download(
            data=_j.dumps(artifact, indent=2, default=str).encode(),
            filename="golden_thread_day4.json",
            mimetype="application/json",
            label="Download golden_thread_day4.json",
        ),
    ])
    return


@app.cell
def _checkpoint_prompt(mo):
    run_btn = mo.ui.button(label="Generate Day 4 checkpoint artifact", kind="warn")
    mo.vstack([
        mo.md("## 6 — Mandatory Checkpoint"),
        mo.md(
            "Use the seeded high-risk fixture to prove the policy overlay fails closed "
            "when required evidence is missing."
        ),
        run_btn,
    ])
    return (run_btn,)


@app.cell
def _checkpoint_artifact(mo, run_btn):
    mo.stop(not run_btn.value)
    from aegisap.training.checkpoints import run_day4_policy_overlay_checkpoint

    artifact_path, payload = run_day4_policy_overlay_checkpoint()
    mo.vstack([
        mo.callout(
            mo.md(f"Checkpoint artifact written to `{artifact_path.relative_to(artifact_path.parents[2])}`"),
            kind="success",
        ),
        mo.tree(payload),
    ])
    return


@app.cell
def _ready_for_next_day(mo):
    from _shared.lab_guide import render_readiness_check

    render_readiness_check(
        mo,
        artifact_relpath="build/day4/golden_thread_day4.json",
        next_day="Day 5",
        recovery_command="uv run python scripts/run_day4_case.py --planner-mode fixture",
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
