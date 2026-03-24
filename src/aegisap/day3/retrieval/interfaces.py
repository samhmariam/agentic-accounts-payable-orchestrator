from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal

from aegisap.common.paths import repo_root

RetrievalMode = Literal["fixture", "azure_search_live", "pgvector_fixture"]


def parse_iso_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value.strip())


@dataclass(slots=True)
class ParsedMarkdownDocument:
    metadata: dict[str, str]
    body: str
    path: Path


@dataclass(slots=True)
class RetrievalConfig:
    mode: RetrievalMode = "fixture"
    search_endpoint: str | None = None
    search_index_name: str | None = None
    docs_path: Path | None = None
    max_results: int = 5


def parse_front_matter_text(text: str, *, path: Path) -> ParsedMarkdownDocument:
    if not text.startswith("---\n"):
        return ParsedMarkdownDocument(metadata={}, body=text, path=path)

    _, rest = text.split("---\n", 1)
    front_matter, body = rest.split("\n---\n", 1)
    metadata: dict[str, str] = {}
    for line in front_matter.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return ParsedMarkdownDocument(metadata=metadata, body=body.strip(), path=path)


def parse_front_matter_markdown(path: Path) -> ParsedMarkdownDocument:
    """
    Minimal front matter parser.

    Expected shape:
    ---
    key: value
    key2: value2
    ---
    body...
    """
    return parse_front_matter_text(path.read_text(encoding="utf-8"), path=path)


def day3_data_path(*parts: str) -> Path:
    return repo_root(__file__) / "data" / "day3" / Path(*parts)


def day3_search_index_name(default: str = "day3-evidence") -> str:
    value = os.getenv("AZURE_SEARCH_DAY3_INDEX", default).strip()
    if not value:
        raise RuntimeError("AZURE_SEARCH_DAY3_INDEX is set but empty")
    return value


def build_retrieval_config(
    mode: RetrievalMode = "fixture",
    *,
    search_endpoint: str | None = None,
    search_index_name: str | None = None,
    docs_path: str | Path | None = None,
    max_results: int = 5,
) -> RetrievalConfig:
    resolved_docs_path = Path(docs_path) if docs_path is not None else None
    if mode == "azure_search_live":
        endpoint = (search_endpoint or os.getenv("AZURE_SEARCH_ENDPOINT", "")).strip()
        index_name = (search_index_name or os.getenv("AZURE_SEARCH_DAY3_INDEX", "")).strip()
        if not endpoint:
            raise RuntimeError("missing required environment variable: AZURE_SEARCH_ENDPOINT")
        if not index_name:
            raise RuntimeError("missing required environment variable: AZURE_SEARCH_DAY3_INDEX")
        return RetrievalConfig(
            mode=mode,
            search_endpoint=endpoint,
            search_index_name=index_name,
            docs_path=resolved_docs_path,
            max_results=max_results,
        )

    return RetrievalConfig(
        mode=mode,
        docs_path=resolved_docs_path,
        search_index_name=search_index_name,
        search_endpoint=search_endpoint,
        max_results=max_results,
    )
