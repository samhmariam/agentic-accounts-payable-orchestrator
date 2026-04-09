import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _bootstrap():
    import json
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

    from aegisap.cache.cache_policy import evaluate_cache_policy
    from aegisap.cost.budget_gate import check_budget
    from aegisap.routing.routing_policy import route_task

    return check_budget, evaluate_cache_policy, json, mo, repo_root, route_task


@app.cell
def _title(mo):
    mo.md(
        """
        # Day 9 - Observability, Routing, Cost, and Economic Control

        Primary learner entrypoint: `modules/day_09_observability_cost/README.md`. Read the customer context and file manifest there before you start the incident.

        Day 9 begins with a cost-cutting drift that quietly routes risky work onto a
        cheaper model tier. Your job is to prove the routing mistake, restore the
        safety escalation logic, and defend the economic tradeoff in writing.
        """
    )
    return


@app.cell
def _incident(mo):
    mo.md(
        """
        ## Incident

        Finance asked for cheaper routing, and the deployed policy now under-routes
        high-risk tasks to the light tier unless confidence is also low.

        **What success looks like**

        - risk escalators force strong-tier routing again
        - cache and budget logic still remain explicit and observable
        - the Day 9 cost artifacts explain why unsafe cost savings are rejected
        """
    )
    return


@app.cell
def _portal_investigation(mo):
    mo.md(
        """
        ## Portal Investigation

        Start in the live telemetry before you edit the router:

        1. Open Application Insights and compare a high-risk workflow run to a clean-path run.
        2. Confirm which deployment tier each task class used and whether the risky case stayed on the light tier.
        3. Inspect cost and latency signals for the same trace so you can separate budget pressure from safety pressure.
        4. Capture which routing rule changed the operator outcome.
        """
    )
    return


@app.cell
def _lab_intro(mo):
    mo.md(
        """
        ## Lab Repair

        Use the notebook to exercise the routing contract in-memory. The real fix
        still belongs in the routing and cost code under `src/`.
        """
    )
    return


@app.cell
def _starter_investigation(mo):
    mo.md(
        """
        ## Starter Investigation

        Starter-only mode is active from this day onward.

        Do not use the shared lab wrapper helpers in this phase.
        Build your own probes with `azure-identity` and the relevant `azure-mgmt-*` SDK clients, then carry only the proof back into the notebook.
        """
    )
    return


@app.cell
def _routing_preview(check_budget, evaluate_cache_policy, json, mo, route_task):
    clean = route_task(task_class="extract", risk_flags=["clean_path"])
    risky = route_task(task_class="extract", risk_flags=["high_value", "bank_details_changed"])
    cache = evaluate_cache_policy(
        task_class="retrieve_summarise",
        risk_flags=["high_value"],
        retrieval_confidence=0.96,
    )
    budget = check_budget(
        [
            {"estimated_cost": 0.0042, "task_class": "extract"},
            {"estimated_cost": 0.0036, "task_class": "plan"},
            {"estimated_cost": 0.0061, "task_class": "compliance_review"},
        ],
        daily_limit_usd=5.0,
    )
    mo.callout(
        mo.md(
            f"""
            Routing preview:

            ```json
            {json.dumps(
                {
                    "clean_route": clean.to_metadata(),
                    "risky_route": risky.to_metadata(),
                    "cache_decision": {
                        "allowed": cache.allowed,
                        "bypass_reason": cache.bypass_reason,
                    },
                    "budget_status": budget.as_dict(),
                },
                indent=2,
            )}
            ```
            """
        ),
        kind="info",
    )
    return


@app.cell
def _kql_evidence(mo):
    mo.md(
        """
        ## KQL Evidence

        Save `build/day9/kql_evidence.json` before you patch production code.

        Capture at least one literal Log Analytics query with:

        - capture order
        - captured_before_patch=true
        - workspace
        - first_signal_or_followup
        - correlation or trace reference when available
        - purpose
        - observed excerpt
        - operator interpretation
        """
    )
    return


@app.cell
def _codification_bridge(mo):
    mo.md(
        """
        ## Why This Fails In Prod

        List three specific ways this notebook logic fails in an Azure Container App. You must reference at least one Azure limit (memory, timeout, or ephemeral storage) and one concurrency issue.

        ## Codification Bridge

        Treat the routing telemetry and notebook previews as the same control decision.

        - Portal state: risky work is staying on the wrong deployment tier.
        - Notebook proof: the routing, cache, and budget preview shows whether routing, cache policy, or budget framing drifted.
        - Durable repo boundary: the routing-control owner in the observability, cache, or budget boundary that keeps risky work off the wrong tier.

        Rosetta Stone: `notebooks/bridges/day09_routing_cost.md`
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

        Move into the real routing boundary and identify the durable owner of:

        - routing safety for the correct deployment tier
        - cache behavior if stale or cheap-tier bypass is part of the failure
        - budget framing only if the cost-control decision is wrong

        Then update the written Day 9 evidence:

        - `docs/curriculum/artifacts/day09/CAPABILITY_ALLOCATION_MEMO.md`
        - `docs/curriculum/artifacts/day09/COST_GOVERNANCE_POLICY.md`
        - `docs/curriculum/artifacts/day09/PTU_PAYG_DECISION_NOTE.md`

        ### Export to Production

        - Which telemetry signal proved the wrong tier choice?
        - Which policy file makes the safety escalation durable?
        - Which verification proves risky work no longer rides the cheap tier?
        """
    )
    return


@app.cell
def _verification(repo_root, mo):
    artifact_path = repo_root / "build" / "day9" / "routing_report.json"
    native_path = repo_root / "build" / "day9" / "native_operator_evidence.json"
    artifact_note = (
        f"Current artifact present: `{artifact_path.relative_to(repo_root)}`"
        if artifact_path.exists()
        else "Artifact missing: rebuild the Day 9 artifact after the repair."
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
        uv run python -m pytest tests/day9/test_routing_policy.py tests/day9/test_cache_and_cost.py tests/day9/test_runtime_day9_contract.py -q
        uv run aegisap-lab artifact rebuild --day 09
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

        Save your raw operator proof in `build/day9/native_operator_evidence.json`.

        Allowed tools during this gate:

        - Azure Portal
        - `az`
        - `az rest`
        - raw KQL
        - `git`
        - `curl`
        - `nslookup` or `Resolve-DnsName`

        Tools banned during this gate:

        - `aegisap-lab`
        - helper verification wrappers
        - canned step-by-step answer keys

        Wrappers stay banned until both raw evidence files are complete. After that,
        they may be used only for artifact rebuild, mastery, or reset flows.

        Day 9 native evidence is blocking, must include two native commands plus one
        raw KQL query, and must be replay-ready for the Day 10 CAB review.
        """
    )
    return


@app.cell
def _chaos_gate(mo):
    mo.md(
        """
        ## Chaos Gate

        Failure signal: Routing or caching pushes the workload outside the cost ceiling while inherited infrastructure posture still has to hold.

        Starting signal: Routing telemetry shows risky work landing on the wrong tier while cost controls drift.

        Expected recovery artifact: `build/day9/routing_report.json`

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


if __name__ == "__main__":
    app.run()
