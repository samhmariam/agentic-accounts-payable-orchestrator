# Day 6 — Policy Review & Graceful Refusal
# ==========================================
# Test policy enforcement, prompt-injection detection, authority-boundary
# checks, and typed refusal outcomes — including an adversarial lab that
# batch-runs all 20 malicious cases.
# 
# Run:
#     marimo edit notebooks/day6_policy_review.py

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
    # Day 6 — Policy Review & Graceful Refusal

    **What you will learn**:
    - How policy rules are declared as typed `PolicyReference` objects — not inline strings
    - How `detect_prompt_injection()` catches override and hearsay-approval patterns
    - How `evaluate_authority_boundary()` scores whether the proposed action is in scope
    - Why **three typed outcomes** are safer than a boolean: `approved_to_proceed` /
      `needs_human_review` / `not_authorised_to_continue`
    - The adversarial lab: 20 malicious cases across 5 attack buckets
    """)
    return


@app.cell
def _lab_contract(mo):
    from _shared.lab_guide import render_lab_overview

    render_lab_overview(
        mo,
        prerequisites=[
            "Policy fixtures are present under `fixtures/day06`.",
            "If you are following the full cumulative path, Day 5 produced `build/day5/golden_thread_day5_resumed.json`.",
            "The adversarial cases file exists if you want to run the malicious-case batch.",
        ],
        required_inputs=[
            "A Day 6 fixture or custom `Day6ReviewInput` payload.",
        ],
        required_env_vars=[],
        expected_artifact="build/day6/golden_thread_day6.json",
        pass_criteria=[
            "The notebook produces one of the three typed policy outcomes.",
            "The adversarial summary shows whether malicious cases are blocked correctly.",
            "The Day 6 artifact is written for Day 10 refusal-safety gating.",
        ],
        implementation_exercise=(
            "Run or extend a refusal scenario and prove the decision object still explains "
            "the reason codes, blocking conditions, and citations."
        ),
    )
    return


@app.cell
def _fixture_picker(mo):
    from pathlib import Path as _P
    import os as _os

    fixtures_dir = _P(__file__).resolve().parents[1] / "fixtures" / "day06"
    fixture_names = sorted(p.stem for p in fixtures_dir.glob(
        "*.json")) if fixtures_dir.exists() else []

    scenario = mo.ui.dropdown(
        options=["-- custom JSON below --"] + fixture_names,
        value=fixture_names[0] if fixture_names else "-- custom JSON below --",
        label="Fixture Scenario",
    )
    custom_json = mo.ui.code_editor(
        value="",
        language="json",
        label="Or paste a Day6ReviewInput JSON",
    )
    mo.vstack([mo.md("## 1 — Select Scenario"), scenario, custom_json])
    return custom_json, fixtures_dir, scenario


@app.cell
def _load_review_input(custom_json, fixtures_dir, mo, scenario):
    import json as _j
    from pathlib import Path as _P
    from aegisap.day6.state.models import Day6ReviewInput

    def _parse_review_input(raw: str) -> Day6ReviewInput:
        payload = _j.loads(raw)
        return Day6ReviewInput.model_validate(payload.get("review_input", payload))

    review_input = None
    load_error = None
    if scenario.value and scenario.value != "-- custom JSON below --":
        try:
            raw = (_P(fixtures_dir) / f"{scenario.value}.json").read_text()
            review_input = _parse_review_input(raw)
        except Exception as exc:  # noqa: BLE001
            load_error = str(exc)
    elif custom_json.value.strip():
        try:
            review_input = _parse_review_input(custom_json.value)
        except Exception as exc:  # noqa: BLE001
            load_error = str(exc)

    mo.stop(review_input is None and not load_error,
            mo.md("Select a fixture or paste JSON."))
    if load_error:
        mo.stop(True, mo.callout(
            mo.md(f"**Load error**: `{load_error}`"), kind="danger"))

    mo.vstack([mo.md("## 2 — Review Input"), mo.tree(
        review_input.model_dump(mode="json"))])
    return (review_input,)


@app.cell
def _policy_registry(mo):
    from aegisap.day6.policy.registry import build_policy_context
    # Show static policy table without requiring full Day4 state
    from aegisap.day6.state.models import PolicyReference
    policies = [
        {"Policy ID": "POL-CTRL-001",
            "Title": "Control plane immutability", "Blocking": "Yes"},
        {"Policy ID": "POL-AUTH-004",
            "Title": "Approval channel registration", "Blocking": "Yes"},
        {"Policy ID": "POL-EVID-002",
            "Title": "Mandatory evidence present", "Blocking": "Yes"},
        {"Policy ID": "POL-SCOPE-003",
            "Title": "System authority boundary", "Blocking": "Yes"},
    ]
    mo.vstack([
        mo.md("## 3 — Policy Registry"),
        mo.ui.table(policies, selection=None),
    ])
    return


@app.cell
def _injection_scan(mo, review_input):
    from aegisap.day6.review.prompt_injection import detect_prompt_injection
    from aegisap.day6.export import injection_signals_to_table

    signals = detect_prompt_injection(review_input)
    rows = injection_signals_to_table(signals)

    if signals:
        _out = mo.vstack([
            mo.md("## 4 — Prompt-Injection Scan"),
            mo.callout(
                mo.md(f"**{len(signals)} injection signal(s) detected.**"), kind="danger"),
            mo.table(rows, selection=None),
        ])
    else:
        _out = mo.vstack([
            mo.md("## 4 — Prompt-Injection Scan"),
            mo.callout(mo.md("No injection signals detected."),
                       kind="success"),
        ])
    _out
    return (signals,)


@app.cell
def _authority_check(mo, review_input, signals):
    from aegisap.day6.review.authority_boundary import evaluate_authority_boundary

    auth_check = evaluate_authority_boundary(
        review_input,
        injection_detected=bool(signals),
    )
    mo.vstack([
        mo.md("## 5 — Authority Boundary Check"),
        mo.tree(auth_check.model_dump(mode="json")),
    ])
    return (auth_check,)


@app.cell
def _evidence_check(mo, review_input, signals):
    from aegisap.day6.review.evidence_sufficiency import evaluate_evidence_sufficiency

    conflicting_claims = [
        claim.claim_id
        for claim in review_input.claim_ledger
        if claim.conflicting_evidence_ids
    ]
    ev_check = evaluate_evidence_sufficiency(
        review_input,
        injection_detected=bool(signals),
        conflicting_claims=conflicting_claims,
    )
    mo.vstack([
        mo.md("## 6 — Evidence Sufficiency"),
        mo.tree(ev_check.model_dump(mode="json")),
    ])
    return (ev_check,)


@app.cell
def _reflection_and_outcome(auth_check, ev_check, mo, review_input, signals):
    from aegisap.day6.review.reflection import build_reflection_review
    from aegisap.day6.review.decision_mapping import map_review_outcome
    from aegisap.day6.export import refusal_to_audit_row

    reflection = build_reflection_review(
        review_input,
        evidence_assessment=ev_check,
        authorisation_check=auth_check,
        injection_signals=signals,
    )
    outcome = map_review_outcome(
        review_input,
        evidence_assessment=ev_check,
        authorisation_check=auth_check,
        injection_signals=signals,
        reflection_review=reflection,
    )
    audit_row = refusal_to_audit_row(outcome, review_input)

    _outcome_val = str(getattr(outcome, "outcome", outcome))
    _kind = (
        "success" if "approved" in _outcome_val
        else "warn" if "human" in _outcome_val
        else "danger"
    )

    mo.vstack([
        mo.md("## 7 — Decision Outcome"),
        mo.callout(mo.md(f"**`{_outcome_val}`**"), kind=_kind),
        mo.accordion({
            "Full reflection review": mo.tree(reflection.model_dump(mode="json")),
            "Audit row": mo.tree(audit_row),
        }),
    ])
    return audit_row, outcome


@app.cell
def _adversarial_lab(mo):
    def _():
        import json as _j
        from pathlib import Path as _P
        from aegisap.day6.review.prompt_injection import detect_prompt_injection as _detect_prompt_injection
        from aegisap.day6.review.authority_boundary import evaluate_authority_boundary as _evaluate_authority_boundary
        from aegisap.day6.review.evidence_sufficiency import evaluate_evidence_sufficiency as _evaluate_evidence_sufficiency
        from aegisap.day6.review.reflection import build_reflection_review as _build_reflection_review
        from aegisap.day6.review.decision_mapping import map_review_outcome as _map_review_outcome
        from aegisap.day6.state.models import Day6ReviewInput as _Day6ReviewInput

        malicious_path = _P(__file__).resolve(
        ).parents[1] / "evals" / "malicious_cases.jsonl"
        mo.stop(not malicious_path.exists(), mo.callout(
            mo.md("malicious_cases.jsonl not found."), kind="warn"))

        cases = [_j.loads(line) for line in malicious_path.read_text(
        ).splitlines() if line.strip()]

        results_by_bucket: dict[str, dict[str, int]] = {}
        for case in cases:
            bucket = case.get("bucket", "unknown")
            if bucket not in results_by_bucket:
                results_by_bucket[bucket] = {"pass": 0, "fail": 0}
            try:
                ri = _Day6ReviewInput.model_validate(case.get("review_input", case))
                sigs = _detect_prompt_injection(ri)
                conflicting_claims = [
                    claim.claim_id
                    for claim in ri.claim_ledger
                    if claim.conflicting_evidence_ids
                ]
                auth = _evaluate_authority_boundary(
                    ri,
                    injection_detected=bool(sigs),
                )
                ev = _evaluate_evidence_sufficiency(
                    ri,
                    injection_detected=bool(sigs),
                    conflicting_claims=conflicting_claims,
                )
                refl = _build_reflection_review(
                    ri,
                    evidence_assessment=ev,
                    authorisation_check=auth,
                    injection_signals=sigs,
                )
                out = _map_review_outcome(
                    ri, evidence_assessment=ev, authorisation_check=auth, injection_signals=sigs, reflection_review=refl)
                outcome_val = str(getattr(out, "outcome", out))
                expected = case.get("expected_outcome",
                                    "not_authorised_to_continue")
                if outcome_val == expected:
                    results_by_bucket[bucket]["pass"] += 1
                else:
                    results_by_bucket[bucket]["fail"] += 1
            except Exception:  # noqa: BLE001
                results_by_bucket[bucket]["fail"] += 1

        summary_rows = [
            {
                "Bucket": b,
                "Pass": v["pass"],
                "Fail": v["fail"],
                "Pass Rate": f"{100 * v['pass'] // max(v['pass'] + v['fail'], 1)}%",
            }
            for b, v in sorted(results_by_bucket.items())
        ]

        all_pass = all(r["Fail"] == 0 for r in summary_rows)
        return mo.vstack([
            mo.md("## 8 — Adversarial Lab Results"),
            mo.ui.table(summary_rows, selection=None),
            mo.callout(mo.md("All adversarial cases passed."), kind="success")
            if all_pass
            else mo.callout(mo.md("Some adversarial cases failed — review the Fail column."), kind="danger"),
        ])


    _()
    return


@app.cell
def _persist(audit_row, mo, outcome):
    import json as _j
    from pathlib import Path as _P

    out_dir = _P(__file__).resolve().parents[1] / "build" / "day6"
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact = {
        "outcome": str(getattr(outcome, "outcome", outcome)),
        "audit_row": audit_row,
        "full_outcome": outcome.model_dump(mode="json") if hasattr(outcome, "model_dump") else str(outcome),
    }
    out_path = out_dir / "golden_thread_day6.json"
    out_path.write_text(_j.dumps(artifact, indent=2, default=str))

    mo.vstack([
        mo.callout(mo.md(
            "Artifact written to `build/day6/golden_thread_day6.json`"), kind="success"),
        mo.download(
            data=_j.dumps(artifact, indent=2, default=str).encode(),
            filename="golden_thread_day6.json",
            mimetype="application/json",
            label="Download golden_thread_day6.json",
        ),
    ])
    return


@app.cell
def _ready_for_next_day(mo):
    from _shared.lab_guide import render_readiness_check

    render_readiness_check(
        mo,
        artifact_relpath="build/day6/golden_thread_day6.json",
        next_day="Day 7 or Day 10 gate validation",
        recovery_command="marimo edit notebooks/day6_policy_review.py",
    )
    return


if __name__ == "__main__":
    app.run()
