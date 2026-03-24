from pathlib import Path

import pytest

from aegisap.day3.retrieval import (
    AzureAISearchFixtureAdapter,
    PGVectorFixtureAdapter,
    build_retrieval_config,
    build_unstructured_retriever,
    evidence_item_from_search_result,
    search_document_from_markdown,
)
from aegisap.day3.retrieval.interfaces import parse_front_matter_markdown


def test_search_document_from_markdown_preserves_day3_metadata():
    parsed = parse_front_matter_markdown(Path("data/day3/unstructured/bank_change_approval_email.md"))

    document = search_document_from_markdown(parsed, source_uri="blob://documents/day3/bank_change_approval_email.md")

    assert document["id"] == "doc-bank-change-approved"
    assert document["source_type"] == "approved_bank_change"
    assert document["bank_account_last4"] == "4421"
    assert document["source_uri"] == "blob://documents/day3/bank_change_approval_email.md"


def test_evidence_item_from_search_result_maps_live_search_fields():
    document = {
        "id": "doc-onboarding-old-bank",
        "doc_id": "doc-onboarding-old-bank",
        "title": "Supplier onboarding email with original bank details",
        "content": "Original onboarding package listed account ending 1138.",
        "source_name": "supplier_onboarding_email",
        "source_type": "email",
        "source_uri": "https://example.blob.core.windows.net/documents/day3/unstructured/supplier_onboarding_old_email.md",
        "authority_tier": 3,
        "event_time": "2025-04-10",
        "ingest_time": "2025-04-10",
        "vendor_id": "VEND-001",
        "vendor_name": "Acme Office Supplies",
        "bank_account_last4": "1138",
        "chunk_id": 0,
        "@search.score": 2.75,
    }

    item = evidence_item_from_search_result(document, backend="azure_ai_search_live")

    assert item.evidence_id == "doc-onboarding-old-bank"
    assert item.backend == "azure_ai_search_live"
    assert item.retrieval_score == 2.75
    assert item.metadata["bank_account_last4"] == "1138"


def test_build_retrieval_config_defaults_to_fixture():
    config = build_retrieval_config()

    assert config.mode == "fixture"
    retriever = build_unstructured_retriever(config)
    assert isinstance(retriever, AzureAISearchFixtureAdapter)


def test_build_retrieval_config_selects_pgvector_fixture():
    config = build_retrieval_config("pgvector_fixture")

    assert config.mode == "pgvector_fixture"
    retriever = build_unstructured_retriever(config)
    assert isinstance(retriever, PGVectorFixtureAdapter)


def test_live_retrieval_config_requires_day3_search_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("AZURE_SEARCH_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_SEARCH_DAY3_INDEX", raising=False)

    with pytest.raises(RuntimeError, match="AZURE_SEARCH_ENDPOINT"):
        build_retrieval_config("azure_search_live")

    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://example.search.windows.net")
    with pytest.raises(RuntimeError, match="AZURE_SEARCH_DAY3_INDEX"):
        build_retrieval_config("azure_search_live")


def test_live_retrieval_config_accepts_explicit_args_without_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("AZURE_SEARCH_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_SEARCH_DAY3_INDEX", raising=False)

    config = build_retrieval_config(
        "azure_search_live",
        search_endpoint="https://example.search.windows.net",
        search_index_name="day3-evidence",
    )

    assert config.mode == "azure_search_live"
    assert config.search_endpoint == "https://example.search.windows.net"
    assert config.search_index_name == "day3-evidence"
