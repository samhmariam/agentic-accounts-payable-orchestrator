from __future__ import annotations

from pathlib import Path


def compiled_prompt_dir() -> Path:
    return Path(__file__).resolve().parent
