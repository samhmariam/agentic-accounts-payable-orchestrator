from __future__ import annotations

from dataclasses import dataclass

from aegisap.common.hashing import stable_sha256
from aegisap.security.config import load_security_config


@dataclass(slots=True)
class CacheDecision:
    allowed: bool
    bypass_reason: str | None = None
    ttl_seconds: int = 0


def evaluate_cache_policy(
    *,
    task_class: str,
    risk_flags: list[str] | None = None,
    retrieval_confidence: float | None = None,
    evidence_conflict_count: int = 0,
    evidence_fresh: bool = True,
) -> CacheDecision:
    config = load_security_config()
    risk_flags = risk_flags or []
    if not config.cache_enabled:
        return CacheDecision(allowed=False, bypass_reason="cache_disabled", ttl_seconds=0)
    if task_class not in {"retrieve_summarise", "final_render", "extract"}:
        return CacheDecision(allowed=False, bypass_reason="task_class_not_cacheable", ttl_seconds=0)
    if evidence_conflict_count > 0:
        return CacheDecision(allowed=False, bypass_reason="evidence_conflict_present", ttl_seconds=0)
    if not evidence_fresh:
        return CacheDecision(allowed=False, bypass_reason="evidence_stale", ttl_seconds=0)
    if retrieval_confidence is not None and retrieval_confidence < 0.85:
        return CacheDecision(allowed=False, bypass_reason="retrieval_confidence_below_threshold", ttl_seconds=0)
    blocked = {
        "high_value",
        "missing_po",
        "bank_details_changed",
        "contradictory_evidence",
        "prior_refusal",
        "new_vendor",
    }
    if blocked.intersection(risk_flags):
        return CacheDecision(allowed=False, bypass_reason="high_risk_case", ttl_seconds=0)
    return CacheDecision(allowed=True, ttl_seconds=config.cache_ttl_seconds)


def build_cache_key(
    *,
    tenant: str,
    task_class: str,
    policy_version: str | None,
    source_snapshot_hash: str,
    prompt_text: str,
) -> str:
    version = policy_version or "unknown"
    prompt_hash = stable_sha256(prompt_text)
    return stable_sha256(f"{tenant}:{task_class}:{version}:{source_snapshot_hash}:{prompt_hash}")
