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
        # Day 1 — Trust Boundary Rescue Mission

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
def _production_patch(mo):
    mo.md(
        """
        ## Production Patch

        This section is **markdown-only**.

        Do not edit repo files from this notebook.

        Your prototype is only a hypothesis until the real code changes land in the repo.
        Open the production files in your editor and implement the fix there:

        - `src/aegisap/day_01/normalizers.py`
        - `src/aegisap/day_01/service.py` if the rejection path or exception handling needs adjustment

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
def _pr_defense(mo):
    mo.md(
        """
        ## PR Defense

        Your pull request must include:

        - the exact failing signal you started from
        - why the bug lived in deterministic normalization instead of extraction or IAM
        - proof that the repaired path still rejects malformed amounts
        - one sentence on blast radius if the trust boundary were allowed to fail open
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
