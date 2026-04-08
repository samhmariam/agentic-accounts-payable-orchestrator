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

    from aegisap.day_01.normalizers import parse_money
    from aegisap.day_01.service import IntakeReject, canonicalize_with_candidate
    from aegisap.training.labs import load_candidate, load_invoice_package

    return (
        IntakeReject,
        canonicalize_with_candidate,
        json,
        load_candidate,
        load_invoice_package,
        mo,
        parse_money,
        repo_root,
    )


@app.cell
def _title(mo):
    mo.md(
        """
        # Day 1 - Agentic Systems Fundamentals, Business Value, and FDE Judgment

        Primary learner entrypoint: `modules/day_01_trust_boundary/README.md`. Read the customer context and file manifest there before you start the incident.

        Day 1 is no longer a conceptual tour. You are responding to a real intake failure,
        proving where the break lives, prototyping the repair in the notebook, and then
        shipping the fix in the production codebase.
        """
    )
    return


@app.cell
def _incident(mo):
    mo.md(
        """
        ## Incident

        A valid European supplier invoice is being rejected at the trust boundary after a
        recent change. The finance team does not care about the theory. They care that a
        real invoice with mixed separators like `1.250,00 EUR` no longer crosses the
        boundary safely.

        **What success looks like**

        - you can prove the failure is deterministic Python, not the model prompt
        - the repaired path still rejects malformed amounts and accepts valid locale input
        - the production tests are green before AP retries the invoice
        """
    )
    return


@app.cell
def _portal_investigation(mo):
    mo.md(
        """
        ## Portal Investigation

        Start in Azure before you blame the parser.

        1. Open the Foundry or Azure OpenAI deployment and confirm the extractor still returns the expected Day 1 candidate keys.
        2. Compare one raw model payload with the failing finance case. Capture the exact amount string the model produced.
        3. Confirm IAM and endpoint health are unchanged so you do not misclassify an identity or networking problem as a parsing bug.
        4. Write down the exact amount literal that crosses from extraction into deterministic normalization.

        **Infrastructure-first debugging rule**

        - Check identity and endpoint health before changing prompts.
        - Check data shape before changing policy.
        - Blame the model only after the deterministic boundary is proven correct.
        """
    )
    return


@app.cell
def _lab_repair_intro(mo):
    mo.md(
        """
        ## Lab Repair

        Use this section as a scratchpad only. The goal is to prove a safe fix reactively
        before you touch the production files.
        """
    )
    return


@app.cell
def _amount_input(mo):
    sample_amount = mo.ui.text(
        value="1.250,00 EUR",
        label="Prototype with the amount string from the customer incident",
    )
    sample_amount
    return (sample_amount,)


@app.cell
def _amount_preview(mo, parse_money, sample_amount):
    amount_text = sample_amount.value.strip()
    try:
        parsed = parse_money(amount_text)
        panel = mo.callout(
            mo.md(
                f"""
                `parse_money("{amount_text}")` returned:

                ```text
                {parsed}
                ```
                """
            ),
            kind="success",
        )
    except Exception as exc:
        panel = mo.callout(
            mo.md(
                f"""
                The prototype failed with:

                ```text
                {exc}
                ```
                """
            ),
            kind="danger",
        )
    panel
    return


@app.cell
def _fixture_walkthrough(
    IntakeReject,
    canonicalize_with_candidate,
    json,
    load_candidate,
    load_invoice_package,
    mo,
    repo_root,
):
    package = load_invoice_package(repo_root / "fixtures" / "locale_mismatch" / "package.json")
    candidate = load_candidate(repo_root / "fixtures" / "locale_mismatch" / "candidate.json")

    try:
        canonical = canonicalize_with_candidate(package, candidate)
        result = mo.callout(
            mo.md(
                f"""
                The locale-mismatch fixture currently canonicalizes to:

                ```json
                {json.dumps(canonical.model_dump(mode="json"), indent=2)}
                ```
                """
            ),
            kind="success",
        )
    except IntakeReject as exc:
        result = mo.callout(
            mo.md(
                f"""
                The fixture is currently rejected:

                ```text
                {exc}
                ```
                """
            ),
            kind="danger",
        )

    result
    return


@app.cell
def _codification_bridge(mo):
    mo.md(
        """
        ## Why This Fails In Prod

        List three specific ways this notebook logic fails in an Azure Container App. You must reference at least one Azure limit (memory, timeout, or ephemeral storage) and one concurrency issue.

        ## Codification Bridge

        Treat the portal and notebook as evidence, not as the fix.

        - Portal state: the extractor and endpoint health are fine, but the locale-formatted amount crossing the deterministic boundary is not handled safely.
        - Notebook proof: `parse_money(...)` and the fixture walkthrough prove whether the break lives in normalization or the reject path.
        - Permanent repo change: `src/aegisap/day_01/normalizers.py` and, if needed, `src/aegisap/day_01/service.py`.

        Rosetta Stone: `notebooks/bridges/day01_trust_boundary.md`
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

        Your prototype is only a hypothesis until the real code changes land in the repo.
        Open the production files in your editor and implement the fix there:

        - `src/aegisap/day_01/normalizers.py`
        - `src/aegisap/day_01/service.py` if the rejection path or exception handling needs adjustment

        ### Export to Production

        - Which exact amount literal caused the failure?
        - What exact normalization or rejection rule must change in `src/aegisap/day_01/normalizers.py` or `src/aegisap/day_01/service.py`?
        - Which test and rebuilt artifact prove the change is permanent?

        After the code change, run the terminal verification commands below. Do not proceed
        until the tests are green.
        """
    )
    return


@app.cell
def _verification(repo_root, mo):
    artifact_path = repo_root / "build" / "day1" / "golden_thread_day1.json"
    artifact_note = (
        f"Current artifact present: `{artifact_path.relative_to(repo_root)}`"
        if artifact_path.exists()
        else "Artifact missing: rerun the Day 1 fixture path after the repair."
    )
    mo.md(
        f"""
        ## Verification

        Run these commands in the terminal, not in this notebook:

        ```bash
        uv run python -m pytest tests/test_day_01_money.py tests/test_day_01_fixtures.py -q
        uv run aegisap-lab artifact rebuild --day 01
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

        Failure signal: A locale-formatted invoice amount is rejected even though the extraction payload and endpoint health are clean.

        Diagnostic surface: Foundry extraction payload, notebook fixture replay, and trust-boundary parser behavior.

        Expected recovery artifact: `build/day1/golden_thread_day1.json`

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

        - [ ] Reproduced the locale regression from the customer incident
        - [ ] Prototyped the deterministic fix in the notebook scratchpad
        - [ ] Implemented the real patch in `src/`
        - [ ] Ran Day 1 tests and fixture intake from the terminal
        - [ ] Prepared PR evidence for hostile review
        """
    )
    return


if __name__ == "__main__":
    app.run()
