#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _bootstrap_src_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify one live Day 3 Azure Search retrieval path.")
    parser.add_argument("--endpoint", default=os.getenv("AZURE_SEARCH_ENDPOINT", ""), help="Search endpoint")
    parser.add_argument("--index-name", default=os.getenv("AZURE_SEARCH_DAY3_INDEX", ""), help="Dedicated Day 3 Search index")
    return parser.parse_args()


def main() -> int:
    _bootstrap_src_path()
    args = parse_args()

    if not args.endpoint.strip():
        print("Missing AZURE_SEARCH_ENDPOINT for live Day 3 verification.", file=sys.stderr)
        return 2
    if not args.index_name.strip():
        print("Missing AZURE_SEARCH_DAY3_INDEX for live Day 3 verification.", file=sys.stderr)
        return 2

    from azure.search.documents.indexes import SearchIndexClient

    from aegisap.day3.graph import run_day3_workflow
    from aegisap.day3.retrieval.azure_ai_search_adapter import AzureAISearchLiveAdapter, _build_credential
    from aegisap.day3.retrieval.interfaces import build_retrieval_config

    credential = _build_credential()
    SearchIndexClient(endpoint=args.endpoint.rstrip("/"), credential=credential).get_index(args.index_name)

    adapter = AzureAISearchLiveAdapter(endpoint=args.endpoint, index_name=args.index_name, credential=credential)
    results = adapter.search(query="Acme Office Supplies bank change 4421", max_results=5)
    if not results:
        print(f"No live Day 3 Search results returned from '{args.index_name}'.", file=sys.stderr)
        return 1

    invoice = {
        "case_id": "CASE-3001",
        "invoice_id": "INV-3001",
        "invoice_date": "2026-03-01",
        "vendor_id": "VEND-001",
        "vendor_name": "Acme Office Supplies",
        "po_number": "PO-9001",
        "amount": 12500.00,
        "currency": "GBP",
        "bank_account_last4": "4421",
    }
    retrieval_config = build_retrieval_config(
        "azure_search_live",
        search_endpoint=args.endpoint,
        search_index_name=args.index_name,
    )
    state = run_day3_workflow(
        invoice,
        retrieval_mode="azure_search_live",
        retrieval_config=retrieval_config,
    )
    decision = state.agent_findings["decision"]
    vendor_risk = state.agent_findings["vendor_risk"]

    if decision.recommendation != "approve":
        print(f"Unexpected decision recommendation: {decision.recommendation}", file=sys.stderr)
        return 1
    if "vendor-master-VEND-001" not in decision.evidence_ids:
        print("Live run did not cite the authoritative vendor master record.", file=sys.stderr)
        return 1
    if not any(item.backend == "azure_ai_search_live" for item in state.bucket("vendor", "policy")):
        print("Live run did not record any Azure Search-backed evidence.", file=sys.stderr)
        return 1
    if "doc-onboarding-old-bank" not in vendor_risk.evidence_ids:
        print("Live run did not surface the stale onboarding email as historical context.", file=sys.stderr)
        return 1

    print(f"PASS: Day 3 live Azure retrieval succeeded against '{args.index_name}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
