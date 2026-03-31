"""
Export helpers for the Day 3 multi-agent retrieval layer.
Converts EvidenceItem collections to notebook-friendly table rows.
"""
from __future__ import annotations

from typing import Any


def evidence_to_table(items: list[Any]) -> list[dict[str, Any]]:
    """
    Convert a list of EvidenceItem dataclasses to plain dicts suitable
    for marimo table rendering.
    """
    rows = []
    for item in items:
        if hasattr(item, "as_dict"):
            d = item.as_dict()
        else:
            d = item if isinstance(item, dict) else vars(item)
        rows.append(
            {
                "evidence_id": d.get("evidence_id", ""),
                "source_name": d.get("source_name", ""),
                "source_type": d.get("source_type", ""),
                "backend": d.get("backend", ""),
                "authority_tier": d.get("authority_tier", 0),
                "retrieval_score": round(float(d.get("retrieval_score", 0.0)), 4),
                "authority_adjusted_score": round(float(d.get("authority_adjusted_score", 0.0)), 4),
                "event_time": str(d.get("event_time", "")),
                "citation": d.get("citation", ""),
                "content_preview": str(d.get("content", ""))[:120],
            }
        )
    return sorted(rows, key=lambda r: r["authority_adjusted_score"], reverse=True)
