from __future__ import annotations

from pathlib import Path

from ..state.evidence_models import EvidenceItem
from .interfaces import day3_data_path, parse_front_matter_markdown, parse_iso_date


def _token_overlap_score(query: str, text: str) -> float:
    q = {token.lower().strip(".,:;()") for token in query.split() if token.strip()}
    t = {token.lower().strip(".,:;()") for token in text.split() if token.strip()}
    if not q:
        return 0.0
    overlap = len(q & t) / max(len(q), 1)
    return round(0.35 + overlap, 4)


class PGVectorFixtureAdapter:
    """
    Cost-sensitive local retriever stand-in for pgvector-backed retrieval.
    """

    def __init__(self, docs_path: str | Path | None = None) -> None:
        self.docs_path = Path(docs_path or day3_data_path("unstructured"))

    def search(self, *, query: str, max_results: int = 5) -> list[EvidenceItem]:
        results: list[EvidenceItem] = []
        for path in sorted(self.docs_path.glob("*.md")):
            parsed = parse_front_matter_markdown(path)
            score = _token_overlap_score(query, parsed.body)
            if score <= 0.45:
                continue
            metadata = dict(parsed.metadata)
            results.append(
                EvidenceItem(
                    evidence_id=metadata["doc_id"],
                    source_name=metadata["source_name"],
                    source_type=metadata["source_type"],
                    backend="pgvector_fixture",
                    authority_tier=int(metadata["authority_tier"]),
                    event_time=parse_iso_date(metadata.get("event_time")),
                    ingest_time=parse_iso_date(metadata.get("ingest_time")),
                    retrieval_score=score,
                    citation=metadata.get("title", path.stem),
                    raw_ref=f"unstructured:{path.name}",
                    content=parsed.body,
                    metadata=metadata,
                )
            )
        results.sort(key=lambda item: item.retrieval_score, reverse=True)
        return results[:max_results]
