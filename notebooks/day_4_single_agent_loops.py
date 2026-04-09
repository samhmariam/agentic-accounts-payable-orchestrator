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

    from _shared.curriculum_scaffolds import deep_reload_modules

    deep_reload_modules("aegisap")

    from aegisap.day4.planning.policy_overlay import derive_policy_overlay
    from aegisap.day4.recommendation.recommendation_gate import evaluate_recommendation_gate
    from aegisap.day4.state.workflow_state import create_initial_workflow_state
    from aegisap.training.day4_plans import build_training_plan
    from aegisap.training.labs import load_case_facts

    return (
        build_training_plan,
        create_initial_workflow_state,
        derive_policy_overlay,
        load_case_facts,
        mo,
        repo_root,
        evaluate_recommendation_gate,
    )


@app.cell
def _title(mo):
    mo.md(
        """
        # Day 4 - Single-Agent Loops, Policy Overlay, and Fail-Closed Repair

        Primary learner entrypoint: `modules/day_04_single_agent_loops/README.md`. Read the customer context and file manifest there before you start the incident.

        Day 4 starts from a dangerous regression: combined-risk invoices are no longer
        guaranteed to trigger manual review. You are here to prove that the planner and
        gate still fail closed when the controls get ugly.
        """
    )
    return


@app.cell
def _rubric_helper(repo_root):
    import sys

    notebooks_root = repo_root / "notebooks"
    text = str(notebooks_root)
    if text not in sys.path:
        sys.path.insert(0, text)

    from _shared.curriculum_scaffolds import render_daily_rubric_callout

    return (render_daily_rubric_callout,)


@app.cell
def _rubric_surface(mo, render_daily_rubric_callout, repo_root):
    render_daily_rubric_callout(mo, day="04", repo_root=repo_root)
    return


@app.cell
def _incident(mo):
    mo.md(
        """
        ## Incident

        A high-value invoice with missing PO evidence and changed bank details is no
        longer producing the expected combined-risk behavior.

        **What success looks like**

        - combined-risk invoices always carry the correct risk flag
        - manual escalation remains mandatory for the risky slice
        - the recommendation gate never acts like this path is safe to auto-progress

        ## Stakeholder Inject

        The executive sponsor has now asked you to bypass the pause and auto-issue
        payments. You are expected to refuse that request in two forms:

        - internal engineering record: `adr/ADR-002_irreversible_actions_and_hitl.md`
        - sponsor-facing response: `docs/curriculum/artifacts/day04/SPONSOR_PUSHBACK_EMAIL.md`
        """
    )
    return


@app.cell
def _portal_investigation(mo):
    mo.md(
        """
        ## Portal Investigation

        Before you patch the planner, gather production evidence:

        1. Inspect the execution trace for the failing invoice and capture the actual risk flags.
        2. Confirm the underlying invoice facts still show missing PO plus changed bank details.
        3. Compare the policy overlay output with the final routing decision.
        4. Prove whether the bug is in risk derivation, recommendation gating, or both.
        """
    )
    return


@app.cell
def _lab_repair_intro(mo):
    mo.md(
        """
        ## Lab Repair

        Use the notebook to prove the fail-closed logic in memory before you change the
        production planner or gate.
        """
    )
    return


@app.cell
def _overlay_preview(
    build_training_plan,
    create_initial_workflow_state,
    derive_policy_overlay,
    load_case_facts,
    mo,
    repo_root,
    evaluate_recommendation_gate,
):
    case_facts = load_case_facts(repo_root / "fixtures" / "day4" / "high_value_missing_po_bank_change.json")
    overlay = derive_policy_overlay(case_facts)
    plan = build_training_plan(case_facts, plan_id=f"plan_{case_facts.case_id}")
    state = create_initial_workflow_state(case_facts)
    gate = evaluate_recommendation_gate(state, plan)

    mo.callout(
        mo.md(
            f"""
            Prototype outcome:

            - `risk_flags={overlay.risk_flags}`
            - `mandatory_task_types={overlay.mandatory_task_types}`
            - `eligible={gate.eligible}`
            - `reasons={gate.reasons}`
            """
        ),
        kind="info",
    )
    return


@app.cell
def _codification_bridge(mo):
    mo.md(
        """
        ## Why This Fails In Prod

        List three specific ways this notebook logic fails in an Azure Container App. You must reference at least one Azure limit (memory, timeout, or ephemeral storage) and one concurrency issue.

        ## Codification Bridge

        Treat the trace evidence and notebook prototype as one fail-closed contract.

        - Portal state: the risky invoice facts and final routing outcome disagree.
        - Notebook proof: the overlay preview shows whether the break lives in risk derivation, recommendation gating, or both.
        - Permanent repo change: `src/aegisap/day4/planning/policy_overlay.py` and `src/aegisap/day4/recommendation/recommendation_gate.py`.

        Rosetta Stone: `notebooks/bridges/day04_fail_closed_planning.md`
        """
    )
    return


@app.cell
def _production_patch(mo):
    mo.md(
        """
        ## Production Patch

        This section is **markdown-only**.

        Do not edit repo files from this notebook.

        Edit the repo target in your IDE first.

        Rerun this notebook bootstrap cell after every repo edit so `deep_reload_modules(...)`
        reloads the real package imports before you trust the notebook proof again.

        Write the durable patch in the repo target below, not inside Marimo.

        Implement the repair in the production files:

        - `src/aegisap/day4/planning/policy_overlay.py`
        - `src/aegisap/day4/recommendation/recommendation_gate.py`

        Then update the written evidence:

        - `docs/curriculum/artifacts/day04/ACTION_RISK_REGISTER.md`
        - `docs/curriculum/artifacts/day04/POLICY_PRECEDENCE.md`
        - `adr/ADR-002_irreversible_actions_and_hitl.md`
        - `docs/curriculum/artifacts/day04/SPONSOR_PUSHBACK_EMAIL.md`

        ### Export to Production

        - Which exact risk combination stopped failing closed?
        - Which file enforces the durable fix: `policy_overlay.py`, `recommendation_gate.py`, or both?
        - Which test and rebuilt artifact prove manual escalation is mandatory again?
        - Which ADR and sponsor-facing artifact defend the Executive No?
        """
    )
    return


@app.cell
def _verification(repo_root, mo):
    artifact_path = repo_root / "build" / "day4" / "golden_thread_day4.json"
    native_path = repo_root / "build" / "day4" / "native_operator_evidence.json"
    artifact_note = (
        f"Current artifact present: `{artifact_path.relative_to(repo_root)}`"
        if artifact_path.exists()
        else "Artifact missing: rebuild the Day 4 artifact after the repair."
    )
    native_note = (
        f"Native evidence path: `{native_path.relative_to(repo_root)}`"
        if native_path.exists()
        else f"Native evidence still required later: `{native_path.relative_to(repo_root)}`"
    )
    mo.md(
        f"""
        ## Verification

        Run these commands in the terminal:

        ```bash
        uv run python -m pytest tests/day4/unit/planning/test_policy_overlay.py tests/day4/unit/recommendation/test_recommendation_gate.py -q
        uv run aegisap-lab artifact rebuild --day 04
        ```

        {artifact_note}

        {native_note}
        """
    )
    return


@app.cell
def _native_tooling_gate(mo):
    mo.md(
        """
        ## Native Tooling Gate

        Policy source: `docs/curriculum/NATIVE_TOOLING_POLICY.md`

        Save your raw operator proof in `build/day4/native_operator_evidence.json`.

        Use Azure Portal, `az`, or `az rest` to capture the public-network and fail-closed
        signal family before you patch. Append `-o json` to Azure CLI diagnostics so the
        saved `observed_excerpt` is machine-readable and replayable.

        Tools banned during this gate:

        - `aegisap-lab`
        - helper verification wrappers
        - canned answer keys

        Wrappers stay banned until the raw evidence file is complete. After that, they may
        be used only for artifact rebuild, mastery, or reset flows.
        """
    )
    return


@app.cell
def _chaos_gate(mo):
    mo.md(
        """
        ## Chaos Gate

        Failure signal: Execution traces show a risky recommendation escaping the policy overlay while public exposure constraints stay in force.

        Diagnostic surface: Execution traces, policy overlay cells, and live cloud posture for AI and data endpoints.

        Expected recovery artifact: `build/day4/golden_thread_day4.json`

        Time box: 25 minutes. If you miss it, stop and rerun the four pillars in `docs/curriculum/FDE_DEBUGGING_FRAMEWORK.md`.
        """
    )
    return


@app.cell
def _map_the_gap(mo):
    mo.md(
        """
        ## Map the Gap

        Capture these before you ask for review:

        - Portal action or observed state:
        - Exact API/SDK/Python call that matches it:
        - Exact relative production filepath that made the fix durable:
        """
    )
    return


@app.cell
def _pr_defense(mo):
    mo.md(
        """
        ## PR Defense

        Answer these three questions before you push:

        - What trade-off did I make today to satisfy the customer constraint?
        - What is the blast radius if my code fails?
        - How will I know it failed in production?

        Copy-ready PR body:

        ```md
        ## Principal Review Defense
        - Trade-off: <name the compromise and why it was worth it>
        - Blast radius: <name the affected systems, approvers, and rollback edge>
        - Production failure signal: <monitor, alert, trace, or dashboard link>
        - Constraint held: <which inherited customer rule stayed intact>
        ```

        Open or update a PR targeting `cohort/<your-name>/<day-slug>`, paste the markdown block below into the PR body, and push to trigger `.github/workflows/principal-review.yml` on `opened`, `synchronize`, or `ready_for_review`.
        """
    )
    return
