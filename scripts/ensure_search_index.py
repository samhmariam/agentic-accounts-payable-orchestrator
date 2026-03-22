#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import time


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ensure the starter Azure AI Search index exists.")
    parser.add_argument("--endpoint", required=True, help="Search service endpoint, for example https://<name>.search.windows.net")
    parser.add_argument("--index-name", required=True, help="Target index name")
    parser.add_argument("--retries", type=int, default=18, help="Number of RBAC propagation retries")
    parser.add_argument("--delay-seconds", type=int, default=10, help="Delay between retries")
    return parser.parse_args()


def build_index(index_name: str):
    from azure.search.documents.indexes.models import SearchIndex, SearchableField, SimpleField
    from azure.search.documents.indexes.models import SearchFieldDataType

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True, sortable=True),
        SearchableField(name="title", type=SearchFieldDataType.String, sortable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="source_uri", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SimpleField(name="source_type", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="chunk_id", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
    ]
    return SearchIndex(name=index_name, fields=fields)


def build_credential():
    from azure.identity import DefaultAzureCredential

    try:
        return DefaultAzureCredential(exclude_interactive_browser_credential=True)
    except ValueError as exc:
        print(
            f"Falling back to Azure CLI credential flow for local bootstrap: {exc}",
            file=sys.stderr,
        )
        return DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_interactive_browser_credential=True,
        )


def ensure_index(endpoint: str, index_name: str, retries: int, delay_seconds: int) -> int:
    try:
        from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceNotFoundError
        from azure.search.documents.indexes import SearchIndexClient
    except ImportError as exc:
        print(
            f"Missing dependency while bootstrapping Azure AI Search: {exc}. "
            "Install requirements.txt or use the dev container first.",
            file=sys.stderr,
        )
        return 2

    credential = build_credential()
    client = SearchIndexClient(endpoint=endpoint.rstrip("/"), credential=credential)

    for attempt in range(1, retries + 1):
        try:
            client.get_index(index_name)
            print(f"Search index already present: {index_name}")
            return 0
        except ResourceNotFoundError:
            try:
                client.create_index(build_index(index_name))
                print(f"Created Search index: {index_name}")
                return 0
            except (ClientAuthenticationError, HttpResponseError) as exc:
                message = str(exc)
                if attempt < retries and ("403" in message or "401" in message or "Forbidden" in message):
                    print(
                        f"Waiting for Search RBAC propagation ({attempt}/{retries}) for index '{index_name}'...",
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
                    f"Waiting for Search RBAC propagation ({attempt}/{retries}) for index '{index_name}'...",
                    file=sys.stderr,
                )
                time.sleep(delay_seconds)
                continue
            print(message, file=sys.stderr)
            return 1

    print(f"Search index bootstrap timed out for '{index_name}'.", file=sys.stderr)
    return 1


def main() -> int:
    args = parse_args()
    return ensure_index(args.endpoint, args.index_name, args.retries, args.delay_seconds)


if __name__ == "__main__":
    sys.exit(main())
