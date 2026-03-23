from __future__ import annotations

from aegisap.common.hashing import stable_sha256
from aegisap.day2.state import WorkflowState


def semantic_idempotency_key(state: WorkflowState, node_name: str, action: str) -> str:
    raw = f"{state.workflow_id}:{node_name}:{action}"
    return stable_sha256(raw)


def ensure_action_once(state: WorkflowState, node_name: str, action: str) -> bool:
    key = semantic_idempotency_key(state, node_name, action)
    if action in state.idempotency_keys and state.idempotency_keys[action] == key:
        return False
    state.idempotency_keys[action] = key
    return True
