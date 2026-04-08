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
        # Day 7 — Guardrail Breach Rescue Mission

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
def _production_patch(mo):
    mo.md(
        """
        ## Production Patch

        This section is **markdown-only**.

        Do not edit repo files from this notebook.

        Move into the real guardrail boundary and implement the repair in:

        - `src/aegisap/security/redaction.py`
        - `src/aegisap/audit/events.py` if the audit payload needs stricter shaping
        - `src/aegisap/audit/writer.py` only if the persistence boundary is wrong

        Then update the written Day 7 evidence:

        - `docs/curriculum/artifacts/day07/EVAL_GOVERNANCE_POLICY.md`
        - `docs/curriculum/artifacts/day07/REFUSAL_REASON_CODE_CATALOG.md`
        - `docs/curriculum/artifacts/day07/SLICE_REGRESSION_DECISION_LOG.md`
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

        - the exact field that was leaking before the repair
        - why this is a guardrail failure, not just a cosmetic logging bug
        - proof that the repaired redaction still preserves operator-usable context
        - one sentence explaining the business blast radius of audit evidence leaking raw identifiers
        """
    )
    return


if __name__ == "__main__":
    app.run()
