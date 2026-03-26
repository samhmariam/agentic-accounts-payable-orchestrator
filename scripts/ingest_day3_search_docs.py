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
    parser = argparse.ArgumentParser(description="Index Day 3 unstructured evidence into Azure AI Search.")
    parser.add_argument("--endpoint", default=os.getenv("AZURE_SEARCH_ENDPOINT", ""), help="Search endpoint")
    parser.add_argument("--index-name", default=os.getenv("AZURE_SEARCH_DAY3_INDEX", "day3-evidence"), help="Target Day 3 index")
    parser.add_argument("--source", choices=["local", "blob"], default="local", help="Document source")
    parser.add_argument("--docs-path", default="", help="Local docs path override")
    parser.add_argument("--account-url", default=os.getenv("AZURE_STORAGE_ACCOUNT_URL", ""), help="Blob account URL for blob source")
    parser.add_argument("--container-name", default=os.getenv("AZURE_STORAGE_CONTAINER", ""), help="Blob container name for blob source")
    parser.add_argument("--blob-prefix", default="day3/unstructured/", help="Blob prefix for markdown documents")
    return parser.parse_args()


def main() -> int:
    _bootstrap_src_path()
    args = parse_args()

    if not args.endpoint.strip():
        print("Missing required endpoint. Set AZURE_SEARCH_ENDPOINT or pass --endpoint.", file=sys.stderr)
        return 2
    if not args.index_name.strip():
        print("Missing required index name. Set AZURE_SEARCH_DAY3_INDEX or pass --index-name.", file=sys.stderr)
        return 2

    from aegisap.day3.retrieval.azure_ai_search_adapter import (
        blob_markdown_documents,
        day3_fixture_documents,
    )
    from aegisap.security.credentials import get_search_query_client

    if args.source == "blob":
        if not args.account_url.strip() or not args.container_name.strip():
            print(
                "Blob ingestion requires --account-url and --container-name or their Azure env vars.",
                file=sys.stderr,
            )
            return 2
        documents = blob_markdown_documents(
            account_url=args.account_url,
            container_name=args.container_name,
            prefix=args.blob_prefix,
        )
    else:
        docs_path = Path(args.docs_path) if args.docs_path.strip() else None
        documents = day3_fixture_documents(docs_path=docs_path)

    if not documents:
        print("No Day 3 documents found to ingest.", file=sys.stderr)
        return 1

    client = get_search_query_client(
        endpoint=args.endpoint.rstrip("/"),
        index_name=args.index_name,
    )
    results = client.upload_documents(documents=documents)
    failures = [result.key for result in results if not result.succeeded]
    if failures:
        print(f"Failed to index {len(failures)} documents: {', '.join(failures)}", file=sys.stderr)
        return 1

    print(f"Indexed {len(documents)} Day 3 documents into '{args.index_name}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
