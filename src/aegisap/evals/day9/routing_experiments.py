from __future__ import annotations

from typing import Any


def score_experiment_slices(examples: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    slices: dict[str, list[dict[str, Any]]] = {}
    for example in examples:
        for slice_name in example.get("slices", []):
            slices.setdefault(slice_name, []).append(example)

    results: dict[str, dict[str, float]] = {}
    for slice_name, items in slices.items():
        passed = sum(1 for item in items if item.get("passed", False))
        latency = [float(item.get("latency_ms", 0.0) or 0.0) for item in items]
        cost = [float(item.get("workflow_cost", 0.0) or 0.0) for item in items]
        results[slice_name] = {
            "pass_rate": passed / len(items) if items else 0.0,
            "median_latency_ms": sorted(latency)[len(latency) // 2] if latency else 0.0,
            "median_workflow_cost": sorted(cost)[len(cost) // 2] if cost else 0.0,
        }
    return results
