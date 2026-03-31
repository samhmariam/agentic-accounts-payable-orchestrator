import os

import pytest

from aegisap.day3.graph import run_day3_workflow
from aegisap.day3.retrieval.azure_ai_search_adapter import AzureAISearchLiveAdapter


required_env = ("AZURE_SEARCH_ENDPOINT", "AZURE_SEARCH_DAY3_INDEX")


def test_live_adapter_uses_semantic_query_options(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    class FakeSearchClient:
        def search(self, **kwargs):
            calls.append(kwargs)
            return [
                {
                    "id": "doc-1",
                    "doc_id": "doc-1",
                    "title": "Acme bank change",
                    "content": "Authoritative vendor master record.",
                    "source_name": "vendor-master",
                    "source_type": "erp_vendor_master",
                    "source_uri": "search:doc-1",
                    "authority_tier": 1,
                    "vendor_id": "VEND-001",
                    "vendor_name": "Acme Office Supplies",
                    "bank_account_last4": "4421",
                    "@search.score": 2.5,
                }
            ]

    monkeypatch.setattr(
        "aegisap.day3.retrieval.azure_ai_search_adapter.get_search_query_client",
        lambda **_: FakeSearchClient(),
    )

    adapter = AzureAISearchLiveAdapter(
        endpoint="https://example.search.windows.net",
        index_name="day3-evidence",
    )
    results = adapter.search(query="Acme Office Supplies bank change 4421", max_results=5)

    assert results
    assert calls == [
        {
            "search_text": "Acme Office Supplies bank change 4421",
            "query_type": "semantic",
            "semantic_query": "Acme Office Supplies bank change 4421",
            "semantic_configuration_name": "day3-semantic-config",
            "top": 5,
            "select": [
                "id",
                "doc_id",
                "title",
                "content",
                "source_name",
                "source_type",
                "source_uri",
                "authority_tier",
                "event_time",
                "ingest_time",
                "vendor_id",
                "vendor_name",
                "bank_account_last4",
                "chunk_id",
            ],
        }
    ]


@pytest.mark.skipif(
    not all(os.getenv(name, "").strip() for name in required_env),
    reason="Live Azure Search env is not configured",
)
def test_live_azure_search_smoke_path_prefers_authoritative_vendor_master():
    adapter = AzureAISearchLiveAdapter(
        endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
        index_name=os.environ["AZURE_SEARCH_DAY3_INDEX"],
    )
    live_results = adapter.search(query="Acme Office Supplies bank change 4421", max_results=5)

    assert live_results

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
    state = run_day3_workflow(invoice, retrieval_mode="azure_search_live")

    assert state.agent_findings["decision"].recommendation == "approve"
    assert "vendor-master-VEND-001" in state.agent_findings["decision"].evidence_ids
    assert "doc-onboarding-old-bank" in state.agent_findings["vendor_risk"].evidence_ids
    assert any(item.backend == "azure_ai_search_live" for item in state.bucket("vendor", "policy"))
