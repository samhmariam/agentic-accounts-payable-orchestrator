import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _bootstrap():
    import os
    import sys
    from pathlib import Path

    import marimo as mo

    repo_root = Path(__file__).resolve().parents[1]
    for candidate in [repo_root / "src", repo_root / "notebooks"]:
        text = str(candidate)
        if text not in sys.path:
            sys.path.insert(0, text)

    from aegisap.observability.retry_policy import RetryPolicy, execute_with_retry
    from aegisap.resilience.backpressure import evaluate_backpressure

    return RetryPolicy, evaluate_backpressure, execute_with_retry, mo, os, repo_root


@app.cell
def _title(mo):
    mo.md(
        """
        # Day 2 - Resilience Under Load, NFR Enforcement, and Ownership

        Primary learner entrypoint: `modules/day_02_resilience_ownership/README.md`. Read the customer context and file manifest there before you start the incident.

        Day 2 now starts where real FDE work starts: a customer has flooded the
        orchestrator, Azure OpenAI is returning `429` throttle responses, and the
        protected planning path is not behaving safely under pressure.
        """
    )
    return


@app.cell
def _incident(mo):
    mo.md(
        """
        ## Incident

        Operations is seeing sustained `429` responses during a bulk replay, and the
        planning path is not queueing safely when capacity is saturated.

        **What success looks like**

        - idempotent paths retry quota throttles correctly
        - protected paths queue instead of pretending capacity still exists
        - the repair is defended with code, tests, and updated NFR or ADR evidence
        """
    )
    return


@app.cell
def _portal_investigation(mo):
    mo.md(
        """
        ## Portal Investigation

        Before you touch the code, inspect the live control plane:

        1. Open the Azure OpenAI deployment metrics and confirm the throttling signal is real.
        2. Inspect Application Insights or Azure Monitor traces for retry count, queue delay, and dependency failures.
        3. Confirm identity and quota configuration did not drift before you classify the problem as an application bug.
        4. Capture the exact evidence that proves the planning path is protected and should never silently fail open.
        """
    )
    return


@app.cell
def _lab_repair_intro(mo):
    mo.md(
        """
        ## Lab Repair

        Prototype the resilience behavior here, then move the real fix into the codebase.
        """
    )
    return


@app.cell
def _backpressure_inputs(mo):
    task_class = mo.ui.dropdown(
        options=["plan", "extract", "compliance_review", "reflection"],
        value="plan",
        label="Task class",
    )
    deployment_tier = mo.ui.dropdown(
        options=["strong", "light"],
        value="strong",
        label="Deployment tier",
    )
    active_inflight = mo.ui.slider(
        start=0,
        stop=6,
        step=1,
        value=2,
        label="Active in-flight calls",
    )
    strong_limit = mo.ui.slider(
        start=1,
        stop=4,
        step=1,
        value=2,
        label="Strong-tier concurrency limit",
    )
    light_limit = mo.ui.slider(
        start=1,
        stop=8,
        step=1,
        value=4,
        label="Light-tier concurrency limit",
    )

    mo.vstack([task_class, deployment_tier, active_inflight, strong_limit, light_limit])
    return active_inflight, deployment_tier, light_limit, strong_limit, task_class


@app.cell
def _backpressure_preview(
    active_inflight,
    deployment_tier,
    evaluate_backpressure,
    light_limit,
    mo,
    os,
    strong_limit,
    task_class,
):
    os.environ["AEGISAP_BACKPRESSURE_ENABLED"] = "true"
    os.environ["AEGISAP_STRONG_MODEL_MAX_CONCURRENCY"] = str(strong_limit.value)
    os.environ["AEGISAP_CHEAP_MODEL_MAX_CONCURRENCY"] = str(light_limit.value)

    decision = evaluate_backpressure(
        task_class=task_class.value,
        deployment_tier=deployment_tier.value,
        active_inflight=active_inflight.value,
    )

    mo.callout(
        mo.md(
            f"""
            Backpressure decision:

            - `allow_execution={decision.allow_execution}`
            - `queue_required={decision.queue_required}`
            - `queue_delay_ms={decision.queue_delay_ms}`
            - `reason={decision.reason}`
            """
        ),
        kind="info",
    )
    return


@app.cell
def _retry_inputs(mo):
    failures_before_success = mo.ui.slider(
        start=0,
        stop=4,
        step=1,
        value=2,
        label="Number of synthetic 429 failures before recovery",
    )
    idempotent = mo.ui.dropdown(
        options=["true", "false"],
        value="true",
        label="Treat the path as idempotent?",
    )
    mo.vstack([failures_before_success, idempotent])
    return failures_before_success, idempotent


@app.cell
def _retry_preview(RetryPolicy, execute_with_retry, failures_before_success, idempotent, mo):
    attempts = {"count": 0}

    def flaky_call() -> str:
        attempts["count"] += 1
        if attempts["count"] <= failures_before_success.value:
            raise RuntimeError("429 quota throttle from azure openai")
        return "recovered"

    try:
        result = execute_with_retry(
            flaky_call,
            policy=RetryPolicy(max_attempts=4, initial_backoff_ms=0, max_backoff_ms=0, deadline_ms=1_000),
            node_name="planner_call",
            dependency_name="azure_openai",
            idempotent=idempotent.value == "true",
            sleep_fn=lambda _seconds: None,
            random_fn=lambda: 0.5,
        )
        output = mo.callout(
            mo.md(
                f"""
                Retry prototype completed successfully.

                - `result={result}`
                - `attempts={attempts["count"]}`
                """
            ),
            kind="success",
        )
    except Exception as exc:
        output = mo.callout(
            mo.md(
                f"""
                Retry prototype failed.

                - `attempts={attempts["count"]}`
                - `error={exc}`
                """
            ),
            kind="warn",
        )
    output
    return


@app.cell
def _codification_bridge(mo):
    mo.md(
        """
        ## Why This Fails In Prod

        List three specific ways this notebook logic fails in an Azure Container App. You must reference at least one Azure limit (memory, timeout, or ephemeral storage) and one concurrency issue.

        ## Codification Bridge

        Treat the portal metrics and notebook controls as one chain.

        - Portal state: Azure metrics prove the `429` pressure is real and the planning path is under stress.
        - Notebook proof: the backpressure and retry previews show whether the safe fix belongs to queueing, retry policy, or both.
        - Permanent repo change: `src/aegisap/observability/retry_policy.py` and `src/aegisap/resilience/backpressure.py`.

        Rosetta Stone: `notebooks/bridges/day02_resilience_controls.md`
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

        STOP. Close this notebook.

        Open the exact relative filepath listed below in your IDE. Write the durable patch there, not inside Marimo.

        Move into the real codebase and repair the production implementation:

        - `src/aegisap/observability/retry_policy.py`
        - `src/aegisap/resilience/backpressure.py`

        Then update the evidence that explains the fix:

        - `docs/curriculum/artifacts/day02/NFR_REGISTER.md`
        - `docs/curriculum/artifacts/day02/ADR_001_SCOPE_AND_BOUNDARIES.md`

        ### Export to Production

        - Which telemetry signal proved quota pressure versus an auth problem?
        - Which exact rule belongs in `src/aegisap/observability/retry_policy.py` and which belongs in `src/aegisap/resilience/backpressure.py`?
        - What verification proves the protected path no longer fails open?

        Your code change is the repair. The Day 2 artifacts are the explanation that survives review.
        """
    )
    return


@app.cell
def _verification(repo_root, mo):
    artifact_path = repo_root / "build" / "day2" / "golden_thread_day2.json"
    artifact_note = (
        f"Current artifact present: `{artifact_path.relative_to(repo_root)}`"
        if artifact_path.exists()
        else "Artifact missing: regenerate the Day 2 workflow artifact after the repair."
    )
    mo.md(
        f"""
        ## Verification

        Run these commands in the terminal:

        ```bash
        uv run python -m pytest tests/day2/test_resilience_controls.py tests/day8/test_retry_policy.py -q
        uv run aegisap-lab artifact rebuild --day 02
        ```

        {artifact_note}
        """
    )
    return


@app.cell
def _chaos_gate(mo):
    mo.md(
        """
        ## Chaos Gate

        Failure signal: Retry policy and backpressure assumptions no longer match observed queue pressure and latency targets.

        Diagnostic surface: Azure OpenAI metrics, queue pressure notes, and the resilience policy code paths.

        Expected recovery artifact: `build/day2/golden_thread_day2.json`

        Time box: 20 minutes. If you miss it, stop and rerun the four pillars in `docs/curriculum/FDE_DEBUGGING_FRAMEWORK.md`.
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


@app.cell
def _summary(mo):
    mo.md(
        """
        ## Summary Checklist

        - [ ] Reproduced the 429 and backpressure failure
        - [ ] Prototyped the repair in Marimo
        - [ ] Patched the real resilience code in `src/`
        - [ ] Ran the Day 2 resilience tests from the terminal
        - [ ] Updated Day 2 evidence for PR review
        """
    )
    return


if __name__ == "__main__":
    app.run()
