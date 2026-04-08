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

    from aegisap.audit.events import build_audit_event
    from aegisap.security.redaction import redact_text

    return build_audit_event, json, mo, redact_text, repo_root


@app.cell
def _title(mo):
    mo.md(
        """
        # Day 7 - Evaluation, Guardrails, Structured Refusal, and Slice Governance

        Primary learner entrypoint: `modules/day_07_eval_guardrails/README.md`. Read the customer context and file manifest there before you start the incident.

        Day 7 starts with a safety failure: sensitive approval evidence is leaking
        through the redaction boundary into audit material. Your job is to prove the
        leak, repair the guardrail, and defend why the fix blocks both PII exposure
        and downstream policy drift.
        """
    )
    return


@app.cell
def _incident(mo):
    mo.md(
        """
        ## Incident

        Internal audit found a refusal event whose evidence summary still exposed
        an email address, a phone number, and bank-account digits.

        **What success looks like**

        - sensitive evidence is redacted before audit persistence
        - the redaction boundary still preserves enough context for investigation
        - the Day 7 refusal and governance artifacts explain why this is release-blocking
        """
    )
    return


@app.cell
def _portal_investigation(mo):
    mo.md(
        """
        ## Portal Investigation

        Start from the live evidence before you touch the code:

        1. Open Application Insights or Log Analytics and locate the refusal event tied to the customer complaint.
        2. Confirm which fields still expose raw identifiers in traces, logs, or audit summaries.
        3. Compare the leaked payload to the control objective in the Day 7 governance packet.
        4. Capture whether the fault is in redaction, audit shaping, or both.
        """
    )
    return


@app.cell
def _lab_intro(mo):
    mo.md(
        """
        ## Lab Repair

        Use the notebook to prove the leak and the repaired behavior in-memory only.
        The real fix belongs in the repo, not in notebook cells.
        """
    )
    return


@app.cell
def _controls(mo):
    evidence = mo.ui.text_area(
        value=(
            "Blocked because finance@example.com requested approval via phone +44 20 7946 0958 "
            "for VAT GB123456789 and account 12345678."
        ),
        label="Evidence summary to redact",
        rows=4,
    )
    mo.vstack([evidence])
    return (evidence,)


@app.cell
def _redaction_preview(json, mo, redact_text, evidence):
    redacted, changed = redact_text(evidence.value)
    mo.callout(
        mo.md(
            f"""
            Redaction preview:

            ```json
            {json.dumps({"changed": changed, "redacted": redacted}, indent=2)}
            ```
            """
        ),
        kind="info",
    )
    return


@app.cell
def _audit_preview(build_audit_event, json, mo, evidence):
    event = build_audit_event(
        workflow_run_id="case-training-guardrail",
        thread_id="thread-training-guardrail",
        state_version=9,
        actor_type="managed_identity",
        actor_id="runtime-api",
        action_type="refusal",
        decision_outcome="not_authorised_to_continue",
        evidence_summary=evidence.value,
        evidence_refs=["email_017", "POL-AUTH-004"],
        error_code="UNVERIFIED_APPROVAL_CLAIM",
        trace_id="trace-training-guardrail",
    )
    mo.callout(
        mo.md(
            f"""
            Audit-event preview:

            ```json
            {json.dumps(event.model_dump(mode="json"), indent=2)}
            ```
            """
        ),
        kind="success",
    )
    return


@app.cell
def _codification_bridge(mo):
    mo.md(
        """
        ## Why This Fails In Prod

        List three specific ways this notebook logic fails in an Azure Container App. You must reference at least one Azure limit (memory, timeout, or ephemeral storage) and one concurrency issue.

        ## Codification Bridge

        Treat the leaked telemetry and notebook previews as one guardrail failure.

        - Portal state: traces or logs still expose raw identifiers.
        - Notebook proof: the redaction preview and audit-event preview show whether the leak is in masking, audit shaping, or both.
        - Permanent repo change: `src/aegisap/security/redaction.py`, `src/aegisap/audit/events.py`, and, if needed, `src/aegisap/audit/writer.py`.
        - Drift-repair targets: `src/aegisap/day3/policies/source_authority_rules.yaml` and `src/aegisap/day3/retrieval/authority_policy.py` if the probabilistic authority slice is failing.

        Rosetta Stone: `notebooks/bridges/day07_guardrail_redaction.md`
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

        Move into the real guardrail boundary and implement the repair in:

        - `src/aegisap/security/redaction.py`
        - `src/aegisap/audit/events.py` if the audit payload needs stricter shaping
        - `src/aegisap/audit/writer.py` only if the persistence boundary is wrong
        - `src/aegisap/day3/policies/source_authority_rules.yaml` and `src/aegisap/day3/retrieval/authority_policy.py` when the drift drill shows authoritative evidence is losing on the eval slice

        Then update the written Day 7 evidence:

        - `docs/curriculum/artifacts/day07/EVAL_GOVERNANCE_POLICY.md`
        - `docs/curriculum/artifacts/day07/REFUSAL_REASON_CODE_CATALOG.md`
        - `docs/curriculum/artifacts/day07/SLICE_REGRESSION_DECISION_LOG.md`

        ### Export to Production

        - Which exact field or token leaked in the live evidence?
        - Which file permanently removes the leak before audit persistence?
        - Which verification proves operator context survives without exposing raw identifiers?
        """
    )
    return


@app.cell
def _verification(repo_root, mo):
    artifact_path = repo_root / "build" / "day7" / "eval_report.json"
    artifact_note = (
        f"Current artifact present: `{artifact_path.relative_to(repo_root)}`"
        if artifact_path.exists()
        else "Artifact missing: rebuild the Day 7 artifact after the repair."
    )
    mo.md(
        f"""
        ## Verification

        Run these commands in the terminal:

        ```bash
        uv run python -m pytest tests/day7/security/test_redaction.py tests/day7/audit/test_audit_row_written_for_sensitive_decision.py -q
        uv run aegisap-lab artifact rebuild --day 07
        uv run python evals/run_eval_suite.py --suite all --synthetic-cases build/day7/synthetic_cases_drift.jsonl --malicious-cases build/day7/malicious_cases_drift.jsonl --thresholds evals/score_thresholds.yaml --output build/day7/prompt_drift_report.json --enforce-thresholds
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

        Failure signal: A probabilistic authority drift keeps the app running while Day 7 eval thresholds quietly fall out of policy.

        Diagnostic surface: Content-safety notebook evidence, evaluation traces, drift cases under `build/day7/`, Day 3 authority policy, and audit writer outputs.

        Expected recovery artifact: `build/day7/prompt_drift_report.json`

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
