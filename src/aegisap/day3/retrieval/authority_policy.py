from __future__ import annotations

from pathlib import Path
from typing import Any

DEFAULT_POLICY: dict[str, Any] = {
    "authority_weights": {1: 1.6, 2: 1.25, 3: 0.75, 4: 0.4},
    "recency_half_life_days": {
        "mutable_fact": 90,
        "policy": 365,
        "reference": 730,
    },
    "exact_match_bonus": 0.15,
    "staleness_labels": {"bank_account": "bank_account_last4"},
    "authority_rules": {
        "bank_account_last4": {
            "preferred_source_types": ["erp_vendor_master", "approved_bank_change", "policy_doc"]
        }
    },
}


def load_authority_policy(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return DEFAULT_POLICY

    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text) or {}
        return _coerce_policy(data)
    except Exception:
        return DEFAULT_POLICY


def _coerce_policy(data: dict[str, Any]) -> dict[str, Any]:
    policy = DEFAULT_POLICY.copy()
    for key in ("authority_weights", "recency_half_life_days", "exact_match_bonus", "staleness_labels", "authority_rules"):
        if key in data:
            policy[key] = data[key]
    if "authority_weights" in policy:
        policy["authority_weights"] = {int(k): float(v) for k, v in policy["authority_weights"].items()}
    return policy
