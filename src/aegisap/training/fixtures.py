from __future__ import annotations

from pathlib import Path

from aegisap.common.paths import repo_root


def golden_thread_path(*parts: str) -> Path:
    return repo_root(__file__) / "fixtures" / "golden_thread" / Path(*parts)


def day6_fixture_path(*parts: str) -> Path:
    return repo_root(__file__) / "fixtures" / "day06" / Path(*parts)
