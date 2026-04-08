from __future__ import annotations

import argparse
import json
from pathlib import Path

from aegisap.day_01.models import ExtractedInvoiceCandidate, InvoicePackageInput
from aegisap.day_01.service import canonicalize_with_candidate
from aegisap.day2.config import HIGH_VALUE_THRESHOLD, KNOWN_VENDORS, ROUTE_PRECEDENCE
from aegisap.day2.graph import build_graph
from aegisap.day2.state import WorkflowState, make_initial_state


def load_fixture_package(path: Path) -> InvoicePackageInput:
    with path.open("r", encoding="utf-8") as handle:
        return InvoicePackageInput.model_validate(json.load(handle))


def load_fixture_candidate(path: Path) -> ExtractedInvoiceCandidate:
    with path.open("r", encoding="utf-8") as handle:
        return ExtractedInvoiceCandidate.model_validate(json.load(handle))


def resolve_known_vendor(invoice_name: str, known_vendor: bool | None = None) -> bool:
    if known_vendor is not None:
        return known_vendor
    return invoice_name in KNOWN_VENDORS


def run_from_fixture(
    fixture_dir: Path, known_vendor: bool | None = None
) -> WorkflowState:
    package = load_fixture_package(fixture_dir / "package.json")
    candidate = load_fixture_candidate(fixture_dir / "candidate.json")
    invoice = canonicalize_with_candidate(package, candidate)
    state = make_initial_state(
        invoice,
        package_id=package.message_id,
        known_vendor=resolve_known_vendor(invoice.supplier_name, known_vendor),
        high_value_threshold=HIGH_VALUE_THRESHOLD,
        route_precedence=ROUTE_PRECEDENCE,
    )
    app = build_graph()
    result = app.invoke(state)
    if isinstance(result, WorkflowState):
        return result
    return WorkflowState.model_validate(result)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Day 2 fixture workflow directly for local debugging. The learner-facing training entrypoint is `uv run aegisap-lab incident start --day 02`."
    )
    parser.add_argument("fixture", help="fixture directory name under fixtures/day2")
    parser.add_argument(
        "--known-vendor",
        dest="known_vendor",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="override vendor approval status; defaults to inferring from KNOWN_VENDORS",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[3]
    fixture_dir = root / "fixtures" / "day2" / args.fixture
    state = run_from_fixture(fixture_dir, known_vendor=args.known_vendor)

    summary = {
        "workflow_id": state.workflow_id,
        "thread_id": state.thread_id,
        "invoice_id": state.invoice_id,
        "route": state.route,
        "route_reason": state.route_reason,
        "status": state.status,
        "completed_nodes": state.completed_nodes,
        "recommendations": [r.model_dump() for r in state.recommendations],
        "metrics": [m.model_dump() for m in state.node_metrics],
        "evidence": [e.model_dump() for e in state.evidence],
        "totals": {
            "latency_ms": state.total_latency_ms,
            "prompt_tokens": state.total_tokens_prompt,
            "completion_tokens": state.total_tokens_completion,
            "cost_usd": state.total_cost_usd,
        },
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
