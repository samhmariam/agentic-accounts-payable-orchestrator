from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from aegisap.common.paths import repo_root

from .models import utc_now_iso


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write an idempotent preview Azure mutation receipt for a lab scenario.")
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--action", choices=["break", "restore"], required=True)
    return parser.parse_args()


def resolve_runtime_root() -> Path:
    env_root = os.environ.get("AEGISAP_LAB_REPO_ROOT", "").strip()
    if env_root:
        return Path(env_root).resolve()
    cwd = Path.cwd().resolve()
    if (cwd / "pyproject.toml").exists():
        return cwd
    return repo_root(__file__)


def main() -> int:
    args = parse_args()
    root = resolve_runtime_root()
    receipt_dir = root / ".aegisap-lab" / "azure"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = receipt_dir / f"{args.scenario}_{args.action}.json"
    payload = {
        "scenario": args.scenario,
        "action": args.action,
        "executed_at": utc_now_iso(),
        "mode": "preview",
        "detail": "Preview-only Azure mutation receipt. Replace with real Azure sandbox mutation commands when the cohort environment is available.",
    }
    receipt_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
