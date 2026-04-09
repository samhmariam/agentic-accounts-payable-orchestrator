from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from aegisap.common.paths import repo_root

from .models import utc_now_iso


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mutate or restore Day 00 bootstrap state for incident training.")
    parser.add_argument("--action", choices=["break", "restore"], required=True)
    parser.add_argument("--track", choices=["core", "full"], required=True)
    return parser.parse_args()


def resolve_runtime_root() -> Path:
    env_root = os.environ.get("AEGISAP_LAB_REPO_ROOT", "").strip()
    if env_root:
        return Path(env_root).resolve()
    cwd = Path.cwd().resolve()
    if (cwd / "pyproject.toml").exists():
        return cwd
    return repo_root(__file__)


def _state_path(root: Path, track: str) -> Path:
    return root / ".day0" / f"{track}.json"


def _backup_path(root: Path, track: str) -> Path:
    return root / ".aegisap-lab" / "bootstrap_incident" / f"{track}_backup.json"


def _receipt_path(root: Path, track: str, action: str) -> Path:
    return root / ".aegisap-lab" / "bootstrap_incident" / f"{track}_{action}.json"


def _broken_state(track: str) -> dict[str, Any]:
    required_env = {
        "core": {
            "AZURE_OPENAI_CHAT_DEPLOYMENT": "day00-broken-deployment",
            "AZURE_SEARCH_INDEX": "",
        },
        "full": {
            "AZURE_OPENAI_CHAT_DEPLOYMENT": "day00-broken-deployment",
            "AZURE_POSTGRES_HOST": "",
        },
    }
    payload = {
        "track": track,
        "generatedAtUtc": utc_now_iso(),
        "environment": required_env[track],
        "resources": {
            "note": "Day 00 incident intentionally breaks the bootstrap contract.",
        },
    }
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def break_state(root: Path, track: str) -> dict[str, Any]:
    state_path = _state_path(root, track)
    backup_path = _backup_path(root, track)
    original_exists = state_path.exists()
    backup_payload: dict[str, Any] = {
        "track": track,
        "captured_at": utc_now_iso(),
        "original_exists": original_exists,
        "original_payload": None,
    }
    if original_exists:
        backup_payload["original_payload"] = json.loads(state_path.read_text(encoding="utf-8"))
    _write_json(backup_path, backup_payload)
    _write_json(state_path, _broken_state(track))
    payload = {
        "track": track,
        "action": "break",
        "executed_at": utc_now_iso(),
        "state_path": str(state_path),
        "backup_path": str(backup_path),
        "detail": "Day 00 bootstrap state corrupted so setup-env plus verify_env fails until the contract is repaired.",
    }
    _write_json(_receipt_path(root, track, "break"), payload)
    return payload


def restore_state(root: Path, track: str) -> dict[str, Any]:
    state_path = _state_path(root, track)
    backup_path = _backup_path(root, track)
    if backup_path.exists():
        backup_payload = json.loads(backup_path.read_text(encoding="utf-8"))
        if backup_payload.get("original_exists"):
            _write_json(state_path, backup_payload["original_payload"])
        elif state_path.exists():
            state_path.unlink()
        backup_path.unlink()
    payload = {
        "track": track,
        "action": "restore",
        "executed_at": utc_now_iso(),
        "state_path": str(state_path),
        "backup_path": str(backup_path),
        "detail": "Day 00 bootstrap state restored to the pre-incident snapshot.",
    }
    _write_json(_receipt_path(root, track, "restore"), payload)
    return payload


def main() -> int:
    args = parse_args()
    root = resolve_runtime_root()
    payload = break_state(root, args.track) if args.action == "break" else restore_state(root, args.track)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
