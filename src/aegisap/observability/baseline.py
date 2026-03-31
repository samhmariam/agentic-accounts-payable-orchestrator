"""
Regression baseline capture and comparison for Day 8 observability.

baseline.json stores score snapshots produced by the eval suite.
compare_to_baseline() surfaces any regressions against score_thresholds.yaml.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RegressionDelta:
    metric: str
    baseline_value: float
    current_value: float
    threshold: float
    direction: str  # "min" or "max"

    @property
    def is_regression(self) -> bool:
        if self.direction == "min":
            return self.current_value < self.threshold
        return self.current_value > self.threshold


def _baseline_path() -> Path:
    return Path(__file__).resolve().parents[3] / "build" / "day8" / "regression_baseline.json"


def _thresholds_path() -> Path:
    return Path(__file__).resolve().parents[3] / "evals" / "score_thresholds.yaml"


def capture_baseline(results: dict[str, float]) -> None:
    """Write an eval results dict to the regression baseline file."""
    baseline_path = _baseline_path()
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.write_text(json.dumps(results, indent=2))


def load_baseline() -> dict[str, float] | None:
    p = _baseline_path()
    if not p.exists():
        return None
    return json.loads(p.read_text())


def _load_thresholds() -> dict[str, Any]:
    p = _thresholds_path()
    if not p.exists():
        return {}
    try:
        import yaml  # type: ignore
        return yaml.safe_load(p.read_text()) or {}
    except Exception:  # noqa: BLE001
        return {}


def compare_to_baseline(current: dict[str, float]) -> list[RegressionDelta]:
    """
    Compare current eval scores against score_thresholds.yaml.

    Returns a list of RegressionDelta items for every metric that breaches
    its threshold.  An empty list means no regressions.
    """
    thresholds = _load_thresholds()
    deltas: list[RegressionDelta] = []
    baseline = load_baseline() or {}

    for key, value in current.items():
        if key.endswith("_min"):
            metric = key[: -len("_min")]
            threshold = float(thresholds.get(key, float("-inf")))
            current_val = float(current.get(metric, value))
            baseline_val = float(baseline.get(metric, current_val))
            delta = RegressionDelta(
                metric=metric,
                baseline_value=baseline_val,
                current_value=current_val,
                threshold=threshold,
                direction="min",
            )
            if delta.is_regression:
                deltas.append(delta)
        elif key.endswith("_max"):
            metric = key[: -len("_max")]
            threshold = float(thresholds.get(key, float("inf")))
            current_val = float(current.get(metric, value))
            baseline_val = float(baseline.get(metric, current_val))
            delta = RegressionDelta(
                metric=metric,
                baseline_value=baseline_val,
                current_value=current_val,
                threshold=threshold,
                direction="max",
            )
            if delta.is_regression:
                deltas.append(delta)

    return deltas
