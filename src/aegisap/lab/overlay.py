from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .assets import (
    ASSET_PROVIDER_LOCAL,
    ASSET_PROVIDER_REMOTE,
    asset_provider_status,
    bundle_overlay_path,
    configured_asset_provider,
    hydrate_remote_bundle,
)
from .curriculum import normalize_day, resolve_repo_root


PHASE1_MAX_COHORTS = 2
PHASE1_MAX_AGE_DAYS = 60
OVERLAY_CACHE_ROOT = Path(".aegisap-lab") / "cache" / "instructor"
OVERLAY_FILE_NAME = "overlay.yaml"
HINT_STATE_ROOT = OVERLAY_CACHE_ROOT / "interventions"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def overlay_cache_dir(repo_root: str | Path | None = None) -> Path:
    return resolve_repo_root(repo_root) / OVERLAY_CACHE_ROOT


def overlay_cache_path(repo_root: str | Path | None = None) -> Path:
    return overlay_cache_dir(repo_root) / OVERLAY_FILE_NAME


def hint_state_path(day: str | int, repo_root: str | Path | None = None) -> Path:
    return resolve_repo_root(repo_root) / HINT_STATE_ROOT / f"day{normalize_day(day)}.json"


def load_instructor_overlay(
    repo_root: str | Path | None = None,
    *,
    required: bool = False,
) -> dict[str, Any]:
    if configured_asset_provider() == ASSET_PROVIDER_REMOTE:
        payload: dict[str, Any] = {
            "schema_version": 1,
            "phase1_limits": {
                "max_cohorts": PHASE1_MAX_COHORTS,
                "max_age_days": PHASE1_MAX_AGE_DAYS,
            },
            "days": {},
        }
        for day_id in asset_provider_status(repo_root).get("cached_days", []):
            overlay_path = bundle_overlay_path(day_id, repo_root)
            bundle_payload = yaml.safe_load(overlay_path.read_text(encoding="utf-8")) or {}
            if not isinstance(bundle_payload, dict):
                continue
            days = bundle_payload.get("days", {})
            if isinstance(days, dict):
                payload["days"].update(days)
        if required and not payload["days"]:
            raise ValueError(
                "No cached remote instructor bundles available. Hydrate one with "
                "`uv run aegisap-lab overlay hydrate --day <day>`."
            )
        return payload
    path = overlay_cache_path(repo_root)
    if not path.exists():
        if required:
            raise ValueError(
                "Instructor overlay missing. Import it with `uv run aegisap-lab overlay import --file <path>`."
            )
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Instructor overlay must be a mapping: {path}")
    return payload


def overlay_day(day: str | int, repo_root: str | Path | None = None) -> dict[str, Any]:
    if configured_asset_provider() == ASSET_PROVIDER_REMOTE:
        overlay_path = bundle_overlay_path(day, repo_root)
        payload = yaml.safe_load(overlay_path.read_text(encoding="utf-8")) or {}
        if not isinstance(payload, dict):
            raise ValueError(f"Remote instructor overlay must be a mapping: {overlay_path}")
        days = payload.get("days", {})
        if not isinstance(days, dict):
            return {}
        entry = days.get(normalize_day(day), {})
        return entry if isinstance(entry, dict) else {}
    overlay = load_instructor_overlay(repo_root)
    if not overlay:
        return {}
    days = overlay.get("days", {})
    if not isinstance(days, dict):
        return {}
    entry = days.get(normalize_day(day), {})
    return entry if isinstance(entry, dict) else {}


def import_instructor_overlay(
    *,
    source: str | Path,
    repo_root: str | Path | None = None,
    force: bool = False,
) -> dict[str, Any]:
    if configured_asset_provider() == ASSET_PROVIDER_REMOTE:
        raise ValueError(
            f"`overlay import` is only valid for `{ASSET_PROVIDER_LOCAL}` mode. "
            f"Use `uv run aegisap-lab overlay hydrate --day <day>` in `{ASSET_PROVIDER_REMOTE}` mode."
        )
    source_path = Path(source).expanduser().resolve()
    if not source_path.exists():
        raise ValueError(f"Overlay source not found: {source_path}")
    destination = overlay_cache_path(repo_root)
    if destination.exists() and not force:
        raise ValueError(
            f"Overlay already exists at {destination}. Re-run with `--force` to replace it."
        )
    payload = yaml.safe_load(source_path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError("Overlay payload must be a mapping.")
    days = payload.get("days")
    if not isinstance(days, dict) or not days:
        raise ValueError("Overlay payload must declare at least one day entry under `days`.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, destination)
    imported_payload = yaml.safe_load(destination.read_text(encoding="utf-8")) or {}
    return {
        "overlay_path": str(destination),
        "day_count": len(imported_payload.get("days", {})),
        "provider": ASSET_PROVIDER_LOCAL,
        "phase1_limits": imported_payload.get(
            "phase1_limits",
            {
                "max_cohorts": PHASE1_MAX_COHORTS,
                "max_age_days": PHASE1_MAX_AGE_DAYS,
            },
        ),
    }


def overlay_status(repo_root: str | Path | None = None) -> dict[str, Any]:
    provider_status = asset_provider_status(repo_root)
    if provider_status["provider"] == ASSET_PROVIDER_REMOTE:
        return {
            "status": "ready" if provider_status.get("cached_days") else "missing",
            "provider": ASSET_PROVIDER_REMOTE,
            "cache_root": provider_status["cache_root"],
            "base_url": provider_status.get("base_url", ""),
            "token_configured": provider_status.get("token_configured", False),
            "cached_days": provider_status.get("cached_days", []),
        }
    path = overlay_cache_path(repo_root)
    if not path.exists():
        return {"status": "missing", "provider": ASSET_PROVIDER_LOCAL, "overlay_path": str(path)}
    payload = load_instructor_overlay(repo_root)
    return {
        "status": "ready",
        "provider": ASSET_PROVIDER_LOCAL,
        "overlay_path": str(path),
        "day_count": len(payload.get("days", {})),
        "phase1_limits": payload.get(
            "phase1_limits",
            {
                "max_cohorts": PHASE1_MAX_COHORTS,
                "max_age_days": PHASE1_MAX_AGE_DAYS,
            },
        ),
    }


def hydrate_instructor_bundle(
    *,
    day: str | int,
    repo_root: str | Path | None = None,
    force: bool = False,
) -> dict[str, Any]:
    return hydrate_remote_bundle(day=day, repo_root=repo_root, force=force)


def record_hint_usage(
    *,
    day: str | int,
    level: str,
    repo_root: str | Path | None = None,
    prompt: str = "",
    note: str = "",
) -> dict[str, Any]:
    path = hint_state_path(day, repo_root)
    payload = {
        "day": normalize_day(day),
        "level": level,
        "prompt": prompt,
        "note": note,
        "recorded_at": _utc_now_iso(),
        "diagnostic_independence_eligible": False,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return {"hint_state_path": str(path), "payload": payload}


def load_hint_usage(day: str | int, repo_root: str | Path | None = None) -> dict[str, Any]:
    path = hint_state_path(day, repo_root)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
