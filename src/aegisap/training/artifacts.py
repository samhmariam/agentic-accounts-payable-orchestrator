from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aegisap.common.paths import repo_root


def build_root(*parts: str) -> Path:
    path = repo_root(__file__) / "build" / Path(*parts)
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json_artifact(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return path


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))
