from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from aegisap.common.paths import repo_root

from .models import utc_now_iso


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reprovision the Day 0 baseline for a training scenario.")
    parser.add_argument("--track", choices=["core", "full"], required=True)
    parser.add_argument("--scenario", required=True)
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
    receipt_dir = root / ".aegisap-lab" / "baseline"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = receipt_dir / f"{args.scenario}_{args.track}.json"
    payload = {
        "scenario": args.scenario,
        "track": args.track,
        "reprovisioned_at": utc_now_iso(),
        "mode": "preview",
        "detail": "Preview baseline reprovision completed. Replace this command with a live Day 0 reprovision command in Azure-enabled cohorts.",
    }
    receipt_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
