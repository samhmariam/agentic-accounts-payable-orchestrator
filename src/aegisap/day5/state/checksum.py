from __future__ import annotations

import hashlib
import json
from typing import Any

from aegisap.day5.state.durable_models import DurableWorkflowState



def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )



def compute_payload_checksum(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()



def compute_state_checksum(state: DurableWorkflowState) -> str:
    return compute_payload_checksum(state.canonical_payload())
