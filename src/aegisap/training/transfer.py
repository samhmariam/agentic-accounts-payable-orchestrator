from __future__ import annotations

from pathlib import Path
from typing import Any

from aegisap.common.paths import repo_root
from aegisap.training.artifacts import build_root, write_json_artifact
from aegisap.transfer import adapt_claim_to_control_signals, evaluate_control_signals, load_claim_payload


def build_day7_claims_transfer_report(
    *,
    fixtures_dir: str | Path | None = None,
    artifact_name: str = "claims_transfer_report",
) -> tuple[Path, dict[str, Any]]:
    root = Path(fixtures_dir) if fixtures_dir is not None else (
        repo_root(__file__) / "fixtures" / "capstone_b" / "claims_intake"
    )

    cases: list[dict[str, Any]] = []
    seen_claim_numbers: set[str] = set()
    for fixture_path in sorted(root.glob("claim_*.json")):
        payload = load_claim_payload(fixture_path)
        signals = adapt_claim_to_control_signals(payload, known_duplicates=set(seen_claim_numbers))
        decision = evaluate_control_signals(signals)
        cases.append(
            {
                "fixture": str(fixture_path),
                "case_id": signals.case_id,
                "claim_number": signals.claim_number,
                "control_signals": signals.model_dump(mode="json"),
                "decision": decision.model_dump(mode="json"),
            }
        )
        seen_claim_numbers.add(signals.claim_number)

    report = {
        "day": 7,
        "title": "Claims transfer adapter proof",
        "adapter_boundary": "claims_payload -> ControlSignals -> fail_closed_decision",
        "fixtures_dir": str(root),
        "total_cases": len(cases),
        "cases": cases,
    }
    artifact_path = build_root("day7") / f"{artifact_name}.json"
    return write_json_artifact(artifact_path, report), report
