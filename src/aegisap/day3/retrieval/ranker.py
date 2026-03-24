from __future__ import annotations

from datetime import date
from math import pow
from typing import Any

from ..state.evidence_models import EvidenceItem


def _recency_weight(item: EvidenceItem, *, today: date, half_life_days: int) -> float:
    if not item.event_time:
        return 0.85
    age_days = max((today - item.event_time).days, 0)
    return max(0.2, pow(0.5, age_days / max(half_life_days, 1)))


def _exact_match_bonus(item: EvidenceItem, query_terms: dict[str, Any], bonus: float) -> float:
    if not query_terms:
        return 0.0
    for key, value in query_terms.items():
        if value is None:
            continue
        item_value = item.metadata.get(key)
        if item_value is not None and str(item_value).lower() == str(value).lower():
            return bonus
    return 0.0


def apply_authority_ranking(
    evidence_items: list[EvidenceItem],
    *,
    policy: dict[str, Any],
    query_terms: dict[str, Any] | None = None,
    today: date | None = None,
    recency_mode: str = "mutable_fact",
) -> list[EvidenceItem]:
    today = today or date.today()
    weights = policy["authority_weights"]
    half_life = int(policy["recency_half_life_days"].get(recency_mode, 365))
    bonus = float(policy.get("exact_match_bonus", 0.0))
    query_terms = query_terms or {}

    ranked: list[EvidenceItem] = []
    for item in evidence_items:
        authority_weight = float(weights.get(item.authority_tier, 0.4))
        recency_weight = _recency_weight(item, today=today, half_life_days=half_life)
        exact_bonus = _exact_match_bonus(item, query_terms, bonus)
        item.authority_adjusted_score = round(
            (item.retrieval_score * authority_weight * recency_weight) + exact_bonus, 6
        )
        ranked.append(item)

    ranked.sort(
        key=lambda item: (
            item.authority_adjusted_score,
            item.authority_tier * -1,
            item.event_time.isoformat() if item.event_time else "",
        ),
        reverse=True,
    )
    return ranked
