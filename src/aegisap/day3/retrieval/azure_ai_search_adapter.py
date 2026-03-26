from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from aegisap.security.credentials import get_blob_service_client, get_search_query_client, get_token_credential

from ..state.evidence_models import EvidenceItem
from .interfaces import (
    ParsedMarkdownDocument,
    RetrievalConfig,
    day3_data_path,
    day3_search_index_name,
    parse_front_matter_markdown,
    parse_front_matter_text,
    parse_iso_date,
)

SEARCH_INDEX_FIELDS = [
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
]

def _naive_keyword_score(query: str, text: str) -> float:
    query_tokens = {token.lower() for token in query.split() if token.strip()}
    if not query_tokens:
        return 0.0
    text_lower = text.lower()
    hits = sum(1 for token in query_tokens if token in text_lower)
    return round(min(1.0, 0.4 + (hits / max(len(query_tokens), 1))), 4)


def evidence_item_from_markdown(
    parsed: ParsedMarkdownDocument,
    *,
    retrieval_score: float,
    backend: str,
) -> EvidenceItem:
    metadata = dict(parsed.metadata)
    evidence_id = metadata.get("doc_id", parsed.path.stem)
    return EvidenceItem(
        evidence_id=evidence_id,
        source_name=metadata.get("source_name", parsed.path.stem),
        source_type=metadata.get("source_type", "unstructured_doc"),
        backend=backend,
        authority_tier=int(metadata.get("authority_tier", 4)),
        event_time=parse_iso_date(metadata.get("event_time")),
        ingest_time=parse_iso_date(metadata.get("ingest_time")),
        retrieval_score=retrieval_score,
        citation=metadata.get("title", parsed.path.stem),
        raw_ref=f"unstructured:{parsed.path.name}",
        content=parsed.body,
        metadata=metadata,
    )


def search_document_from_markdown(
    parsed: ParsedMarkdownDocument,
    *,
    source_uri: str | None = None,
    chunk_id: int = 0,
) -> dict[str, Any]:
    metadata = dict(parsed.metadata)
    doc_id = metadata.get("doc_id", parsed.path.stem)
    document = {
        "id": doc_id,
        "doc_id": doc_id,
        "title": metadata.get("title", parsed.path.stem),
        "content": parsed.body,
        "source_name": metadata.get("source_name", parsed.path.stem),
        "source_type": metadata.get("source_type", "unstructured_doc"),
        "source_uri": source_uri or f"unstructured:{parsed.path.name}",
        "authority_tier": int(metadata.get("authority_tier", 4)),
        "event_time": metadata.get("event_time") or None,
        "ingest_time": metadata.get("ingest_time") or None,
        "vendor_id": metadata.get("vendor_id") or None,
        "vendor_name": metadata.get("vendor_name") or None,
        "bank_account_last4": metadata.get("bank_account_last4") or None,
        "chunk_id": chunk_id,
    }
    return document


def evidence_item_from_search_result(document: Mapping[str, Any], *, backend: str) -> EvidenceItem:
    metadata = {
        key: document.get(key)
        for key in ("doc_id", "vendor_id", "vendor_name", "bank_account_last4", "title")
        if document.get(key) is not None
    }
    score = float(document.get("@search.score", 0.0) or 0.0)
    evidence_id = str(document.get("doc_id") or document.get("id") or "missing-doc-id")
    title = str(document.get("title") or evidence_id)
    source_uri = str(document.get("source_uri") or f"search:{evidence_id}")
    return EvidenceItem(
        evidence_id=evidence_id,
        source_name=str(document.get("source_name") or title),
        source_type=str(document.get("source_type") or "unstructured_doc"),
        backend=backend,
        authority_tier=int(document.get("authority_tier") or 4),
        event_time=parse_iso_date(document.get("event_time")),
        ingest_time=parse_iso_date(document.get("ingest_time")),
        retrieval_score=score,
        citation=title,
        raw_ref=source_uri,
        content=str(document.get("content") or ""),
        metadata=metadata,
    )


def build_day3_search_index(index_name: str):
    from azure.search.documents.indexes.models import SearchFieldDataType, SearchIndex, SearchableField, SimpleField

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True, sortable=True),
        SimpleField(name="doc_id", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SearchableField(name="title", type=SearchFieldDataType.String, sortable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="source_name", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="source_type", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="source_uri", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SimpleField(name="authority_tier", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
        SimpleField(name="event_time", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SimpleField(name="ingest_time", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SimpleField(name="vendor_id", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="vendor_name", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="bank_account_last4", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="chunk_id", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
    ]
    return SearchIndex(name=index_name, fields=fields)


def day3_fixture_documents(docs_path: str | Path | None = None) -> list[dict[str, Any]]:
    resolved_docs_path = Path(docs_path or day3_data_path("unstructured"))
    documents: list[dict[str, Any]] = []
    for path in sorted(resolved_docs_path.glob("*.md")):
        parsed = parse_front_matter_markdown(path)
        documents.append(search_document_from_markdown(parsed))
    return documents


class AzureAISearchFixtureAdapter:
    """
    Fixture-backed stand-in for Azure AI Search hybrid retrieval.
    """

    def __init__(self, docs_path: str | Path | None = None) -> None:
        self.docs_path = Path(docs_path or day3_data_path("unstructured"))

    def search(self, *, query: str, max_results: int = 5) -> list[EvidenceItem]:
        results: list[EvidenceItem] = []
        for path in sorted(self.docs_path.glob("*.md")):
            parsed = parse_front_matter_markdown(path)
            score = _naive_keyword_score(query, parsed.body)
            if score <= 0.4:
                continue
            results.append(
                evidence_item_from_markdown(
                    parsed,
                    retrieval_score=score,
                    backend="azure_ai_search_hybrid_fixture",
                )
            )
        results.sort(key=lambda item: item.retrieval_score, reverse=True)
        return results[:max_results]


class AzureAISearchLiveAdapter:
    """
    Live Azure AI Search retriever using RBAC via DefaultAzureCredential.
    """

    def __init__(
        self,
        *,
        endpoint: str | None = None,
        index_name: str | None = None,
        credential: Any | None = None,
    ) -> None:
        self.endpoint = (endpoint or "").rstrip("/")
        self.index_name = index_name or day3_search_index_name()
        if not self.endpoint:
            raise RuntimeError("missing required environment variable: AZURE_SEARCH_ENDPOINT")
        self.credential = credential or get_token_credential()

    def search(self, *, query: str, max_results: int = 5) -> list[EvidenceItem]:
        client = get_search_query_client(
            endpoint=self.endpoint,
            index_name=self.index_name,
        )
        results = client.search(
            search_text=query,
            top=max_results,
            select=SEARCH_INDEX_FIELDS,
        )
        items = [
            evidence_item_from_search_result(document, backend="azure_ai_search_live")
            for document in results
        ]
        items.sort(key=lambda item: item.retrieval_score, reverse=True)
        return items


def build_unstructured_retriever(config: RetrievalConfig):
    if config.mode == "azure_search_live":
        return AzureAISearchLiveAdapter(
            endpoint=config.search_endpoint,
            index_name=config.search_index_name,
        )
    if config.mode == "pgvector_fixture":
        from .pgvector_adapter import PGVectorFixtureAdapter

        return PGVectorFixtureAdapter(docs_path=config.docs_path)
    return AzureAISearchFixtureAdapter(docs_path=config.docs_path)


def blob_markdown_documents(
    *,
    account_url: str,
    container_name: str,
    credential: Any | None = None,
    prefix: str = "day3/unstructured/",
) -> list[dict[str, Any]]:
    service_client = get_blob_service_client(account_url=account_url)
    container = service_client.get_container_client(container_name)
    documents: list[dict[str, Any]] = []
    for blob in container.list_blobs(name_starts_with=prefix):
        if not blob.name.endswith(".md"):
            continue
        content = container.download_blob(blob.name).readall().decode("utf-8")
        parsed = parse_front_matter_text(content, path=Path(blob.name))
        source_uri = f"{account_url.rstrip('/')}/{container_name}/{blob.name}"
        documents.append(search_document_from_markdown(parsed, source_uri=source_uri))
    return documents
