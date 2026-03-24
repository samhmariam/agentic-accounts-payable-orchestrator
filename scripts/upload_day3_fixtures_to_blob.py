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
    parser = argparse.ArgumentParser(description="Upload Day 3 markdown fixtures to Azure Blob Storage.")
    parser.add_argument("--account-url", default=os.getenv("AZURE_STORAGE_ACCOUNT_URL", ""), help="Blob account URL")
    parser.add_argument("--container-name", default=os.getenv("AZURE_STORAGE_CONTAINER", ""), help="Blob container name")
    parser.add_argument("--docs-path", default="", help="Local docs path override")
    parser.add_argument("--blob-prefix", default="day3/unstructured/", help="Blob prefix for uploaded markdown files")
    return parser.parse_args()


def main() -> int:
    _bootstrap_src_path()
    args = parse_args()

    if not args.account_url.strip() or not args.container_name.strip():
        print(
            "Blob upload requires --account-url and --container-name or their Azure env vars.",
            file=sys.stderr,
        )
        return 2

    from azure.storage.blob import BlobServiceClient

    from aegisap.day3.retrieval.azure_ai_search_adapter import _build_credential
    from aegisap.day3.retrieval.interfaces import day3_data_path

    docs_path = Path(args.docs_path) if args.docs_path.strip() else day3_data_path("unstructured")
    paths = sorted(docs_path.glob("*.md"))
    if not paths:
        print(f"No markdown fixtures found under {docs_path}", file=sys.stderr)
        return 1

    service_client = BlobServiceClient(account_url=args.account_url, credential=_build_credential())
    container = service_client.get_container_client(args.container_name)

    for path in paths:
        blob_name = f"{args.blob_prefix.rstrip('/')}/{path.name}"
        container.upload_blob(name=blob_name, data=path.read_bytes(), overwrite=True)

    print(f"Uploaded {len(paths)} Day 3 fixture documents to {args.container_name}/{args.blob_prefix.rstrip('/')}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
