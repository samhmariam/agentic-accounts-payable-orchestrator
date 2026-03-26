from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(slots=True)
class SemanticCacheRecord:
    response_text: str
    created_at: datetime
    expires_at: datetime
    citation_hash: str


class InMemorySemanticCache:
    def __init__(self) -> None:
        self._store: dict[str, SemanticCacheRecord] = {}

    def get(self, key: str) -> SemanticCacheRecord | None:
        record = self._store.get(key)
        if record is None:
            return None
        if record.expires_at <= datetime.now(timezone.utc):
            self._store.pop(key, None)
            return None
        return record

    def put(self, *, key: str, response_text: str, ttl_seconds: int, citation_hash: str) -> SemanticCacheRecord:
        now = datetime.now(timezone.utc)
        record = SemanticCacheRecord(
            response_text=response_text,
            created_at=now,
            expires_at=now + timedelta(seconds=ttl_seconds),
            citation_hash=citation_hash,
        )
        self._store[key] = record
        return record
