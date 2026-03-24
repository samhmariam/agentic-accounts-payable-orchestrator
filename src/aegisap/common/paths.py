from __future__ import annotations

from pathlib import Path


def repo_root(start: str | Path | None = None) -> Path:
    current = Path(start or __file__).resolve()
    candidates = [current] + list(current.parents)
    for candidate in candidates:
        if (candidate / "pyproject.toml").exists() and (candidate / "src" / "aegisap").exists():
            return candidate
    raise FileNotFoundError(f"Could not resolve repository root from {current}")
