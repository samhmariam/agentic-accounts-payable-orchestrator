"""
Rubric consistency tests.

Validates the scoring model: pass bars, zero-tolerance enforcement logic, and
graduation tier definitions. Does not import from src/aegisap.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "docs" / "curriculum" / "CURRICULUM_MANIFEST.yaml"


@pytest.fixture(scope="module")
def manifest() -> dict:
    with MANIFEST_PATH.open() as fh:
        return yaml.safe_load(fh)


# ---------------------------------------------------------------------------
# Pass bars
# ---------------------------------------------------------------------------


def test_daily_pass_bar_is_80(manifest: dict) -> None:
    assert manifest["daily_pass_bar"] == 80


def test_elite_pass_bar_is_90(manifest: dict) -> None:
    assert manifest["elite_pass_bar"] == 90


def test_daily_pass_bar_below_elite_bar(manifest: dict) -> None:
    assert manifest["daily_pass_bar"] < manifest["elite_pass_bar"]


# ---------------------------------------------------------------------------
# Zero-tolerance enforcement model
# ---------------------------------------------------------------------------


def test_zero_tolerance_hard_fail_overrides_total() -> None:
    """
    Simulate a day score that would otherwise pass but has a zero-tolerance
    failure. The result must be 0 regardless of numeric total.
    """
    numeric_total = 85  # would pass at the daily bar of 80

    def apply_zero_tolerance(score: int, zero_tolerance_failures: list[str]) -> int:
        if zero_tolerance_failures:
            return 0
        return score

    result = apply_zero_tolerance(
        numeric_total, ["mandatory_escalation_missed"])
    assert result == 0, (
        "Zero-tolerance failure must set day score to 0 regardless of numeric total"
    )


def test_no_zero_tolerance_failures_preserves_score() -> None:
    def apply_zero_tolerance(score: int, zero_tolerance_failures: list[str]) -> int:
        if zero_tolerance_failures:
            return 0
        return score

    result = apply_zero_tolerance(85, [])
    assert result == 85


# ---------------------------------------------------------------------------
# Graduation tiers
# ---------------------------------------------------------------------------


def test_graduation_tiers_defined(manifest: dict) -> None:
    tiers = manifest.get("graduation_tiers", {})
    assert "graduate" in tiers
    assert "strong_fde" in tiers
    assert "top_talent" in tiers


def test_graduation_tier_score_thresholds_non_overlapping(manifest: dict) -> None:
    tiers = manifest["graduation_tiers"]
    graduate_bar = tiers["graduate"]["average_score"]
    strong_bar = tiers["strong_fde"]["average_score"]
    top_bar = tiers["top_talent"]["average_score"]

    assert graduate_bar < strong_bar, (
        f"Graduate bar ({graduate_bar}) must be below Strong FDE bar ({strong_bar})"
    )
    assert strong_bar < top_bar, (
        f"Strong FDE bar ({strong_bar}) must be below Top Talent bar ({top_bar})"
    )


def test_graduate_tier_requires_all_days_pass(manifest: dict) -> None:
    graduate = manifest["graduation_tiers"]["graduate"]
    assert graduate.get("all_days_pass") is True


def test_graduate_tier_requires_zero_tolerance_pass(manifest: dict) -> None:
    graduate = manifest["graduation_tiers"]["graduate"]
    assert graduate.get("all_zero_tolerance_pass") is True


def test_top_talent_requires_transfer_capstone(manifest: dict) -> None:
    top = manifest["graduation_tiers"]["top_talent"]
    assert top.get("transfer_capstone_pass") is True


# ---------------------------------------------------------------------------
# Rubric dimensions are consistent across all 14 days
# ---------------------------------------------------------------------------


def test_all_rubric_weights_are_positive(manifest: dict) -> None:
    for day in manifest["days"]:
        for dim, weight in day["rubric_weights"].items():
            assert weight > 0, (
                f"Day {day['id']} dimension '{dim}' has non-positive weight {weight}"
            )


def test_no_single_dimension_exceeds_35(manifest: dict) -> None:
    """No single rubric dimension should dominate beyond the programme max of 35."""
    for day in manifest["days"]:
        for dim, weight in day["rubric_weights"].items():
            assert weight <= 35, (
                f"Day {day['id']} dimension '{dim}' weight {weight} exceeds max 35"
            )
