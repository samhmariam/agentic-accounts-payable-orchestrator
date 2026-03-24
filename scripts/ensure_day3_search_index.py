#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


def _bootstrap_src_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ensure the dedicated Day 3 Azure AI Search index exists.")
    parser.add_argument("--endpoint", required=True, help="Search service endpoint, for example https://<name>.search.windows.net")
    parser.add_argument("--index-name", default="day3-evidence", help="Target Day 3 index name")
    parser.add_argument("--retries", type=int, default=18, help="Number of RBAC propagation retries")
    parser.add_argument("--delay-seconds", type=int, default=10, help="Delay between retries")
    return parser.parse_args()


def ensure_index(endpoint: str, index_name: str, retries: int, delay_seconds: int) -> int:
    from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceNotFoundError
    from azure.search.documents.indexes import SearchIndexClient

    from aegisap.day3.retrieval.azure_ai_search_adapter import SEARCH_INDEX_FIELDS, _build_credential, build_day3_search_index

    client = SearchIndexClient(endpoint=endpoint.rstrip("/"), credential=_build_credential())
    required_fields = set(SEARCH_INDEX_FIELDS)

    for attempt in range(1, retries + 1):
        try:
            existing = client.get_index(index_name)
            existing_fields = {field.name for field in existing.fields}
            missing = sorted(required_fields - existing_fields)
            if missing:
                print(
                    f"Day 3 index '{index_name}' exists but is missing required fields: {', '.join(missing)}",
                    file=sys.stderr,
                )
                return 1
            print(f"Day 3 Search index already present: {index_name}")
            return 0
        except ResourceNotFoundError:
            try:
                client.create_index(build_day3_search_index(index_name))
                print(f"Created Day 3 Search index: {index_name}")
                return 0
            except (ClientAuthenticationError, HttpResponseError) as exc:
                message = str(exc)
                if attempt < retries and ("403" in message or "401" in message or "Forbidden" in message):
                    print(
                        f"Waiting for Search RBAC propagation ({attempt}/{retries}) for Day 3 index '{index_name}'...",
                        file=sys.stderr,
                    )
                    time.sleep(delay_seconds)
                    continue
                print(message, file=sys.stderr)
                return 1
        except (ClientAuthenticationError, HttpResponseError) as exc:
            message = str(exc)
            if attempt < retries and ("403" in message or "401" in message or "Forbidden" in message):
                print(
                    f"Waiting for Search RBAC propagation ({attempt}/{retries}) for Day 3 index '{index_name}'...",
                    file=sys.stderr,
                )
                time.sleep(delay_seconds)
                continue
            print(message, file=sys.stderr)
            return 1

    print(f"Day 3 Search index bootstrap timed out for '{index_name}'.", file=sys.stderr)
    return 1


def main() -> int:
    _bootstrap_src_path()
    args = parse_args()
    return ensure_index(args.endpoint, args.index_name, args.retries, args.delay_seconds)


if __name__ == "__main__":
    sys.exit(main())
