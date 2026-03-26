from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class TraceContext:
    request_id: str
    trace_id: str
    thread_id: str | None = None
    checkpoint_id: str | None = None


def make_trace_context(
    *,
    request_id: str,
    thread_id: str | None = None,
    checkpoint_id: str | None = None,
) -> TraceContext:
    return TraceContext(
        request_id=request_id,
        trace_id=str(uuid.uuid4()),
        thread_id=thread_id,
        checkpoint_id=checkpoint_id,
    )

