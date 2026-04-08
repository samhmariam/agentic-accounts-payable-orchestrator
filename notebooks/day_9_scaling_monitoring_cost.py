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

    from aegisap.cache.cache_policy import evaluate_cache_policy
    from aegisap.cost.budget_gate import check_budget
    from aegisap.routing.routing_policy import route_task

    return check_budget, evaluate_cache_policy, json, mo, repo_root, route_task


@app.cell
def _title(mo):
    mo.md(
        """
        # Day 9 — Routing Regression Rescue Mission

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
def _codification_bridge(mo):
    mo.md(
        """
        ## Codification Bridge

        Treat the routing telemetry and notebook previews as the same control decision.

        - Portal state: risky work is staying on the wrong deployment tier.
        - Notebook proof: the routing, cache, and budget preview shows whether routing, cache policy, or budget framing drifted.
        - Permanent repo change: `src/aegisap/routing/routing_policy.py`, `src/aegisap/cache/cache_policy.py`, and, if needed, `src/aegisap/cost/budget_gate.py`.

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

        Move into the real routing boundary and implement the repair in:

        - `src/aegisap/routing/routing_policy.py`
        - `src/aegisap/cache/cache_policy.py` if cache bypass rules drifted too
        - `src/aegisap/cost/budget_gate.py` only if the budget framing is wrong

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
    artifact_note = (
        f"Current artifact present: `{artifact_path.relative_to(repo_root)}`"
        if artifact_path.exists()
        else "Artifact missing: rebuild the Day 9 artifact after the repair."
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
        """
    )
    return


@app.cell
def _pr_defense(mo):
    mo.md(
        """
        ## PR Defense

        Your pull request must include:

        - the exact risk flag or confidence rule that caused the unsafe light-tier route
        - why cheaper routing is subordinate to high-risk safety controls
        - proof that cache and budget behavior remain explicit after the fix
        - one sentence on the business blast radius of letting high-risk work ride the cheap tier
        """
    )
    return


if __name__ == "__main__":
    app.run()
